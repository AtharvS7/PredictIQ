import os
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import asyncpg
import pytest
from app.api.v1 import admin
from app.core import security
from app.services import role_sync
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials


@pytest.mark.asyncio
async def test_demotion_survives_provider_failure_and_stale_token(monkeypatch):
    dsn = os.environ.get('PREDICTIQ_TEST_DATABASE_URL')
    if not dsn:
        pytest.skip('Requires isolated migrated test database')
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
    target = 'role-test-' + uuid4().hex
    for module in (admin, security, role_sync):
        monkeypatch.setattr(module, 'get_db', AsyncMock(return_value=pool))
    monkeypatch.setattr(security.firebase_auth, 'verify_id_token', Mock(return_value={'uid': target, 'role': 'admin'}))
    provider = Mock(side_effect=RuntimeError('provider unavailable'))
    monkeypatch.setattr(role_sync, 'sync_claims', provider)
    try:
        await pool.execute("INSERT INTO profiles (id, role) VALUES ($1, 'admin')", target)
        response = await admin.update_user_role(target, admin.RoleUpdateRequest(role='viewer'), security.CurrentUser(id='another-admin', role='admin'))
        assert response['sync_pending'] is True
        assert await pool.fetchval('SELECT role_sync_pending FROM profiles WHERE id=$1', target)
        user = await security.get_current_user(Request({'type': 'http'}), HTTPAuthorizationCredentials(scheme='Bearer', credentials='stale-test-token'))
        assert user.role == 'viewer'
        with pytest.raises(HTTPException) as denied:
            await security.require_role('admin')(user)
        assert denied.value.status_code == 403
        provider.side_effect = None
        assert await role_sync.sync_pending(target)
        assert not await pool.fetchval('SELECT role_sync_pending FROM profiles WHERE id=$1', target)
        provider.assert_called_with(target, 'viewer')
    finally:
        await pool.execute('DELETE FROM profiles WHERE id=$1', target)
        await pool.close()


@pytest.mark.asyncio
async def test_failed_sync_is_delayed_without_blocking_other_accounts(monkeypatch):
    dsn = os.environ.get('PREDICTIQ_TEST_DATABASE_URL')
    if not dsn:
        pytest.skip('Requires isolated migrated test database')
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
    failed, healthy = ['retry-test-' + uuid4().hex for _ in range(2)]
    monkeypatch.setattr(role_sync, 'get_db', AsyncMock(return_value=pool))

    def provider(user_id, role):
        if user_id == failed:
            raise RuntimeError('provider unavailable')

    monkeypatch.setattr(role_sync, 'sync_claims', provider)
    try:
        await pool.execute("INSERT INTO profiles (id, role, role_sync_pending, role_sync_after) VALUES ($1, 'viewer', TRUE, NOW() - INTERVAL '1 hour'), ($2, 'editor', TRUE, NOW())", failed, healthy)
        assert await role_sync.sync_pending(failed) is False
        assert await pool.fetchval('SELECT role_sync_after > NOW() FROM profiles WHERE id=$1', failed)
        assert await role_sync.sync_pending() is True
        assert not await pool.fetchval('SELECT role_sync_pending FROM profiles WHERE id=$1', healthy)
        assert await pool.fetchval('SELECT role_sync_pending FROM profiles WHERE id=$1', failed)
    finally:
        await pool.execute('DELETE FROM profiles WHERE id=ANY($1::text[])', [failed, healthy])
        await pool.close()
