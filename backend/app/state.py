"""Shared application state for FastAPI app."""

from typing import Optional

from app.model_loader import ForecastingModel

_model: Optional[ForecastingModel] = None


def set_model(model: Optional[ForecastingModel]) -> None:
    global _model
    _model = model


def get_model() -> Optional[ForecastingModel]:
    return _model
