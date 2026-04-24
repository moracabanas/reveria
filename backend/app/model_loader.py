"""Reverso model loading with GPU/CPU detection.

This module provides model loading infrastructure for the Reverso Signal Dashboard.
It detects GPU availability and falls back to CPU if CUDA is not available.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import torch - may not be available on all platforms
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

# Hugging Face model ID for Reverso
REVERSO_MODEL_ID = "shinfxh/reverso"
CHECKPOINT_DIR = "checkpoints/reverso_small"


class ReversoModel:
    """Reverso model wrapper with device detection.

    This class handles model loading and device selection (GPU/CPU).
    Uses Moirai/uni2ts pattern as reference since Reverso returns 404.

    Attributes:
        device: The device the model is loaded on ("cuda" or "cpu")
        model_size: Size variant of the model ("nano", "small", "base")
        model: The underlying model instance (or None if not loaded)
    """

    def __init__(
        self,
        model_size: str = "small",
        device: Optional[str] = None,
    ):
        """Initialize the Reverso model.

        Args:
            model_size: Size variant - "nano" (200K), "small" (550K), or "base" (2.6M)
            device: Target device ("cuda", "cpu", or None for auto-detect)
        """
        self.model_size = model_size
        self.device = self._detect_device(device)
        self.model = None

        logger.info(f"ReversoModel initialized: size={model_size}, device={self.device}")

    def _detect_device(self, device: Optional[str]) -> str:
        """Detect and select the appropriate device.

        Args:
            device: Requested device or None for auto-detect

        Returns:
            Selected device string ("cuda" or "cpu")
        """
        if device is not None:
            return device

        if not TORCH_AVAILABLE:
            logger.warning("PyTorch not available - using CPU only")
            return "cpu"

        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            logger.info(f"CUDA available - using GPU: {device_name}")
            return "cuda"

        logger.warning("CUDA unavailable - using CPU")
        return "cpu"

    def load(self) -> None:
        """Load the model onto the selected device.

        This method loads the Reverso model from Hugging Face checkpoint.
        Downloads checkpoint files if not cached, then loads using Reverso's load_model.

        Raises:
            RuntimeError: If model loading fails completely
        """
        if not TORCH_AVAILABLE:
            logger.warning(
                "PyTorch not available - model loading skipped. "
                "Install torch for actual model support: pip install torch"
            )
            self.model = None
            return

        try:
            logger.info(f"Loading Reverso-{self.model_size} on {self.device}")

            # Attempt to import Reverso and huggingface_hub
            try:
                from huggingface_hub import snapshot_download
                from reverso import load_model
                REVERSO_AVAILABLE = True
            except ImportError as import_error:
                REVERSO_AVAILABLE = False
                reverso_import_error = import_error
                logger.warning(
                    f"Reverso package not available: {import_error}. "
                    "Install with: pip install -e git+https://github.com/SalesforceAIResearch/Reverso.git"
                )

            if not REVERSO_AVAILABLE:
                # Fall back to stub - Reverso dependencies not installed
                logger.warning(
                    "Reverso not installed - using stub model. "
                    "For actual model loading: pip install -e git+https://github.com/SalesforceAIResearch/Reverso.git"
                )
                self.model = {"loaded": True, "device": self.device, "stub": True}
                return

            # Download checkpoint from Hugging Face if not cached
            logger.info(f"Downloading Reverso checkpoint from Hugging Face: {REVERSO_MODEL_ID}")
            try:
                repo_path = snapshot_download(
                    repo_id=REVERSO_MODEL_ID,
                    allow_patterns=[f"{CHECKPOINT_DIR}/**"],
                )
                checkpoint_dir = Path(repo_path) / CHECKPOINT_DIR
                checkpoint_path = checkpoint_dir / "checkpoint.pth"
                args_path = checkpoint_dir / "args.json"

                if not checkpoint_path.exists():
                    raise FileNotFoundError(
                        f"Checkpoint not found at {checkpoint_path}. "
                        f"Available files in {checkpoint_dir}: {list(checkpoint_dir.iterdir()) if checkpoint_dir.exists() else 'directory does not exist'}"
                    )
                if not args_path.exists():
                    raise FileNotFoundError(f"Args file not found at {args_path}")

                logger.info(f"Checkpoint downloaded to {checkpoint_path}")
            except Exception as download_error:
                logger.warning(
                    f"Failed to download checkpoint: {download_error}. "
                    "Using stub model. Check network connectivity and HuggingFace authentication."
                )
                self.model = {"loaded": True, "device": self.device, "stub": True}
                return

            # Load the actual Reverso model
            try:
                logger.info(f"Loading Reverso model from {checkpoint_path} on {self.device}")
                self.model = load_model(
                    checkpoint_path=str(checkpoint_path),
                    args_path=str(args_path),
                    device=self.device,
                )
                logger.info(f"Reverso-{self.model_size} model loaded successfully on {self.device}")
            except Exception as model_error:
                error_msg = str(model_error)
                if "cuda" in error_msg.lower() or "gpu" in error_msg.lower() or "out of memory" in error_msg.lower():
                    logger.warning(f"GPU loading failed: {error_msg}. Falling back to CPU.")
                    self.device = "cpu"
                    try:
                        self.model = load_model(
                            checkpoint_path=str(checkpoint_path),
                            args_path=str(args_path),
                            device="cpu",
                        )
                        logger.info("Model loaded successfully on CPU")
                    except Exception as cpu_error:
                        raise RuntimeError(
                            f"Failed to load Reverso model on CPU: {cpu_error}"
                        ) from cpu_error
                else:
                    raise RuntimeError(
                        f"Failed to load Reverso model: {error_msg}"
                    ) from model_error

        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(
                f"Unexpected error loading Reverso model: {e}"
            ) from e


async def load_model(model_size: str = "small") -> ReversoModel:
    """Load the Reverso model during FastAPI startup.

    This async function is called during the application lifespan
    to load the model before handling requests.

    Args:
        model_size: Size variant of the model to load

    Returns:
        Loaded ReversoModel instance
    """
    logger.info(f"Loading Reverso model (size={model_size})...")

    model = ReversoModel(model_size=model_size)
    model.load()

    return model
