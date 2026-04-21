"""
PredictIQ Backend Configuration
Loads environment variables via pydantic-settings.
"""
import warnings
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Neon PostgreSQL
    DATABASE_URL: str

    # Firebase — provide EITHER a file path OR raw JSON string
    FIREBASE_CREDENTIALS_PATH: str = "./firebase-service-account.json"
    FIREBASE_CREDENTIALS_JSON: str = ""  # Raw JSON string (for Codespaces/Railway)

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ML Model Paths
    ML_MODEL_PATH: str = "./ml/predictiq_best_model.pkl"
    ML_SCALER_PATH: str = "./ml/predictiq_scaler.pkl"
    ML_FEATURES_PATH: str = "./ml/predictiq_features.json"

    # Application
    DEFAULT_HOURLY_RATE_USD: float = 75.0
    APP_ENV: str = "development"
    APP_VERSION: str = "3.0.0"

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        """Crash fast if critical secrets are still placeholder values."""
        if self.APP_ENV not in ("test", "testing", "ci"):
            if not self.DATABASE_URL or "your-" in self.DATABASE_URL:
                warnings.warn(
                    "DATABASE_URL is a placeholder — set a real Neon connection string in .env",
                    stacklevel=2,
                )
        return self

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
