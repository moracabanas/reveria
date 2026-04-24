"""Darts model serving layer with TimesFM2p5Model.

This module provides model loading infrastructure using the darts library's
foundation model API. TimesFM2p5Model from Google is CPU-friendly and provides
zero-shot forecasting without requiring training.

The darts library provides a unified API for multiple foundation models
(TimesFM, Chronos, with Reverso later), making it easy to swap models.
"""

import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Try to import darts components
try:
    from darts.models import TimesFM2p5Model
    from darts import TimeSeries

    DARTS_AVAILABLE = True
except ImportError as import_error:
    DARTS_AVAILABLE = False
    darts_import_error = import_error
    TimesFM2p5Model = None
    TimeSeries = None
    logger.warning(
        f"Darts not available: {import_error}. "
        "Install with: pip install darts[torch]"
    )


class DartsModel:
    """TimesFM2p5Model wrapper using darts unified API.

    This class provides a simplified interface to Google's TimesFM 2.5 model
    through the darts library. It handles model loading and prediction.

    Attributes:
        input_chunk_length: Number of time steps in the past for model input
        output_chunk_length: Number of time steps predicted at once
        model: The underlying darts TimesFM2p5Model instance (or None if not loaded)
    """

    def __init__(
        self,
        input_chunk_length: int = 64,
        output_chunk_length: int = 32,
    ):
        """Initialize the DartsModel with TimesFM2p5Model.

        Args:
            input_chunk_length: Number of past time steps as model input.
                Must be <= 16384 (TimesFM context limit).
            output_chunk_length: Number of future time steps predicted at once.
                Must be <= 128 (TimesFM output patch size).
        """
        self.input_chunk_length = input_chunk_length
        self.output_chunk_length = output_chunk_length
        self.model = None
        self._training_series = None

        logger.info(
            f"DartsModel initialized: input_chunk={input_chunk_length}, "
            f"output_chunk={output_chunk_length}"
        )

    def load(self) -> None:
        """Load the TimesFM2p5Model from darts.

        For foundation models like TimesFM, the model checkpoint is automatically
        downloaded from HuggingFace on first use. This method initializes the
        model but doesn't require explicit loading since darts handles it lazily.

        Raises:
            RuntimeError: If model loading fails
        """
        if not DARTS_AVAILABLE:
            logger.warning(
                "Darts not available - cannot load TimesFM2p5Model. "
                f"Error: {darts_import_error}"
            )
            self.model = None
            return

        try:
            logger.info("Loading TimesFM2p5Model via darts...")
            self.model = TimesFM2p5Model(
                input_chunk_length=self.input_chunk_length,
                output_chunk_length=self.output_chunk_length,
            )
            logger.info("TimesFM2p5Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TimesFM2p5Model: {e}")
            self.model = None
            raise RuntimeError(f"Failed to load TimesFM2p5Model: {e}") from e

    def fit(self, input_series: np.ndarray) -> None:
        """Fit the model on the input time series.

        TimesFM is a foundation model that performs zero-shot forecasting,
        but darts requires calling fit() to prepare the model for prediction.

        Args:
            input_series: numpy array or pandas Series of time series values

        Raises:
            RuntimeError: If fitting fails
        """
        if not DARTS_AVAILABLE:
            raise RuntimeError("Darts not available - cannot fit model")

        if self.model is None:
            self.load()

        try:
            # Convert to darts TimeSeries
            if isinstance(input_series, np.ndarray):
                series = TimeSeries.from_values(input_series)
            elif isinstance(input_series, pd.Series):
                series = TimeSeries.from_series(input_series)
            else:
                series = input_series  # Assume already a TimeSeries

            logger.info(f"Fitting TimesFM2p5Model on series of length {len(input_series)}")
            self.model.fit(series)
            self._training_series = series
            logger.info("Model fit completed")
        except Exception as e:
            logger.error(f"Failed to fit model: {e}")
            raise RuntimeError(f"Failed to fit model: {e}") from e

    def predict(self, n: int) -> np.ndarray:
        """Generate predictions for n future time steps.

        Args:
            n: Number of future time steps to predict

        Returns:
            numpy array of predicted values

        Raises:
            RuntimeError: If prediction fails
        """
        if self.model is None:
            raise RuntimeError("Model not loaded - call load() or fit() first")

        try:
            logger.info(f"Generating {n} predictions...")
            prediction = self.model.predict(n=n)
            # Extract numpy values from prediction
            pred_values = prediction.values().flatten()
            logger.info(f"Prediction completed: shape={pred_values.shape}")
            return pred_values
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e


async def load_model(
    input_chunk_length: int = 64,
    output_chunk_length: int = 32,
) -> DartsModel:
    """Load the TimesFM2p5Model during FastAPI startup.

    This async function is called during the application lifespan
    to load the model before handling requests.

    Args:
        input_chunk_length: Number of past time steps as model input
        output_chunk_length: Number of future time steps predicted at once

    Returns:
        Loaded DartsModel instance
    """
    logger.info(
        f"Loading TimesFM2p5Model (input_chunk={input_chunk_length}, "
        f"output_chunk={output_chunk_length})..."
    )

    model = DartsModel(
        input_chunk_length=input_chunk_length,
        output_chunk_length=output_chunk_length,
    )
    model.load()

    return model
