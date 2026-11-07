"""
Unit and integration tests for Health & Ready endpoints (R01).
Tests:
- /api/v1/health and /api/v1/ready return 200 when v2 bundle is verified and ready.
- capabilities.automatic_prediction is True when ready.
- /api/v1/ready returns 503 when the model bundle is tampered or unavailable.
- capabilities.automatic_prediction is False when model bundle is unavailable.
- /api/v1/live returns 200 regardless of external dependencies.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def test_client_with_mocks():
    """Create a TestClient with mocked DB pool and Firebase."""
    with patch("main.init_firebase"), \
         patch("main.init_db_pool", new_callable=AsyncMock), \
         patch("main.close_db_pool", new_callable=AsyncMock), \
         patch("app.api.v1.health.get_db") as mock_get_db, \
         patch("firebase_admin.get_app", return_value=True):

        mock_pool = AsyncMock()
        mock_pool.fetchval.return_value = 1
        mock_pool.execute.return_value = None
        mock_get_db.return_value = mock_pool

        from main import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def test_health_and_ready_200_when_bundle_ready(test_client_with_mocks):
    """When the production v2 bundle is loaded and valid, /health and /ready return 200."""
    client = test_client_with_mocks

    # Test /health
    resp_health = client.get("/api/v1/health")
    assert resp_health.status_code == 200
    data_health = resp_health.json()
    assert data_health["status"] == "healthy"
    assert data_health["capabilities"]["automatic_prediction"] is True
    assert data_health["services"]["ml_model"] == "ready"
    assert data_health["model_loaded"] is True
    assert data_health["model_version"] == "2.0.0-rc.1"

    # Test /ready
    resp_ready = client.get("/api/v1/ready")
    assert resp_ready.status_code == 200
    data_ready = resp_ready.json()
    assert data_ready["status"] == "healthy"
    assert data_ready["capabilities"]["automatic_prediction"] is True


def test_ready_503_when_bundle_tampered_or_unavailable(test_client_with_mocks):
    """When ML bundle verification fails or is tampered, /ready and /health return 503."""
    client = test_client_with_mocks

    # Mock ml_service to simulate unready / tampered bundle
    with patch("app.api.v1.health.ml_service.is_ready", return_value=False), \
         patch("app.api.v1.health.ml_service.get_model_info", return_value={
             "model_loaded": False,
             "model_mode": "unavailable",
             "error": "Tampered manifest checksum",
         }):

        resp_ready = client.get("/api/v1/ready")
        assert resp_ready.status_code == 503
        data_ready = resp_ready.json()
        assert data_ready["status"] == "degraded"
        assert data_ready["capabilities"]["automatic_prediction"] is False
        assert data_ready["services"]["ml_model"] == "not_loaded"

        resp_health = client.get("/api/v1/health")
        assert resp_health.status_code == 503
        data_health = resp_health.json()
        assert data_health["status"] == "degraded"
        assert data_health["capabilities"]["automatic_prediction"] is False


def test_live_always_200(test_client_with_mocks):
    """Liveness probe /live returns 200 independent of ML bundle readiness."""
    client = test_client_with_mocks
    with patch("app.api.v1.health.ml_service.is_ready", return_value=False):
        resp = client.get("/api/v1/live")
        assert resp.status_code == 200
        assert resp.json() == {"status": "alive"}
