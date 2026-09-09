"""Readiness reflects dependencies; liveness reflects the running process."""
from unittest.mock import AsyncMock, Mock

import firebase_admin
import pytest
from app.api.v1 import health
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()
app.include_router(health.router, prefix='/api/v1')
client = TestClient(app)

@pytest.fixture(autouse=True)
def healthy_dependencies(monkeypatch):
    monkeypatch.setattr(health, 'get_db', AsyncMock(return_value=Mock(fetchval=AsyncMock(return_value=1))))
    monkeypatch.setattr(health.predictor, 'is_ready', True)
    monkeypatch.setattr(firebase_admin, 'get_app', lambda: object())

@pytest.mark.parametrize('path', ['/health', '/ready'])
def test_ready_status_and_schema(path):
    response = client.get('/api/v1' + path)
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert data['model_loaded'] is True
    assert data['version'] == health.settings.APP_VERSION
    assert set(data['services']) == {'database', 'ml_model', 'firebase'}
    assert isinstance(data['uptime_seconds'], int)
    assert data['uptime_seconds'] >= 0

@pytest.mark.parametrize('dependency', ['database', 'model', 'firebase'])
@pytest.mark.parametrize('path', ['/health', '/ready'])
def test_missing_dependency_fails_readiness(monkeypatch, dependency, path):
    if dependency == 'database':
        monkeypatch.setattr(health, 'get_db', AsyncMock(side_effect=RuntimeError('offline')))
    elif dependency == 'model':
        monkeypatch.setattr(health.predictor, 'is_ready', False)
    else:
        monkeypatch.setattr(firebase_admin, 'get_app', Mock(side_effect=ValueError('uninitialized')))
    response = client.get('/api/v1' + path)
    assert response.status_code == 503
    assert response.json()['status'] == 'degraded'
    assert client.get('/api/v1/live').status_code == 200
