"""Readiness reflects dependencies; liveness reflects the running process."""
import asyncio
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
    monkeypatch.setattr(health.settings, 'RELEASE_MODE', 'prediction')
    monkeypatch.setattr(health, 'get_db', AsyncMock(return_value=Mock(fetchval=AsyncMock(return_value=1), execute=AsyncMock())))
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
    assert data['capabilities']['manual_budget'] is True


def test_manual_release_reports_model_unavailable_truthfully(monkeypatch):
    monkeypatch.setattr(health.settings, 'RELEASE_MODE', 'manual_budget')
    monkeypatch.setattr(health.predictor, 'is_ready', False)
    result = client.get('/api/v1/ready')
    assert result.status_code == 200
    assert result.json()['capabilities'] == {'manual_budget': True, 'automatic_prediction': False}
    assert result.json()['services']['ml_model'] == 'not_loaded'
    assert result.json()['model_loaded'] is False


@pytest.mark.parametrize('mode', ['prediction', 'manual_budget'])
def test_every_release_requires_budget_schema(monkeypatch, mode):
    monkeypatch.setattr(health.settings, 'RELEASE_MODE', mode)
    pool = Mock(fetchval=AsyncMock(return_value=1), execute=AsyncMock(side_effect=[None, RuntimeError('missing budgets')]))
    monkeypatch.setattr(health, 'get_db', AsyncMock(return_value=pool))
    result = client.get('/api/v1/ready')
    assert result.status_code == 503
    assert result.json()['capabilities']['manual_budget'] is False


def test_missing_authorization_schema_fails_readiness(monkeypatch):
    pool = Mock(fetchval=AsyncMock(return_value=1), execute=AsyncMock(side_effect=RuntimeError('missing column')))
    monkeypatch.setattr(health, 'get_db', AsyncMock(return_value=pool))
    assert client.get('/api/v1/ready').status_code == 503
    assert client.get('/api/v1/live').status_code == 200

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


@pytest.mark.asyncio
@pytest.mark.parametrize('stage', ['pool', 'query', 'schema'])
async def test_saturated_database_times_out_without_blocking_liveness(monkeypatch, stage):
    from fastapi import Response

    cancelled = asyncio.Event()

    async def stalled(*args):
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    pool = Mock(fetchval=AsyncMock(return_value=1), execute=AsyncMock())
    monkeypatch.setattr(health, 'get_db', stalled if stage == 'pool' else AsyncMock(return_value=pool))
    if stage == 'query':
        pool.fetchval = stalled
    elif stage == 'schema':
        pool.execute = stalled
    monkeypatch.setattr(health, 'READINESS_TIMEOUT_SECONDS', 0.01)
    response = Response()
    result = await asyncio.wait_for(health.health_check(response), timeout=1)
    assert response.status_code == 503
    assert result['services']['database'] == 'error: TimeoutError'
    assert cancelled.is_set()
    assert await health.liveness() == {'status': 'alive'}


@pytest.mark.asyncio
async def test_concurrent_outage_probes_all_finish_and_leave_liveness_available(monkeypatch):
    from fastapi import Response

    async def stalled():
        await asyncio.Event().wait()

    monkeypatch.setattr(health, 'get_db', stalled)
    monkeypatch.setattr(health, 'READINESS_TIMEOUT_SECONDS', 0.02)
    responses = [Response() for _ in range(40)]
    probes = [health.health_check(response) for response in responses]
    results = await asyncio.wait_for(asyncio.gather(*probes, health.liveness()), timeout=2)
    assert all(response.status_code == 503 for response in responses)
    assert results[-1] == {'status': 'alive'}
