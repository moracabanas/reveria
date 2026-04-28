"""FastAPI application entry point for Reverso Signal Dashboard."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.model_loader import load_model
from app.routers import predict
from app.state import get_model, set_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Reverso Signal Dashboard API (NeuralForecast)...")
    try:
        model = await load_model()
        set_model(model)
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        set_model(None)

    yield

    logger.info("Shutting down Reverso Signal Dashboard API...")
    set_model(None)


settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)

app.include_router(predict.router, prefix="/predict", tags=["predictions"])


@app.get("/health")
async def health_check() -> JSONResponse:
    model = get_model()
    model_loaded = model is not None and model.model is not None
    return JSONResponse(
        content={
            "status": "healthy",
            "model_loaded": model_loaded,
        }
    )


@app.get("/")
async def root() -> dict:
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }
