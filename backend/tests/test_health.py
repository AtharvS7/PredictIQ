"""
Predictify — Health Endpoint Tests
Tests for GET /api/v1/health to verify model status, DB, and service reporting.
"""
from fastapi.testclient import TestClient
from main import app
from app.core.config import settings

client = TestClient(app)


def test_health_returns_200():
    """Health endpoint should return HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_has_model_status():
    """Response must include model_loaded boolean."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert "model_loaded" in data


def test_health_has_version():
    """Response version must match APP_VERSION from config."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == settings.APP_VERSION


def test_health_schema():
    """Response shape must contain all expected keys."""
    response = client.get("/api/v1/health")
    data = response.json()
    expected_keys = {"status", "model_loaded", "version", "services"}
    assert expected_keys.issubset(set(data.keys()))


def test_health_model_loaded_is_boolean():
    """model_loaded must be a boolean (True if pkl found, False if demo mode)."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data["model_loaded"], bool)


def test_health_services_present():
    """Services dict must include database, ml_model, and firebase status."""
    response = client.get("/api/v1/health")
    data = response.json()
    services = data.get("services", {})
    assert "database" in services
    assert "ml_model" in services
    assert "firebase" in services


def test_health_uptime():
    """Health must report uptime_seconds as a non-negative integer."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)
    assert data["uptime_seconds"] >= 0
