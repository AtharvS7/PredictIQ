"""CPU-heavy export and password work must leave the request event loop free."""
import threading
from unittest.mock import AsyncMock
from uuid import uuid4

from app.api.v1 import export
from app.core.security import CurrentUser
from app.services import estimate_service


async def test_pdf_generation_runs_outside_event_loop(monkeypatch):
    event_thread = threading.get_ident()
    pool = AsyncMock()
    pool.fetchrow.return_value = {"project_name": "Project", "inputs_json": {}, "outputs_json": {}}
    monkeypatch.setattr(export, "get_db", AsyncMock(return_value=pool))

    def render(*args, **kwargs):
        assert threading.get_ident() != event_thread
        return b"%PDF-test"

    monkeypatch.setattr(export, "generate_pdf_report", render)
    response = await export.export_pdf(uuid4(), "USD", CurrentUser(id="owner"))
    assert response.media_type == "application/pdf"
    body = b"".join([part async for part in response.body_iterator])
    assert body == b"%PDF-test"


async def test_share_password_hash_runs_outside_event_loop(monkeypatch):
    event_thread = threading.get_ident()
    pool = AsyncMock()
    pool.fetchrow.return_value = {"id": uuid4()}
    monkeypatch.setattr(estimate_service, "get_db", AsyncMock(return_value=pool))

    def hash_password(password, salt):
        assert threading.get_ident() != event_thread
        assert password == b"test-password"
        return b"test-hash"

    monkeypatch.setattr(estimate_service.bcrypt, "hashpw", hash_password)
    result = await estimate_service.estimate_service.create_share_link(str(uuid4()), "owner", 1, "test-password")
    assert result is not None
    assert pool.execute.call_args.args[3] == "test-hash"
