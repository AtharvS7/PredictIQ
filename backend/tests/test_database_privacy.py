from unittest.mock import AsyncMock, Mock

import pytest
from app.core import database


@pytest.mark.asyncio
async def test_connection_errors_never_expose_provider_details(monkeypatch):
    secret = 'private-connection-value-never-log'
    logger = Mock()
    monkeypatch.setattr(database, '_pool', None)
    monkeypatch.setattr(database, '_MAX_RETRIES', 2)
    monkeypatch.setattr(database, 'logger', logger)
    monkeypatch.setattr(database.asyncpg, 'create_pool', AsyncMock(side_effect=OSError(secret)))
    monkeypatch.setattr(database.asyncio, 'sleep', AsyncMock())
    with pytest.raises(RuntimeError) as caught:
        await database.init_db_pool()
    assert secret not in str(caught.value)
    assert caught.value.__suppress_context__
    assert secret not in repr(logger.mock_calls)
    assert logger.warning.call_count == 2
    assert logger.error.call_args.kwargs['error_type'] == 'OSError'
