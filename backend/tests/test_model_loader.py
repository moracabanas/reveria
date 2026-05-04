"""Unit tests for ForecastingModel and model loading functionality.

Tests for the darts-based model serving layer using TimesFM2p5Model.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from app.model_loader import ForecastingModel, DARTS_AVAILABLE, load_model


# Skip all tests if darts is not available
pytestmark = pytest.mark.skipif(
    not DARTS_AVAILABLE,
    reason="Darts not available - install darts[torch] for TimesFM support"
)


class TestForecastingModelInitialization:
    """Tests for ForecastingModel initialization."""

    def test_model_creation_with_default_parameters(self) -> None:
        """Test that ForecastingModel can be created with default parameters."""
        model = ForecastingModel()
        assert model.input_chunk_length == 512
        assert model.output_chunk_length == 128
        assert model.model is None

    def test_model_creation_with_custom_parameters(self) -> None:
        """Test that ForecastingModel accepts custom chunk parameters."""
        model = ForecastingModel(
            input_chunk_length=128,
            output_chunk_length=64
        )
        assert model.input_chunk_length == 128
        assert model.output_chunk_length == 64

    def test_model_creation_does_not_load_immediately(self) -> None:
        """Test that model is not loaded until load() is called."""
        model = ForecastingModel()
        assert model.model is None


class TestForecastingModelLoad:
    """Tests for ForecastingModel.load() method."""

    def test_load_initializes_model(self) -> None:
        """Test that load() properly initializes the TimesFM2p5Model."""
        model = ForecastingModel()
        model.load()
        assert model.model is not None

    def test_load_is_idempotent(self) -> None:
        """Test that calling load() multiple times doesn't cause issues."""
        model = ForecastingModel()
        model.load()
        model.load()  # Should not raise
        assert model.model is not None


class TestForecastingModelFit:
    """Tests for ForecastingModel.fit() method."""

    def test_fit_with_numpy_array(self) -> None:
        """Test that fit() works with numpy array input."""
        model = ForecastingModel()
        model.load()

        sample_data = np.random.randn(1000).cumsum()
        model.fit(sample_data)

        assert model._training_series is not None

    def test_fit_with_pandas_series(self) -> None:
        """Test that fit() works with pandas Series input."""
        model = ForecastingModel()
        model.load()

        sample_data = pd.Series(np.random.randn(1000).cumsum())
        model.fit(sample_data)

        assert model._training_series is not None

    def test_fit_with_unavailable_darts_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that fit() raises if darts is not available."""
        # Simulate darts not available
        monkeypatch.setattr("app.model_loader.DARTS_AVAILABLE", False)

        model = ForecastingModel()
        sample_data = np.random.randn(1000)

        with pytest.raises(RuntimeError, match="Darts not available"):
            model.fit(sample_data)


class TestForecastingModelPredict:
    """Tests for ForecastingModel.predict() method."""

    def test_predict_returns_dict(self) -> None:
        """Test that predict() returns a dict with forecast array."""
        model = ForecastingModel()
        model.load()

        sample_data = np.random.randn(1000).cumsum()
        model.fit(sample_data)

        prediction = model.predict(n=10)

        assert isinstance(prediction, dict)
        assert "forecast" in prediction

    def test_predict_returns_correct_length(self) -> None:
        """Test that predict() returns array of requested length."""
        model = ForecastingModel()
        model.load()

        sample_data = np.random.randn(1000).cumsum()
        model.fit(sample_data)

        prediction = model.predict(n=10)

        assert len(prediction["forecast"]) == 10

    def test_predict_with_different_lengths(self) -> None:
        """Test prediction with varying output lengths."""
        model = ForecastingModel()
        model.load()

        sample_data = np.random.randn(1000).cumsum()
        model.fit(sample_data)

        for n in [5, 10, 20, 50]:
            prediction = model.predict(n=n)
            assert len(prediction["forecast"]) == n

    def test_predict_requires_fit_first(self) -> None:
        """Test that predict() raises if model not fitted."""
        model = ForecastingModel()
        model.load()

        with pytest.raises(RuntimeError, match="Prediction failed"):
            model.predict(n=10)

    def test_predict_requires_model_loaded(self) -> None:
        """Test that predict() raises if model not loaded."""
        model = ForecastingModel()
        # Don't call load()

        with pytest.raises(RuntimeError, match="not loaded"):
            model.predict(n=10)


class TestForecastingModelInputValidation:
    """Tests for input validation in ForecastingModel."""

    def test_handles_minimum_length_input(self) -> None:
        """Test that model handles minimum length input series.

        Note: TimesFM2p5Model requires input series length >= input_chunk_length + output_chunk_length
        for the default configuration of 512/128.
        """
        model = ForecastingModel()
        model.load()

        # Minimum length series (must be >= 640 for input_chunk_length=512, output_chunk_length=128)
        min_data = np.random.randn(1000)
        model.fit(min_data)
        prediction = model.predict(n=5)

        assert len(prediction["forecast"]) == 5

    def test_handles_long_input(self) -> None:
        """Test that model handles long input series."""
        model = ForecastingModel()
        model.load()

        # Long series (50K+ points as per project requirements)
        long_data = np.random.randn(50000).cumsum()
        model.fit(long_data)
        prediction = model.predict(n=100)

        assert len(prediction["forecast"]) == 100


@pytest.mark.asyncio
class TestLoadModelFunction:
    """Tests for the async load_model() function."""

    async def test_load_model_returns_forecasting_model_instance(self) -> None:
        """Test that load_model returns a ForecastingModel instance."""
        model = await load_model()

        assert isinstance(model, ForecastingModel)
        assert model.model is not None

    async def test_load_model_default_parameters(self) -> None:
        """Test that load_model uses default chunk parameters."""
        model = await load_model()

        assert model.input_chunk_length == 512
        assert model.output_chunk_length == 128

    async def test_load_model_custom_parameters(self) -> None:
        """Test that load_model respects custom parameters."""
        model = await load_model(
            input_chunk_length=128,
            output_chunk_length=64
        )

        assert model.input_chunk_length == 128
        assert model.output_chunk_length == 64


class TestDartsAvailability:
    """Tests for darts availability detection."""

    def test_darts_available_flag(self) -> None:
        """Test that DARTS_AVAILABLE correctly reflects darts availability."""
        # This test just verifies the flag is boolean
        assert isinstance(DARTS_AVAILABLE, bool)

    def test_timesfm_import_when_available(self) -> None:
        """Test that TimesFM2p5Model can be imported when darts available."""
        from darts.models import TimesFM2p5Model
        assert TimesFM2p5Model is not None
