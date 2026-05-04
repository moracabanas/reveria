"""Prediction service for time series forecasting.

Handles model inference with configurable parameters.
TimesFM2p5Model handles scaling internally — no manual normalization needed.
"""

import logging
import time
from dataclasses import dataclass

import numpy as np

from app.model_loader import ForecastingModel

logger = logging.getLogger(__name__)


@dataclass
class PredictionConfig:
    """User-configurable prediction parameters."""

    context_size: int = 512
    prediction_length: int = 96
    frequency: str = "auto"

    def __post_init__(self):
        if self.context_size < 32:
            raise ValueError("context_size must be at least 32")
        if self.prediction_length < 1:
            raise ValueError("prediction_length must be at least 1")


@dataclass
class PredictionResult:
    """Result of a prediction run."""

    forecast: np.ndarray
    metadata: dict


class PredictionService:
    """Orchestrates prediction: slice -> fit -> predict -> return."""

    def __init__(self, model: ForecastingModel):
        self.model = model

    async def run_prediction(
        self, data: np.ndarray, config: PredictionConfig
    ) -> PredictionResult:
        start_time = time.perf_counter()

        if self.model is None:
            raise RuntimeError("Model not loaded - cannot run prediction")

        # Ensure context is large enough for the model to extract training samples.
        # darts requires series length >= input_chunk_length + output_chunk_length.
        input_chunk = getattr(self.model, "input_chunk_length", 512)
        output_chunk = getattr(self.model, "output_chunk_length", 128)
        if callable(input_chunk):
            input_chunk = 512
        if callable(output_chunk):
            output_chunk = 128
        min_context = input_chunk + output_chunk
        if config.context_size < min_context:
            logger.warning(
                f"context_size ({config.context_size}) < model input_chunk_length ({min_context}). "
                f"Using {min_context} to ensure model sees enough context."
            )
            config.context_size = min_context

        context_size = min(config.context_size, len(data))
        sliced_data = data[-context_size:]

        self.model.fit(sliced_data)

        pred_result = self.model.predict(n=config.prediction_length)
        forecast = pred_result["forecast"]

        elapsed = time.perf_counter() - start_time

        metadata = {
            "computation_time_ms": int(elapsed * 1000),
            "model_used": "TimesFM2p5",
            "input_points": len(sliced_data),
            "prediction_length": config.prediction_length,
            "context_size": config.context_size,
            "frequency": config.frequency,
        }

        return PredictionResult(forecast=forecast, metadata=metadata)


async def run_prediction(
    data: np.ndarray, config: PredictionConfig, model: ForecastingModel
) -> PredictionResult:
    service = PredictionService(model)
    return await service.run_prediction(data, config)
