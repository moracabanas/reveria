"""Tests for prediction_service module.

This test suite covers:
- PredictionConfig validation
- PredictionService integration with mocked model
- End-to-end prediction flow
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

from app.prediction_service import (
    PredictionConfig,
    PredictionResult,
    PredictionService,
    run_prediction,
)


class TestPredictionConfig:
    """Tests for PredictionConfig validation."""

    def test_default_values(self):
        """PredictionConfig has correct defaults."""
        config = PredictionConfig()
        assert config.context_size == 512
        assert config.prediction_length == 96
        assert config.frequency == "auto"

    def test_custom_values(self):
        """PredictionConfig accepts custom values."""
        config = PredictionConfig(context_size=256, prediction_length=48, frequency="D")
        assert config.context_size == 256
        assert config.prediction_length == 48
        assert config.frequency == "D"

    def test_invalid_context_size_too_small(self):
        """PredictionConfig rejects context_size < 32."""
        with pytest.raises(ValueError, match="context_size must be at least 32"):
            PredictionConfig(context_size=10)

    def test_invalid_prediction_length_zero(self):
        """PredictionConfig rejects prediction_length < 1."""
        with pytest.raises(ValueError, match="prediction_length must be at least 1"):
            PredictionConfig(prediction_length=0)


class TestPredictionService:
    """Tests for PredictionService with mocked model."""

    @pytest.fixture
    def mock_model(self):
        """Create a mock ForecastingModel that returns predictable forecasts."""
        model = MagicMock()

        def mock_predict(n):
            return {"forecast": np.linspace(1400, 1600, n), "prediction_length": n}

        model.predict = mock_predict
        model.fit = MagicMock()
        return model

    @pytest.mark.asyncio
    async def test_run_prediction_returns_forecast(self, mock_model):
        """run_prediction returns forecast array of correct length."""
        service = PredictionService(mock_model)
        data = np.linspace(0, 100, 500)
        config = PredictionConfig(context_size=500, prediction_length=96)

        result = await service.run_prediction(data, config)

        assert isinstance(result, PredictionResult)
        assert len(result.forecast) == 96

    @pytest.mark.asyncio
    async def test_run_prediction_metadata_fields(self, mock_model):
        """run_prediction returns metadata with all required fields."""
        service = PredictionService(mock_model)
        data = np.linspace(0, 100, 500)
        config = PredictionConfig(context_size=500, prediction_length=96)

        result = await service.run_prediction(data, config)

        assert "computation_time_ms" in result.metadata
        assert "model_used" in result.metadata
        assert "input_points" in result.metadata
        assert "prediction_length" in result.metadata
        assert result.metadata["model_used"] == "TimesFM2p5"

    @pytest.mark.asyncio
    async def test_run_prediction_uses_context_size(self, mock_model):
        """run_prediction uses at least model input_chunk_length points."""
        service = PredictionService(mock_model)
        data = np.linspace(0, 100, 1000)
        config = PredictionConfig(context_size=100, prediction_length=96)

        await service.run_prediction(data, config)

        mock_model.fit.assert_called_once()
        call_arg = mock_model.fit.call_args[0][0]
        # Context is auto-adjusted to model's input_chunk_length (512)
        assert len(call_arg) == 512

    @pytest.mark.asyncio
    async def test_run_prediction_short_input(self, mock_model):
        """run_prediction handles input shorter than context_size."""
        service = PredictionService(mock_model)
        data = np.linspace(0, 100, 50)
        config = PredictionConfig(context_size=500, prediction_length=96)

        result = await service.run_prediction(data, config)

        assert len(result.forecast) == 96
        assert result.metadata["input_points"] == 50

    @pytest.mark.asyncio
    async def test_run_prediction_model_not_loaded(self):
        """run_prediction raises RuntimeError when model is None."""
        service = PredictionService(None)
        data = np.linspace(0, 100, 500)
        config = PredictionConfig()

        with pytest.raises(RuntimeError, match="Model not loaded"):
            await service.run_prediction(data, config)

    @pytest.mark.asyncio
    async def test_run_prediction_passes_raw_data(self, mock_model):
        """run_prediction passes raw sliced data to model without normalization."""
        service = PredictionService(mock_model)
        data = np.array([1000.0, 1500.0, 2000.0])
        config = PredictionConfig(context_size=32, prediction_length=3)

        await service.run_prediction(data, config)

        call_arg = mock_model.fit.call_args[0][0]
        np.testing.assert_array_equal(call_arg, data)

    @pytest.mark.asyncio
    async def test_forecast_in_realistic_scale(self, mock_model):
        """Predicted values are in realistic scale matching input data range."""
        service = PredictionService(mock_model)
        data = np.array([1000.0, 1500.0, 2000.0])
        config = PredictionConfig(context_size=32, prediction_length=3)

        result = await service.run_prediction(data, config)

        assert result.forecast.min() >= 1000.0
        assert result.forecast.max() <= 2000.0
