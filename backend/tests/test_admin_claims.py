import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from app.api.v1 import admin
from app.services import role_sync


async def test_role_update_preserves_claims_and_runs_outside_event_loop(monkeypatch):
    event_thread = threading.get_ident()
    original = {"role": "viewer", "billing_access": True, "tenant": "test-tenant"}

    def get_user(uid):
        assert uid == "target"
        assert threading.get_ident() != event_thread
        return SimpleNamespace(custom_claims=original)

    setter = Mock()
    monkeypatch.setattr(role_sync.auth, "get_user", get_user)
    monkeypatch.setattr(role_sync.auth, "set_custom_user_claims", setter)
    from starlette.concurrency import run_in_threadpool
    await run_in_threadpool(role_sync.sync_claims, 'target', 'editor')
    setter.assert_called_once_with("target", {"role": "editor", "billing_access": True, "tenant": "test-tenant"})
    assert original["role"] == "viewer"


async def test_delivery_failure_keeps_durable_authority_and_pending_state(monkeypatch):
    from app.core.security import CurrentUser
    pool = AsyncMock()
    pool.fetchrow.return_value = {"id": "target", "role": "viewer"}
    monkeypatch.setattr(admin, "get_db", AsyncMock(return_value=pool))
    monkeypatch.setattr(admin, 'sync_pending', AsyncMock(return_value=False))
    result = await admin.update_user_role("target", admin.RoleUpdateRequest(role="editor"), CurrentUser(id="admin", role="admin"))
    assert result['sync_pending'] is True
    assert 'role_managed=TRUE' in pool.fetchrow.call_args.args[0]
    pool.execute.assert_not_awaited()
