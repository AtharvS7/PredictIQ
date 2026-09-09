"""Full local API/storage/NLP/model/PostgreSQL flow on a migrated disposable DB."""
import os
from contextlib import asynccontextmanager
from uuid import uuid4

import asyncpg
import pytest
from app.api.v1 import documents, estimates, export, shared
from app.core import database
from app.core.rate_limit import limiter
from app.core.security import CurrentUser, get_current_user
from app.services.storage_service import LocalStorageBackend, storage_service
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ml.inference import predictor


@pytest.mark.integration
def test_real_document_to_persisted_result(tmp_path, monkeypatch, sample_document_text, contract_model_artifacts):
    dsn = os.getenv("PREDICTIQ_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("Set PREDICTIQ_TEST_DATABASE_URL to an isolated migrated test database")
    user = CurrentUser(id="flow-test-" + uuid4().hex, role="editor")
    original_user = user.id
    monkeypatch.setattr(storage_service, "_backend", LocalStorageBackend(str(tmp_path)))
    previous_pool = database._pool

    @asynccontextmanager
    async def lifespan(app):
        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=3)
        database._pool = pool
        assert predictor.load(*contract_model_artifacts)
        try:
            yield
        finally:
            # Delete only this test's rows in its explicitly configured DB.
            await pool.execute("DELETE FROM share_links WHERE estimate_id IN (SELECT id FROM estimates WHERE user_id=$1)", original_user)
            await pool.execute("DELETE FROM estimates WHERE user_id=$1", original_user)
            await pool.execute("DELETE FROM document_uploads WHERE user_id=$1", original_user)
            await pool.close()
            database._pool = previous_pool

    app = FastAPI(lifespan=lifespan)
    app.state.limiter = limiter
    limiter.reset()
    for router in (documents.router, estimates.router, export.router, shared.router):
        app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: user
    with TestClient(app) as client:
        uploaded = client.post("/documents/upload-file", files={"file": ("spec.txt", sample_document_text.encode(), "text/plain")})
        assert uploaded.status_code == 200, uploaded.text
        doc_id = uploaded.json()["id"]
        extracted = client.post(f"/documents/{doc_id}/extract")
        assert extracted.status_code == 200, extracted.text
        response = client.post("/estimates/analyze", json={"document_id": doc_id})
        assert response.status_code == 200, response.text
        result = response.json()
        assert result["inputs"]["team_size"] == extracted.json()["team_size"]
        assert result["inputs"]["duration_months"] == 12
        assert result["outputs"]["effort_likely_hours"] > 0
        assert result["inputs"]["feature_count"] == extracted.json()["feature_count"]
        assert result["inputs"]["integration_count"] == extracted.json()["integration_count"]
        assert result["inputs"]["size_fp"] > 0
        identifier = result["estimate_id"]
        saved = client.get(f"/estimates/{identifier}")
        assert saved.status_code == 200, saved.text
        assert saved.json()["outputs"] == result["outputs"]
        assert saved.json()["inputs"] == result["inputs"]
        assert saved.json()["model_version"] == result["model_version"]
        exported = client.get(f"/estimates/{identifier}/export/json")
        assert exported.status_code == 200, exported.text
        assert exported.json()["id"] == identifier
        duplicate = client.post(f"/estimates/{identifier}/duplicate")
        assert duplicate.status_code == 200, duplicate.text
        copied = client.get(f"/estimates/{duplicate.json()['id']}")
        assert copied.status_code == 200, copied.text
        assert copied.json()["inputs"] == result["inputs"]
        link = client.post(f"/estimates/{identifier}/share", json={"password": "test-password", "expires_in_days": 1})
        assert link.status_code == 200, link.text
        token = link.json()["token"]
        # Shared access works without Firebase authentication, but needs its own password.
        app.dependency_overrides.clear()
        assert client.get(f"/shared/{token}").status_code == 401
        assert client.post(f"/shared/{token}", json={"password": "wrong"}).status_code == 401
        public = client.post(f"/shared/{token}", json={"password": "test-password"})
        assert public.status_code == 200, public.text
        assert public.json()["inputs"] == result["inputs"]
        assert public.headers["cache-control"] == "no-store"
        assert set(public.json()) == {"project_name", "version", "created_at", "inputs", "outputs"}
        assert client.get("/shared/invalid-token").status_code == 404
        async def expire():
            await database._pool.execute("UPDATE share_links SET expires_at=NOW()-INTERVAL '1 second' WHERE token=$1", token)
        client.portal.call(expire)
        assert client.post(f"/shared/{token}", json={"password": "test-password"}).status_code == 404
        app.dependency_overrides[get_current_user] = lambda: user
        user.id = "another-test-user"
        assert client.post(f"/documents/{doc_id}/extract").status_code == 404
        assert client.get(f"/estimates/{identifier}").status_code == 404
        assert client.get(f"/estimates/{identifier}/export/json").status_code == 404
