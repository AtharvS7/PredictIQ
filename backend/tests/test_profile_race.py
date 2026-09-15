import asyncio
import os
from unittest.mock import AsyncMock
from uuid import uuid4

import asyncpg
import pytest
from app.api.v1 import profile
from app.core.security import CurrentUser


@pytest.mark.asyncio
async def test_concurrent_profile_creation_preserves_single_row(monkeypatch):
    dsn = os.environ.get('PREDICTIQ_TEST_DATABASE_URL')
    if not dsn:
        pytest.skip('Requires isolated migrated PostgreSQL test database')
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    user = CurrentUser(id='profile-race-' + uuid4().hex)
    monkeypatch.setattr(profile, 'get_db', AsyncMock(return_value=pool))
    try:
        results = await asyncio.gather(*[
            profile.create_or_update_profile(profile.ProfileUpdate(full_name='Concurrent user'), user)
            for _ in range(12)
        ])
        assert all(result['id'] == user.id for result in results)
        assert await pool.fetchval('SELECT count(*) FROM profiles WHERE id=$1', user.id) == 1
        assert await pool.fetchval('SELECT role FROM profiles WHERE id=$1', user.id) == 'editor'
    finally:
        await pool.execute('DELETE FROM profiles WHERE id=$1', user.id)
        await pool.close()
