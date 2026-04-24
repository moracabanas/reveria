"""Time series forecasting using StatsForecast models.

This module provides model loading infrastructure using StatsForecast -
a collection of fast statistical models for time series forecasting.

Models available (CPU-friendly, no torch required):
- AutoARIMA: Automatic ARIMA selection
- AutoETS: Automatic Exponential Smoothing
- AutoCES: Automatic Complex Exponential Smoothing
- AutoTheta: Automatic Theta method
- SeasonalNaive: Seasonal naive baseline
- DynamicOptimizedTheta: Optimized Theta method

For neural models (require ml optional-deps):
- mlforecast: ML-based forecasting (LightGBM, XGBoost, etc.)
- neuralforecast: Neural network models (NBEATS, NHITS, etc.)
"""

import logging
from typing import Optional, Union

import numpy as np

logger = logging.getLogger(__name__)

STATSFORECAST_AVAILABLE = False
try:
    from statsforecast import StatsForecast
    from statsforecast.models import (
        AutoARIMA,
        AutoETS,
        AutoCES,
        AutoTheta,
        SeasonalNaive,
        DynamicOptimizedTheta,
    )
    STATSFORECAST_AVAILABLE = True
    logger.info("StatsForecast available")
except ImportError as e:
    StatsForecast = None
    statsforecast_import_error = e
    logger.warning(
        f"StatsForecast not available: {e}. "
        "Install with: pip install statsforecast"
    )


class ForecastingModel:
    """Wrapper for StatsForecast models providing unified forecasting API.

    Supports multiple statistical models with automatic parameter selection.
    All models run on CPU without requiring GPU or torch.

    Attributes:
        model_type: Type of forecasting model to use
        model: The underlying statsforecast model instance
        fitted_model: The fitted model after calling fit()
    """

    def __init__(
        self,
        model_type: str = "autoarima",
        season_length: int = 1,
    ):
        """Initialize the forecasting model.

        Args:
            model_type: Type of model to use.
                Options: "autoarima", "autoets", "autoces", "autotheta",
                "seasonalnaive", "dynamicoptimizedtheta"
            season_length: Number of observations per season (1 = no seasonality)
        """
        self.model_type = model_type.lower()
        self.season_length = season_length
        self.model = None
        self.fitted_model = None
        self._sf_model = None

        if not STATSFORECAST_AVAILABLE:
            logger.warning("StatsForecast not available - model will be stub")
            return

        try:
            self._sf_model = self._create_model()
            logger.info(f"ForecastingModel initialized: type={model_type}, season={season_length}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self._sf_model = None

    def _create_model(self):
        """Create the underlying statsforecast model."""
        if self.model_type == "autoarima":
            return AutoARIMA(season_length=self.season_length)
        elif self.model_type == "autoets":
            return AutoETS(season_length=self.season_length)
        elif self.model_type == "autoces":
            return AutoCES(season_length=self.season_length)
        elif self.model_type == "autotheta":
            return AutoTheta(season_length=self.season_length)
        elif self.model_type == "seasonalnaive":
            return SeasonalNaive(season_length=self.season_length)
        elif self.model_type == "dynamicoptimizedtheta":
            return DynamicOptimizedTheta(season_length=self.season_length)
        else:
            logger.warning(f"Unknown model type '{self.model_type}', defaulting to AutoARIMA")
            return AutoARIMA(season_length=self.season_length)

    def load(self) -> None:
        """Mark model as loaded (StatsForecast is lazy, no explicit load needed)."""
        if not STATSFORECAST_AVAILABLE:
            logger.warning("StatsForecast not available")
            self.model = None
            return
        self.model = self._sf_model
        logger.info(f"Model loaded: {self.model_type}")

    def fit(self, input_series: np.ndarray) -> None:
        """Fit the model on the input time series.

        Args:
            input_series: numpy array of time series values

        Raises:
            RuntimeError: If fitting fails
        """
        if not STATSFORECAST_AVAILABLE:
            raise RuntimeError("StatsForecast not available - cannot fit model")

        if self._sf_model is None:
            raise RuntimeError("Model not initialized")

        try:
            import pandas as pd

            logger.info(f"Fitting {self.model_type} on series of length {len(input_series)}")

            n = len(input_series)
            df = pd.DataFrame({
                "ds": pd.date_range(start="2020-01-01", periods=n, freq="h"),
                "y": input_series,
                "unique_id": "series1"
            })

            sf = StatsForecast(
                models=[self._sf_model],
                freq="h",
                n_jobs=-1,
            )
            sf.fit(df)

            self.fitted_model = sf
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
            RuntimeError: If prediction fails or model not fitted
        """
        if self.fitted_model is None:
            raise RuntimeError("Model not fitted - call fit() first")

        try:
            logger.info(f"Generating {n} predictions...")
            pred_df = self.fitted_model.predict(h=n)

            pred_values = pred_df["fitted"].values if "fitted" in pred_df.columns else pred_df.iloc[:, 0].values

            logger.info(f"Prediction completed: shape={pred_values.shape}")
            return pred_values

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e


async def load_model(
    model_type: str = "autoarima",
    season_length: int = 1,
) -> ForecastingModel:
    """Load the forecasting model during FastAPI startup.

    Args:
        model_type: Type of forecasting model to use
        season_length: Seasonality length

    Returns:
        Loaded ForecastingModel instance
    """
    logger.info(f"Loading forecasting model (type={model_type})...")

    model = ForecastingModel(model_type=model_type, season_length=season_length)
    model.load()

    return model
