"""
Predictify — Health Endpoint Tests
Tests for GET /api/v1/health to verify model status reporting.
"""
from fastapi.testclient import TestClient
from main import app

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
    """Response must include version matching 2.0.0."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "2.0.0"


def test_health_schema():
    """Response shape must contain all expected keys."""
    response = client.get("/api/v1/health")
    data = response.json()
    expected_keys = {"status", "model_loaded", "version"}
    assert expected_keys.issubset(set(data.keys()))


def test_health_model_loaded_is_boolean():
    """model_loaded must be a boolean (True if pkl found, False if demo mode)."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert isinstance(data["model_loaded"], bool)
