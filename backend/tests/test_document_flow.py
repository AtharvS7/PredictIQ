"""Regression coverage across real local storage, parsing, NLP and API contracts."""
import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from app.api.v1 import documents, estimates
from app.core.security import CurrentUser, get_current_user
from app.services.storage_service import LocalStorageBackend, storage_service
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def flow(tmp_path, monkeypatch):
    store = LocalStorageBackend(str(tmp_path / "uploads"))
    monkeypatch.setattr(storage_service, "_backend", store)
    rows = {}

    async def fetchrow(query, *args):
        if "INSERT INTO estimates" in query:
            return {"id": uuid4(), "created_at": datetime.now(timezone.utc), "version": 1}
        if "INSERT INTO document_uploads" in query:
            row = dict(id=uuid4(), user_id=args[0], storage_path=args[1],
                       original_filename=args[2], file_size_bytes=args[3], mime_type=args[4],
                       status="uploaded", parsed_text_preview=None, created_at=datetime.now(timezone.utc))
            rows[str(row["id"])] = row
            return row
        row = rows.get(str(args[0]))
        return row if row and row["user_id"] == args[1] else None

    pool = AsyncMock()
    pool.fetchrow.side_effect = fetchrow
    monkeypatch.setattr(documents, "get_db", AsyncMock(return_value=pool))
    monkeypatch.setattr(estimates, "get_db", AsyncMock(return_value=pool))
    app = FastAPI()
    app.include_router(documents.router)
    app.include_router(estimates.router)
    user = CurrentUser(id="test-user", role="editor")
    app.dependency_overrides[get_current_user] = lambda: user
    with TestClient(app) as client:
        yield client, rows, user, pool


def upload(client, text):
    response = client.post("/documents/upload-file", files={"file": ("spec.txt", text.encode(), "text/plain")})
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_upload_extract_analyze_uses_document_values(flow, sample_document_text, monkeypatch):
    client, rows, _, _ = flow
    doc_id = upload(client, sample_document_text)
    assert "file_data" not in rows[doc_id]
    extracted = client.post(f"/documents/{doc_id}/extract")
    assert extracted.status_code == 200, extracted.text
    assert extracted.json()["team_size"] != 5
    assert extracted.json()["duration_months"] == 12

    # Stop at the ML/persistence boundary and inspect actual NLP-derived inputs.
    from fastapi import HTTPException
    run = AsyncMock(side_effect=HTTPException(status_code=503, detail="Model unavailable"))
    monkeypatch.setattr(estimates.estimate_service, "run_estimation", run)
    response = client.post("/estimates/analyze", json={"document_id": doc_id})
    assert response.status_code == 503
    params = run.call_args.kwargs
    for name in ("team_size", "duration_months", "project_name", "tech_stack", "feature_count"):
        assert params[name] == extracted.json()[name]


def test_document_to_estimate_result_contract(flow, sample_document_text, monkeypatch):
    from unittest.mock import Mock

    from app.services import estimate_service as service_module
    client, _, _, pool = flow
    monkeypatch.setattr(service_module, "get_db", AsyncMock(return_value=pool))
    predict = Mock(return_value={"effort_hours_likely": 1000.0, "effort_hours_min": 800.0,
        "effort_hours_max": 1400.0, "confidence_pct": 70.0, "model_mode": "live"})
    monkeypatch.setattr(service_module.ml_service, "predict", predict)
    monkeypatch.setattr(estimates, "log_estimation_analytics", AsyncMock())
    doc_id = upload(client, sample_document_text)
    extracted = client.post(f"/documents/{doc_id}/extract").json()
    response = client.post("/estimates/analyze", json={"document_id": doc_id,
        "overrides": {"hourly_rate_usd": 100, "tech_stack": [], "integration_count": 0,
            "volatility_score": 5, "team_experience": 4}})
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["document_id"] == doc_id
    assert result["inputs"]["duration_months"] == 12
    assert result["inputs"]["tech_stack"] == []
    assert result["outputs"]["cost_likely_usd"] == 100000
    assert result["outputs"]["effort_likely_hours"] == 1000
    assert result["outputs"]["risk_level"] in {"Low", "Medium", "High", "Critical"}
    assert predict.call_args.args[0]["feature_count"] == extracted["feature_count"]
    assert predict.call_args.args[0]["size_fp"] > 0
    assert predict.call_args.args[0]["volatility_score"] == 5
    assert predict.call_args.args[0]["team_experience"] == 4
    assert result["inputs"]["integration_count"] == 0
    assert result["inputs"]["volatility_score"] == 5
    assert result["inputs"]["team_experience"] == 4
    assert result["inputs"]["feature_count"] == extracted["feature_count"]
    assert result["inputs"]["size_fp"] == predict.call_args.args[0]["size_fp"]


