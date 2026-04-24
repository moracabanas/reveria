"""Unit tests for DartsModel and model loading functionality.

Tests for the darts-based model serving layer using TimesFM2p5Model.
"""

from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from app.model_loader import DartsModel, DARTS_AVAILABLE, load_model


# Skip all tests if darts is not available
pytestmark = pytest.mark.skipif(
    not DARTS_AVAILABLE,
    reason="Darts not available - install darts[torch] for TimesFM support"
)


class TestDartsModelInitialization:
    """Tests for DartsModel initialization."""

    def test_model_creation_with_default_parameters(self) -> None:
        """Test that DartsModel can be created with default parameters."""
        model = DartsModel()
        assert model.input_chunk_length == 64
        assert model.output_chunk_length == 32
        assert model.model is None

    def test_model_creation_with_custom_parameters(self) -> None:
        """Test that DartsModel accepts custom chunk parameters."""
        model = DartsModel(
            input_chunk_length=128,
            output_chunk_length=64
        )
        assert model.input_chunk_length == 128
        assert model.output_chunk_length == 64

    def test_model_creation_does_not_load_immediately(self) -> None:
        """Test that model is not loaded until load() is called."""
        model = DartsModel()
        assert model.model is None


class TestDartsModelLoad:
    """Tests for DartsModel.load() method."""

    def test_load_initializes_model(self) -> None:
        """Test that load() properly initializes the TimesFM2p5Model."""
        model = DartsModel()
        model.load()
        assert model.model is not None

    def test_load_is_idempotent(self) -> None:
        """Test that calling load() multiple times doesn't cause issues."""
        model = DartsModel()
        model.load()
        model.load()  # Should not raise
        assert model.model is not None


class TestDartsModelFit:
    """Tests for DartsModel.fit() method."""

    def test_fit_with_numpy_array(self) -> None:
        """Test that fit() works with numpy array input."""
        model = DartsModel()
        model.load()

        sample_data = np.random.randn(100).cumsum()
        model.fit(sample_data)

        assert model._training_series is not None

    def test_fit_with_pandas_series(self) -> None:
        """Test that fit() works with pandas Series input."""
        model = DartsModel()
        model.load()

        sample_data = pd.Series(np.random.randn(100).cumsum())
        model.fit(sample_data)

        assert model._training_series is not None

    def test_fit_with_unavailable_darts_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that fit() raises if darts is not available."""
        # Simulate darts not available
        monkeypatch.setattr("app.model_loader.DARTS_AVAILABLE", False)

        model = DartsModel()
        sample_data = np.random.randn(100)

        with pytest.raises(RuntimeError, match="Darts not available"):
            model.fit(sample_data)


class TestDartsModelPredict:
    """Tests for DartsModel.predict() method."""

    def test_predict_returns_numpy_array(self) -> None:
        """Test that predict() returns a numpy array."""
        model = DartsModel()
        model.load()

        sample_data = np.random.randn(100).cumsum()
        model.fit(sample_data)

        prediction = model.predict(n=10)

        assert isinstance(prediction, np.ndarray)

    def test_predict_returns_correct_length(self) -> None:
        """Test that predict() returns array of requested length."""
        model = DartsModel()
        model.load()

        sample_data = np.random.randn(100).cumsum()
        model.fit(sample_data)

        prediction = model.predict(n=10)

        assert len(prediction) == 10

    def test_predict_with_different_lengths(self) -> None:
        """Test prediction with varying output lengths."""
        model = DartsModel()
        model.load()

        sample_data = np.random.randn(200).cumsum()
        model.fit(sample_data)

        for n in [5, 10, 20, 50]:
            prediction = model.predict(n=n)
            assert len(prediction) == n

    def test_predict_requires_fit_first(self) -> None:
        """Test that predict() raises if model not fitted."""
        model = DartsModel()
        model.load()

        with pytest.raises(RuntimeError, match="Prediction failed"):
            model.predict(n=10)

    def test_predict_requires_model_loaded(self) -> None:
        """Test that predict() raises if model not loaded."""
        model = DartsModel()
        # Don't call load()

        with pytest.raises(RuntimeError, match="not loaded"):
            model.predict(n=10)


class TestDartsModelInputValidation:
    """Tests for input validation in DartsModel."""

    def test_handles_minimum_length_input(self) -> None:
        """Test that model handles minimum length input series.

        Note: TimesFM2p5Model requires input series length >= 96 for
        input_chunk_length=64 due to internal padding/offsets.
        """
        model = DartsModel()
        model.load()

        # Minimum length series (must be >= 96 for input_chunk_length=64)
        min_data = np.random.randn(100)
        model.fit(min_data)
        prediction = model.predict(n=5)

        assert len(prediction) == 5

    def test_handles_long_input(self) -> None:
        """Test that model handles long input series."""
        model = DartsModel()
        model.load()

        # Long series (50K+ points as per project requirements)
        long_data = np.random.randn(50000).cumsum()
        model.fit(long_data)
        prediction = model.predict(n=100)

        assert len(prediction) == 100


@pytest.mark.asyncio
class TestLoadModelFunction:
    """Tests for the async load_model() function."""

    async def test_load_model_returns_darts_model_instance(self) -> None:
        """Test that load_model returns a DartsModel instance."""
        model = await load_model()

        assert isinstance(model, DartsModel)
        assert model.model is not None

    async def test_load_model_default_parameters(self) -> None:
        """Test that load_model uses default chunk parameters."""
        model = await load_model()

        assert model.input_chunk_length == 64
        assert model.output_chunk_length == 32

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
