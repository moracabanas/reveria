"""Configuration management for Reverso Signal Dashboard."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelConfig(BaseSettings):
    """Model configuration settings."""

    context_size: int = 512
    prediction_length: int = 100
    model_size: str = "small"


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_prefix="REVERSO_")

    # API settings
    api_title: str = "Reverso Signal Dashboard API"
    api_version: str = "0.1.0"
    api_description: str = "Time series forecasting API using Reverso foundation model"

    # Model settings
    context_size: int = 512
    prediction_length: int = 100
    model_size: str = "small"

    @property
    def model_cfg(self) -> ModelConfig:
        """Get model configuration."""
        return ModelConfig(
            context_size=self.context_size,
            prediction_length=self.prediction_length,
            model_size=self.model_size,
        )


def get_settings() -> Settings:
    """Get application settings (singleton)."""
    return Settings()
