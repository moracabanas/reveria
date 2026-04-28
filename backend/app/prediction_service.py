"""Prediction service for time series forecasting.

Handles normalization, model inference, and output denormalization
with configurable parameters.
"""

import logging
import time
from dataclasses import dataclass
from typing import Optional, Tuple

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


class Normalization:
    """Handles min-max normalization and denormalization."""

    @staticmethod
    def normalize(data: np.ndarray) -> Tuple[np.ndarray, dict]:
        min_val = float(np.min(data))
        max_val = float(np.max(data))

        if max_val == min_val:
            range_val = 1.0
        else:
            range_val = max_val - min_val

        normalized = (data - min_val) / range_val

        params = {"min": min_val, "max": max_val, "range": range_val}
        return normalized, params

    @staticmethod
    def denormalize(normalized: np.ndarray, params: dict) -> np.ndarray:
        range_val = params["range"]
        min_val = params["min"]
        return normalized * range_val + min_val


class PredictionService:
    """Orchestrates prediction: normalize -> fit -> predict -> denormalize."""

    def __init__(self, model: ForecastingModel):
        self.model = model

    async def run_prediction(
        self, data: np.ndarray, config: PredictionConfig
    ) -> PredictionResult:
        start_time = time.perf_counter()

        if self.model is None:
            raise RuntimeError("Model not loaded - cannot run prediction")

        context_size = min(config.context_size, len(data))
        sliced_data = data[-context_size:]

        normalized, norm_params = Normalization.normalize(sliced_data)

        self.model.fit(normalized)

        pred_result = self.model.predict(n=config.prediction_length)
        forecast = pred_result["forecast"]

        denormalized = Normalization.denormalize(forecast, norm_params)

        elapsed = time.perf_counter() - start_time

        metadata = {
            "computation_time_ms": int(elapsed * 1000),
            "model_used": "TimesFM2p5",
            "input_points": len(sliced_data),
            "prediction_length": config.prediction_length,
            "context_size": config.context_size,
            "frequency": config.frequency,
        }

        return PredictionResult(forecast=denormalized, metadata=metadata)


async def run_prediction(
    data: np.ndarray, config: PredictionConfig, model: ForecastingModel
) -> PredictionResult:
    service = PredictionService(model)
    return await service.run_prediction(data, config)