@pytest.mark.parametrize("failure,expected", [("missing", 409), ("empty", 422), ("foreign", 409), ("failed", 409)])
def test_bad_stored_document_never_reaches_estimation(flow, sample_document_text, monkeypatch, failure, expected):
    client, rows, _, _ = flow
    doc_id = upload(client, sample_document_text)
    row = rows[doc_id]
    if failure == "foreign":
        row["storage_path"] = "documents/another-user/file.txt"
    elif failure == "failed":
        row["status"] = "failed"
    else:
        path = storage_service.backend._resolve_key(row["storage_path"])
        if failure == "missing":
            path.unlink()
        else:
            path.write_bytes(b"")
    run = AsyncMock()
    monkeypatch.setattr(estimates.estimate_service, "run_estimation", run)
    assert client.post(f"/documents/{doc_id}/extract").status_code == expected
    assert client.post("/estimates/analyze", json={"document_id": doc_id}).status_code == expected
    run.assert_not_called()


def test_viewer_cannot_upload_or_extract(flow):
    client, _, user, pool = flow
    user.role = "viewer"
    assert client.post("/documents/upload-file", files={"file": ("s.txt", b"some text", "text/plain")}).status_code == 403
    assert client.post(f"/documents/{uuid4()}/extract").status_code == 403
    pool.fetchrow.assert_not_called()


def test_metadata_only_upload_cannot_claim_another_object(flow):
    client, _, _, pool = flow
    response = client.post("/documents/upload", json={"storage_path": "documents/victim/file.txt",
        "original_filename": "file.txt", "file_size_bytes": 10, "mime_type": "text/plain"})
    assert response.status_code == 410
    pool.fetchrow.assert_not_called()


def test_database_failure_cleans_up_uploaded_object(flow):
    client, _, _, pool = flow
    pool.fetchrow.side_effect = RuntimeError("private database details")
    response = client.post("/documents/upload-file", files={"file": ("s.txt", b"A project specification", "text/plain")})
    assert response.status_code == 500
    assert "private" not in response.text
    assert not [p for p in storage_service.backend.base_path.rglob("*") if p.is_file()]


@pytest.mark.parametrize("key", ["../escape", "/absolute", "C:/escape", "C:escape", "a/../../escape",
    "a\\..\\escape", "//server/share", "a//b", "a/./b", "a/.. /b", "a/file:stream", "a\x00b"])
@pytest.mark.parametrize("operation", ["upload", "download", "delete", "exists"])
async def test_storage_rejects_unsafe_keys(tmp_path, key, operation):
    backend = LocalStorageBackend(str(tmp_path / "uploads"))
    with pytest.raises(ValueError, match="Invalid storage key"):
        if operation == "upload":
            await backend.upload(b"data", key)
        else:
            await getattr(backend, operation)(key)


def test_generated_keys_ignore_client_path_components():
    key = storage_service.generate_key("../../user\\path", "..\\..\\escape:stream")
    assert len(key.split("/")) == 3
    assert ".." not in key and "\\" not in key and ":" not in key


async def test_upload_reads_only_bounded_bytes(monkeypatch):
    from app.services.document_analysis import MAX_DOCUMENT_BYTES
    from fastapi import HTTPException, UploadFile
    file = UploadFile(filename="large.txt", file=io.BytesIO())
    file.read = AsyncMock(return_value=b"x" * (MAX_DOCUMENT_BYTES + 1))
    with pytest.raises(HTTPException) as error:
        await documents.upload_document_file(file, CurrentUser(id="u"))
    assert error.value.status_code == 413
    file.read.assert_awaited_once_with(MAX_DOCUMENT_BYTES + 1)
