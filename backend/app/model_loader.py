"""Chronos model serving layer for time series forecasting.

This module provides model loading infrastructure using the Chronos family of
pretrained time series forecasting models from Amazon. Chronos-2 provides
zero-shot forecasting without requiring training.

Models available:
- Chronos-2 (120M params) - latest, best performance
- Chronos-Bolt variants (9M-205M params) - faster, more efficient
- Chronos-T5 variants (8M-710M params) - original Chronos models
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

CHRONOS_AVAILABLE = False
Chronos2Pipeline = None
chronos_import_error = None

try:
    from chronos import Chronos2Pipeline
    CHRONOS_AVAILABLE = True
    logger.info("Chronos-2 pipeline available")
except ImportError as import_error:
    CHRONOS_AVAILABLE = False
    chronos_import_error = import_error
    logger.warning(
        f"Chronos not available: {import_error}. "
        "Install with: pip install chronos-forecasting"
    )


class ChronosModel:
    """Chronos-2 model wrapper for zero-shot time series forecasting.

    This class provides a simplified interface to Amazon's Chronos-2 model
    through the chronos-forecasting package.

    Attributes:
        model_id: The Chronos model variant to use
        device: Device to run inference on ("cpu", "cuda", or "auto")
        model: The underlying Chronos2Pipeline instance (or None if not loaded)
    """

    def __init__(
        self,
        model_id: str = "amazon/chronos-2",
        device: str = "cpu",
    ):
        """Initialize the ChronosModel.

        Args:
            model_id: Chronos model variant.
                Options: "amazon/chronos-2", "amazon/chronos-bolt-tiny/small/medium/base",
                "amazon/chronos-t5-tiny/mini/small/base/large"
            device: Device for inference ("cpu", "cuda", or "auto")
        """
        self.model_id = model_id
        self.device = device
        self.model = None

        logger.info(f"ChronosModel initialized: model_id={model_id}, device={device}")

    def load(self) -> None:
        """Load the Chronos model from HuggingFace.

        Downloads model checkpoints on first use.

        Raises:
            RuntimeError: If model loading fails
        """
        if not CHRONOS_AVAILABLE:
            logger.warning(
                f"Chronos not available - cannot load model. "
                f"Error: {chronos_import_error}"
            )
            self.model = None
            return

        try:
            logger.info(f"Loading Chronos model: {self.model_id}...")
            self.model = Chronos2Pipeline.from_pretrained(
                self.model_id,
                device_map=self.device,
            )
            logger.info(f"Chronos model {self.model_id} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Chronos model: {e}")
            self.model = None
            raise RuntimeError(f"Failed to load Chronos model: {e}") from e

    def predict(
        self,
        context: list[float],
        prediction_length: int = 96,
        quantile_levels: Optional[list[float]] = None,
    ) -> dict:
        """Generate predictions for the given context.

        Args:
            context: List of historical time series values
            prediction_length: Number of future steps to forecast
            quantile_levels: Quantile levels for probabilistic forecast

        Returns:
            Dictionary with:
                - forecast: numpy array of predicted values (median)
                - quantiles: dict of quantile -> array predictions (if quantile_levels provided)
                - prediction_length: number of predicted steps
        """
        if self.model is None:
            raise RuntimeError("Model not loaded - call load() first")

        if quantile_levels is None:
            quantile_levels = [0.1, 0.5, 0.9]

        try:
            import pandas as pd

            logger.info(f"Generating {prediction_length} predictions...")

            context_df = pd.DataFrame({
                "timestamp": pd.date_range(
                    periods=len(context),
                    freq="h"
                ),
                "value": context
            })

            pred_df = self.model.predict_df(
                context_df,
                prediction_length=prediction_length,
                quantile_levels=quantile_levels,
                id_column="timestamp",
                timestamp_column="timestamp",
                target="value",
            )

            forecast = pred_df["predictions"].values

            result = {
                "forecast": forecast,
                "prediction_length": prediction_length,
            }

            if quantile_levels:
                quantiles = {}
                for q in quantile_levels:
                    q_str = str(q)
                    if q_str in pred_df.columns:
                        quantiles[q] = pred_df[q_str].values
                result["quantiles"] = quantiles

            logger.info(f"Prediction completed: shape={forecast.shape}")
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e


def create_chronos_model(
    model_id: str = "amazon/chronos-2",
    device: str = "cpu",
) -> ChronosModel:
    """Factory function to create a ChronosModel instance.

    Args:
        model_id: Chronos model variant to use
        device: Device for inference

    Returns:
        Configured ChronosModel instance (not yet loaded)
    """
    return ChronosModel(model_id=model_id, device=device)


async def load_model(
    model_id: str = "amazon/chronos-2",
    device: str = "cpu",
) -> ChronosModel:
    """Load the Chronos model during FastAPI startup.

    Args:
        model_id: Chronos model variant to load
        device: Device for inference

    Returns:
        Loaded ChronosModel instance
    """
    logger.info(f"Loading Chronos model (id={model_id}, device={device})...")

    model = ChronosModel(model_id=model_id, device=device)
    model.load()

    return model
