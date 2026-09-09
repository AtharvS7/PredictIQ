import threading
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from app.api.v1 import admin
from app.core.security import CurrentUser
from fastapi import HTTPException


async def test_role_update_preserves_claims_and_runs_outside_event_loop(monkeypatch):
    event_thread = threading.get_ident()
    original = {"role": "viewer", "billing_access": True, "tenant": "test-tenant"}
    pool = AsyncMock()
    pool.fetchrow.return_value = {"id": "target", "role": "viewer"}
    monkeypatch.setattr(admin, "get_db", AsyncMock(return_value=pool))

    def get_user(uid):
        assert uid == "target"
        assert threading.get_ident() != event_thread
        return SimpleNamespace(custom_claims=original)

    setter = Mock()
    monkeypatch.setattr(admin.firebase_auth, "get_user", get_user)
    monkeypatch.setattr(admin.firebase_auth, "set_custom_user_claims", setter)
    response = await admin.update_user_role("target", admin.RoleUpdateRequest(role="editor"), CurrentUser(id="admin", role="admin"))
    setter.assert_called_once_with("target", {"role": "editor", "billing_access": True, "tenant": "test-tenant"})
    assert original["role"] == "viewer"
    assert response["synced_to_firebase"] is True


async def test_failed_claim_read_does_not_erase_claims_and_restores_database_role(monkeypatch):
    pool = AsyncMock()
    pool.fetchrow.return_value = {"id": "target", "role": "viewer"}
    monkeypatch.setattr(admin, "get_db", AsyncMock(return_value=pool))
    monkeypatch.setattr(admin.firebase_auth, "get_user", Mock(side_effect=RuntimeError("provider detail")))
    setter = Mock()
    monkeypatch.setattr(admin.firebase_auth, "set_custom_user_claims", setter)
    with pytest.raises(HTTPException) as error:
        await admin.update_user_role("target", admin.RoleUpdateRequest(role="editor"), CurrentUser(id="admin", role="admin"))
    assert error.value.status_code == 500
    assert "provider detail" not in error.value.detail
    setter.assert_not_called()
    assert pool.execute.call_args.args[1:] == ("viewer", "target")
