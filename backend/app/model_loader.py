"""NeuralForecast model serving layer for time series forecasting.

This module provides model loading infrastructure using NeuralForecast -
neural network models for time series forecasting (NBEATS, NHITS, etc.)

Models available (require torch):
- NBEATS: Neural Basis Expansion Analysis
- NHITS: Neural Hierarchical Interpolation for Time Series
- TFT: Temporal Fusion Transformer
- RNN, LSTM, GRU: Recurrent networks
- And more...
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

NEURALFORECAST_AVAILABLE = False
try:
    from neuralforecast import NeuralForecast
    from neuralforecast.models import NHITS, NBEATS
    NEURALFORECAST_AVAILABLE = True
    logger.info("NeuralForecast available")
except ImportError as e:
    NeuralForecast = None
    NHITS = None
    NBEATS = None
    neuralforecast_import_error = e
    logger.warning(
        f"NeuralForecast not available: {e}. "
        "Install with: pip install neuralforecast"
    )


class ForecastingModel:
    """NeuralForecast model wrapper.

    Provides zero-shot or quick-training forecasting using neural networks.

    Attributes:
        model_type: Type of neural model to use
        input_size: Lookback window size
        horizon: Forecast horizon (prediction length)
        model: The underlying neuralforecast model instance
        fitted_model: The fitted model after calling fit()
    """

    def __init__(
        self,
        model_type: str = "nhits",
        input_size: int = 64,
        horizon: int = 32,
    ):
        """Initialize the forecasting model.

        Args:
            model_type: Type of neural model to use.
                Options: "nhits", "nbeats"
            input_size: Number of past time steps as model input
            horizon: Number of future steps to forecast
        """
        self.model_type = model_type.lower()
        self.input_size = input_size
        self.horizon = horizon
        self.model = None
        self.fitted_model = None
        self._nf_model = None

        if not NEURALFORECAST_AVAILABLE:
            logger.warning("NeuralForecast not available - model will be stub")
            return

        try:
            self._nf_model = self._create_model()
            logger.info(f"ForecastingModel initialized: type={model_type}, input={input_size}, horizon={horizon}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            self._nf_model = None

    def _create_model(self):
        """Create the underlying neuralforecast model."""
        if self.model_type == "nhits":
            return NHITS(
                input_size=self.input_size,
                h=self.horizon,
                max_steps=100,
                enable_progress_bar=False,
            )
        elif self.model_type == "nbeats":
            return NBEATS(
                input_size=self.input_size,
                h=self.horizon,
                max_steps=100,
                enable_progress_bar=False,
            )
        else:
            logger.warning(f"Unknown model type '{self.model_type}', defaulting to NHITS")
            return NHITS(
                input_size=self.input_size,
                h=self.horizon,
                max_steps=100,
                enable_progress_bar=False,
            )

    def load(self) -> None:
        """Load and initialize the model."""
        if not NEURALFORECAST_AVAILABLE:
            logger.warning("NeuralForecast not available")
            self.model = None
            return
        self.model = self._nf_model
        logger.info(f"Model loaded: {self.model_type}")

    def fit(self, input_series, **kwargs) -> None:
        """Fit the model on the input time series.

        Args:
            input_series: pandas DataFrame with columns [unique_id, ds, y]
                or numpy array of values
            **kwargs: Additional arguments for fit()

        Raises:
            RuntimeError: If fitting fails
        """
        if not NEURALFORECAST_AVAILABLE:
            raise RuntimeError("NeuralForecast not available - cannot fit model")

        if self._nf_model is None:
            raise RuntimeError("Model not initialized")

        try:
            import pandas as pd

            if isinstance(input_series, dict):
                df = pd.DataFrame(input_series)
            elif hasattr(input_series, 'to_dict'):
                df = pd.DataFrame(input_series.to_dict())
            else:
                n = len(input_series)
                df = pd.DataFrame({
                    "ds": pd.date_range(start="2020-01-01", periods=n, freq="h"),
                    "y": input_series,
                    "unique_id": "series1"
                })

            logger.info(f"Fitting {self.model_type} on series of length {len(df)}")

            nf = NeuralForecast(
                models=[self._nf_model],
                freq="h",
            )
            nf.fit(df=df, **kwargs)

            self.fitted_model = nf
            logger.info("Model fit completed")

        except Exception as e:
            logger.error(f"Failed to fit model: {e}")
            raise RuntimeError(f"Failed to fit model: {e}") from e

    def predict(self, n: Optional[int] = None) -> dict:
        """Generate predictions.

        Args:
            n: Number of future steps (overrides horizon if provided)

        Returns:
            Dictionary with forecast array and metadata

        Raises:
            RuntimeError: If prediction fails or model not fitted
        """
        if self.fitted_model is None:
            raise RuntimeError("Model not fitted - call fit() first")

        horizon = n if n is not None else self.horizon

        try:
            logger.info(f"Generating {horizon} predictions...")
            pred_df = self.fitted_model.predict(h=horizon)

            pred_values = pred_df["NHITS"].values if "NHITS" in pred_df.columns else pred_df.iloc[:, 0].values

            result = {
                "forecast": pred_values,
                "horizon": horizon,
            }

            logger.info(f"Prediction completed: shape={pred_values.shape}")
            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}") from e


async def load_model(
    model_type: str = "nhits",
    input_size: int = 64,
    horizon: int = 32,
) -> ForecastingModel:
    """Load the forecasting model during FastAPI startup.

    Args:
        model_type: Type of neural model to use
        input_size: Lookback window size
        horizon: Forecast horizon

    Returns:
        Loaded ForecastingModel instance
    """
    logger.info(f"Loading NeuralForecast model (type={model_type})...")

    model = ForecastingModel(model_type=model_type, input_size=input_size, horizon=horizon)
    model.load()

    return model
