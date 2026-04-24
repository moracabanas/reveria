"""FastAPI application entry point for Reverso Signal Dashboard."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.model_loader import ForecastingModel, load_model

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
_model: Optional[ForecastingModel] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    global _model

    # Startup: load the model
    logger.info("Starting Reverso Signal Dashboard API (NeuralForecast)...")
    try:
        _model = await load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model = None

    yield

    # Shutdown: cleanup
    logger.info("Shutting down Reverso Signal Dashboard API...")
    _model = None


settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint.

    Returns:
        JSON response with health status and model loaded indicator.
    """
    model_loaded = _model is not None and _model.model is not None

    return JSONResponse(
        content={
            "status": "healthy",
            "model_loaded": model_loaded,
        }
    )


@app.get("/")
async def root() -> dict:
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }
