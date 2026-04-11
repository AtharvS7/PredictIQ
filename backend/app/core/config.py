"""
PredictIQ Backend Configuration
Loads environment variables via pydantic-settings.
"""
from pydantic_settings import BaseSettings
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
    APP_VERSION: str = "2.0.0"

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
