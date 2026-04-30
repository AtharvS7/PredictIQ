"""
Predictify — Configuration Tests
Tests for Settings class, defaults, CORS parsing, and validation.
"""
import pytest
from app.core.config import Settings, settings


class TestSettingsDefaults:
    """Test that default configuration values are correct."""

    def test_app_version_format(self):
        """APP_VERSION should be a semver-like string."""
        assert isinstance(settings.APP_VERSION, str)
        parts = settings.APP_VERSION.split(".")
        assert len(parts) >= 2  # At least major.minor

    def test_default_hourly_rate(self):
        """Default hourly rate should be 75.0."""
        assert settings.DEFAULT_HOURLY_RATE_USD == 75.0

    def test_app_env_set(self):
        """APP_ENV should be a non-empty string."""
        assert isinstance(settings.APP_ENV, str)
        assert len(settings.APP_ENV) > 0

    def test_database_url_set(self):
        """DATABASE_URL should be configured."""
        assert isinstance(settings.DATABASE_URL, str)
        assert len(settings.DATABASE_URL) > 0

    def test_ml_model_paths_set(self):
        """ML model paths should have default values."""
        assert "pkl" in settings.ML_MODEL_PATH or "model" in settings.ML_MODEL_PATH.lower()
        assert "pkl" in settings.ML_SCALER_PATH or "scaler" in settings.ML_SCALER_PATH.lower()
        assert "json" in settings.ML_FEATURES_PATH or "features" in settings.ML_FEATURES_PATH.lower()


class TestCorsOrigins:
    """Test CORS origin parsing."""

    def test_cors_origins_returns_list(self):
        """cors_origins property should return a list."""
        origins = settings.cors_origins
        assert isinstance(origins, list)

    def test_cors_origins_not_empty(self):
        """There should be at least one CORS origin."""
        origins = settings.cors_origins
        assert len(origins) >= 1

    def test_cors_origins_are_strings(self):
        """Each origin should be a string."""
        for origin in settings.cors_origins:
            assert isinstance(origin, str)

    def test_cors_origins_no_trailing_spaces(self):
        """Origins should be trimmed (no trailing/leading spaces)."""
        for origin in settings.cors_origins:
            assert origin == origin.strip()

    def test_cors_origins_are_urls(self):
        """Origins should look like URLs (start with http)."""
        for origin in settings.cors_origins:
            assert origin.startswith("http"), f"Origin '{origin}' doesn't start with http"


class TestSettingsFirebase:
    """Test Firebase credential configuration."""

    def test_firebase_path_has_default(self):
        """FIREBASE_CREDENTIALS_PATH should have a default."""
        assert isinstance(settings.FIREBASE_CREDENTIALS_PATH, str)
        assert len(settings.FIREBASE_CREDENTIALS_PATH) > 0

    def test_firebase_json_is_string(self):
        """FIREBASE_CREDENTIALS_JSON should be a string (possibly empty)."""
        assert isinstance(settings.FIREBASE_CREDENTIALS_JSON, str)


class TestSettingsImmutable:
    """Verify settings instance is consistent."""

    def test_settings_singleton(self):
        """Importing settings twice should give same values."""
        from app.core.config import settings as s2
        assert s2.APP_VERSION == settings.APP_VERSION
        assert s2.APP_ENV == settings.APP_ENV
