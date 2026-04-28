"""Tests for prediction_service module.

This test suite covers:
- Normalization and denormalization
- PredictionConfig validation
- PredictionService integration with mocked model
- End-to-end normalization roundtrip
"""

from unittest.mock import MagicMock

import numpy as np
import pytest

from app.prediction_service import (
    Normalization,
    PredictionConfig,
    PredictionResult,
    PredictionService,
    run_prediction,
)


class TestNormalization:
    """Tests for normalize/denormalize functions."""

    def test_normalize_scales_to_01(self):
        """normalize scales data to [0, 1] range."""
        data = np.array([0.0, 50.0, 100.0])
        normalized, params = Normalization.normalize(data)
        assert np.min(normalized) == 0.0
        assert np.max(normalized) == 1.0

    def test_normalize_all_positive(self):
        """normalize handles all-positive data correctly."""
        data = np.array([10.0, 20.0, 30.0, 40.0])
        normalized, params = Normalization.normalize(data)
        assert np.min(normalized) == 0.0
        assert np.max(normalized) == 1.0

    def test_normalize_mixed_positive_negative(self):
        """normalize handles mixed positive/negative data correctly."""
        data = np.array([-50.0, 0.0, 50.0])
        normalized, params = Normalization.normalize(data)
        assert np.min(normalized) == 0.0
        assert np.max(normalized) == 1.0
        assert params["min"] == -50.0
        assert params["max"] == 50.0

    def test_normalize_identical_values(self):
        """normalize handles identical values (edge case: division by zero)."""
        data = np.array([42.0, 42.0, 42.0])
        normalized, params = Normalization.normalize(data)
        assert params["range"] == 1.0
        assert np.min(normalized) == np.max(normalized)

    def test_denormalize_reverses_normalize(self):
        """denormalize reverses normalization exactly."""
        original = np.array([0.0, 25.0, 50.0, 75.0, 100.0])
        normalized, params = Normalization.normalize(original)
        denormalized = Normalization.denormalize(normalized, params)
        np.testing.assert_array_almost_equal(denormalized, original)


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
            return {"forecast": np.linspace(0.5, 0.8, n), "prediction_length": n}

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
        """run_prediction uses only last context_size points."""
        service = PredictionService(mock_model)
        data = np.linspace(0, 100, 1000)
        config = PredictionConfig(context_size=100, prediction_length=96)

        await service.run_prediction(data, config)

        mock_model.fit.assert_called_once()
        call_arg = mock_model.fit.call_args[0][0]
        assert len(call_arg) == 100

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


class TestEndToEndNormalization:
    """Tests for end-to-end normalization roundtrip."""

    @pytest.mark.asyncio
    async def test_normalize_denormalize_roundtrip(self):
        """normalize -> denormalize preserves values within tolerance."""
        original = np.array([10.0, 25.0, 50.0, 75.0, 100.0])
        normalized, params = Normalization.normalize(original)
        denormalized = Normalization.denormalize(normalized, params)
        np.testing.assert_array_almost_equal(denormalized, original, decimal=10)

    @pytest.mark.asyncio
    async def test_forecast_in_original_scale(self):
        """Predicted values are in original data scale (not [0,1])."""
        mock_model = MagicMock()
        mock_model.fit = MagicMock()
        mock_model.predict = MagicMock(return_value={"forecast": np.array([0.6, 0.7, 0.8]), "prediction_length": 3})

        service = PredictionService(mock_model)
        data = np.array([0.0, 25.0, 50.0, 75.0, 100.0])
        config = PredictionConfig(context_size=32, prediction_length=3)

        result = await service.run_prediction(data, config)

        assert result.forecast.min() >= 0.0
        assert result.forecast.max() <= 100.0
