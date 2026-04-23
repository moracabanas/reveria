"""Pytest configuration and fixtures for backend tests."""

from typing import Any

import numpy as np
import pytest


@pytest.fixture
def mock_torch_cuda_available(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture that patches torch.cuda.is_available to return True."""
    import sys

    # Create a mock torch module with cuda support
    class MockCUDA:
        @staticmethod
        def is_available() -> bool:
            return True

        @staticmethod
        def get_device_name(device: int = 0) -> str:
            return "Mock GPU"

    mock_torch = type("MockTorch", (), {
        "cuda": MockCUDA,
        "cuda_is_available": True,
    })()

    # Store original module if exists
    original_torch = sys.modules.get("torch")
    sys.modules["torch"] = mock_torch  # type: ignore

    # Also patch the model_loader module's reference
    monkeypatch.setattr("app.model_loader.torch", mock_torch)
    monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)

    yield

    # Cleanup
    if original_torch is not None:
        sys.modules["torch"] = original_torch
    else:
        sys.modules.pop("torch", None)


@pytest.fixture
def mock_torch_cuda_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture that patches torch.cuda.is_available to return False."""
    import sys

    # Create a mock torch module without cuda support
    class MockCUDA:
        @staticmethod
        def is_available() -> bool:
            return False

    mock_torch = type("MockTorch", (), {
        "cuda": MockCUDA,
        "cuda_is_available": False,
    })()

    # Store original module if exists
    original_torch = sys.modules.get("torch")
    sys.modules["torch"] = mock_torch  # type: ignore

    # Also patch the model_loader module's reference
    monkeypatch.setattr("app.model_loader.torch", mock_torch)
    monkeypatch.setattr("app.model_loader.TORCH_AVAILABLE", True)

    yield

    # Cleanup
    if original_torch is not None:
        sys.modules["torch"] = original_torch
    else:
        sys.modules.pop("torch", None)


@pytest.fixture
def sample_signal() -> np.ndarray:
    """Fixture returning a numpy array of 1000 random floats for testing.

    Returns:
        np.ndarray: Array of 1000 random floats in range [0, 1]
    """
    np.random.seed(42)  # Reproducible tests
    return np.random.rand(1000).astype(np.float32)


@pytest.fixture
def sample_signal_large() -> np.ndarray:
    """Fixture returning a numpy array of 50000 random floats for testing.

    Returns:
        np.ndarray: Array of 50000 random floats in range [0, 1]
    """
    np.random.seed(42)
    return np.random.rand(50000).astype(np.float32)
