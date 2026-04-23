"""Unit tests for ReversoModel and model loading functionality."""

from unittest.mock import MagicMock, patch

import pytest

from app.model_loader import ReversoModel, TORCH_AVAILABLE, load_model


class TestReversoModelInitialization:
    """Tests for ReversoModel initialization and device detection."""

    def test_model_defaults_to_cpu_when_torch_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ReversoModel uses CPU when torch is not available."""
        # Simulate torch not available
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)
        monkeypatch.setattr("app.model_loader.torch", None)

        model = ReversoModel()

        assert model.device == "cpu"
        assert model.model is None

    def test_model_uses_cpu_when_cuda_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ReversoModel uses CPU when CUDA is not available."""
        # Simulate torch available but CUDA unavailable
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False
        mock_torch.cuda.get_device_name.return_value = "Mock GPU"

        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)
        monkeypatch.setattr("app.model_loader.torch", mock_torch)

        model = ReversoModel()

        assert model.device == "cpu"
        assert model.model is None

    def test_model_uses_cuda_when_available(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that ReversoModel uses CUDA when GPU is available."""
        # Simulate torch available with CUDA
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True
        mock_torch.cuda.get_device_name.return_value = "NVIDIA Tesla T4"

        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)
        monkeypatch.setattr("app.model_loader.torch", mock_torch)

        model = ReversoModel()

        assert model.device == "cuda"
        assert model.model is None

    def test_model_respects_explicit_device_parameter(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that explicitly passed device parameter is respected."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = True

        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)
        monkeypatch.setattr("app.model_loader.torch", mock_torch)

        # Explicitly request CPU
        model = ReversoModel(device="cpu")

        assert model.device == "cpu"

    @pytest.mark.parametrize(
        "model_size,expected_size",
        [
            ("nano", "nano"),
            ("small", "small"),
            ("base", "base"),
        ],
    )
    def test_model_accepts_size_parameter(
        self,
        model_size: str,
        expected_size: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test ReversoModel accepts different size parameters."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)

        model = ReversoModel(model_size=model_size)

        assert model.model_size == expected_size


class TestReversoModelLoad:
    """Tests for ReversoModel.load() method."""

    def test_load_completes_without_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that load() completes without raising when torch unavailable."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)

        model = ReversoModel()
        # Should not raise - handles missing torch gracefully
        model.load()

        # Model remains None when torch unavailable (expected behavior)
        assert model.model is None
        assert model.device == "cpu"

    def test_load_handles_torch_unavailable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that load() handles missing torch gracefully."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)
        monkeypatch.setattr("app.model_loader.torch", None)

        model = ReversoModel()
        # Should not raise
        model.load()

        # Model remains None since torch unavailable
        assert model.model is None


@pytest.mark.asyncio
class TestLoadModelFunction:
    """Tests for the async load_model() function."""

    async def test_load_model_returns_reverso_model_instance(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that load_model returns a ReversoModel instance."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)

        model = await load_model()

        # Returns ReversoModel instance (model attribute depends on torch availability)
        assert isinstance(model, ReversoModel)
        assert model.model is None  # torch unavailable, so model not loaded
        assert model.device == "cpu"

    async def test_load_model_default_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that load_model uses 'small' as default size."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)

        model = await load_model()

        assert model.model_size == "small"

    async def test_load_model_custom_size(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that load_model respects custom size parameter."""
        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", False)

        model = await load_model(model_size="nano")

        assert model.model_size == "nano"


class TestDeviceDetection:
    """Tests for device detection logic in various scenarios."""

    def test_detect_device_cpu_when_forced(self) -> None:
        """Test that _detect_device returns forced CPU device."""
        model = ReversoModel(device="cpu")
        assert model.device == "cpu"

    def test_detect_device_cuda_when_forced(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that _detect_device returns forced CUDA device."""
        mock_torch = MagicMock()
        mock_torch.cuda.is_available.return_value = False

        monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)
        monkeypatch.setattr("app.model_loader.torch", mock_torch)

        model = ReversoModel(device="cuda")
        assert model.device == "cuda"
