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

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_STORAGE_BUCKET: str = "project-docs"

    # Auth
    JWT_SECRET: str = "your-jwt-secret"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ML Model Paths
    ML_MODEL_PATH: str = "./ml/predictiq_best_model.pkl"
    ML_SCALER_PATH: str = "./ml/predictiq_scaler.pkl"
    ML_FEATURES_PATH: str = "./ml/predictiq_features.json"

    # Application
    DEFAULT_HOURLY_RATE_USD: float = 75.0
    APP_ENV: str = "development"
    APP_VERSION: str = "2.5.0"

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        """Crash fast if critical secrets are still placeholder values."""
        UNSAFE = {
            "your-jwt-secret", "changeme", "secret", "test",
            "placeholder", "REPLACE_ME", "",
        }
        if self.APP_ENV not in ("test", "testing", "ci"):
            if self.JWT_SECRET in UNSAFE:
                warnings.warn(
                    "JWT_SECRET is a placeholder — set a real secret in .env",
                    stacklevel=2,
                )
            if not self.SUPABASE_URL.startswith("https://"):
                warnings.warn(
                    f"SUPABASE_URL does not look like a production URL: {self.SUPABASE_URL}",
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
