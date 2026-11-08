"""Tests for Bulk Project Import API & Empirical Bayes Calibration Preview (Checkpoint S06)."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-at-least-32-bytes-long!")

from app.core.security import CurrentUser, get_current_user
from fastapi.testclient import TestClient


def _make_client(role: str = "editor"):
    """Create a TestClient with mocked auth and database pool."""
    import app.core.database as db_module
    from main import app

    mock_pool = AsyncMock()
    mock_pool.fetchrow = AsyncMock(return_value=None)
    mock_pool.fetch = AsyncMock(return_value=[])
    mock_pool.execute = AsyncMock(return_value="UPDATE 0")
    mock_pool.fetchval = AsyncMock(return_value=0)
    db_module._pool = mock_pool

    test_user = CurrentUser(id="test-user-bulk", email="bulk@example.com", role=role)
    app.dependency_overrides[get_current_user] = lambda: test_user

    client = TestClient(app, raise_server_exceptions=False)
    return client, app


def test_bulk_import_json_valid():
    """Bulk import via JSON payload succeeds and computes calibration preview."""
    client, app = _make_client(role="editor")
    payload = {
        "projects": [
            {"project_name": "Portal A", "size_fp": 120.0, "actual_hours": 1500.0, "platform": "Web"},
            {"project_name": "API Service", "size_fp": 80.0, "actual_hours": 950.0, "platform": "Backend"},
            {"project_name": "Mobile App", "size_fp": 220.0, "actual_hours": 2800.0, "platform": "iOS"},
        ]
    }
    resp = client.post("/api/v1/estimates/bulk-import", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_submitted"] == 3
    assert data["valid_count"] == 3
    assert data["error_count"] == 0
    assert len(data["errors"]) == 0

    cal = data["calibration_preview"]
    assert cal["k_projects"] == 3
    assert cal["shrinkage_weight"] > 0.0
    assert cal["exponent_b"] > 0.0
    assert cal["scaling_ratio"] > 0.0


def test_bulk_import_csv_valid_comma():
    """Bulk import via CSV upload (comma delimiter) succeeds."""
    client, app = _make_client(role="editor")
    csv_content = (
        "project_name,size_fp,actual_hours,platform\n"
        "E-Commerce Gateway,150,1800,Web\n"
        "Billing Engine,250,3100,Backend\n"
        "Analytics Dashboard,95,1100,Data\n"
    )
    files = {"file": ("projects.csv", csv_content.encode("utf-8"), "text/csv")}
    resp = client.post("/api/v1/estimates/bulk-import", files=files)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_submitted"] == 3
    assert data["valid_count"] == 3
    assert data["error_count"] == 0
    assert data["calibration_preview"]["k_projects"] == 3


def test_bulk_import_csv_tab_and_semicolon():
    """Bulk import detects tab and semicolon delimiters with CRLF."""
    client, app = _make_client(role="editor")

    # Tab-delimited with CRLF
    tab_content = (
        "project_name\tsize_fp\tactual_hours\r\n"
        "Project Alpha\t100\t1200\r\n"
        "Project Beta\t200\t2400\r\n"
    )
    files = {"file": ("projects.tsv", tab_content.encode("utf-8-sig"), "text/tab-separated-values")}
    resp = client.post("/api/v1/estimates/bulk-import", files=files)
    assert resp.status_code == 200, resp.text
    assert resp.json()["valid_count"] == 2

    # Semicolon-delimited
    semi_content = (
        "project_name;size_fp;actual_hours\n"
        "Project Gamma;140;1600\n"
        "Project Delta;280;3200\n"
    )
    files_semi = {"file": ("projects_semi.csv", semi_content.encode("latin-1"), "text/csv")}
    resp_semi = client.post("/api/v1/estimates/bulk-import", files=files_semi)
    assert resp_semi.status_code == 200, resp_semi.text
    assert resp_semi.json()["valid_count"] == 2


def test_bulk_import_row_errors_tolerated():
    """Invalid rows (negative size, missing hours) are reported in errors without failing valid rows."""
    client, app = _make_client(role="editor")
    payload = {
        "projects": [
            {"project_name": "Valid 1", "size_fp": 100.0, "actual_hours": 1200.0},
            {"project_name": "Invalid Size", "size_fp": -5.0, "actual_hours": 1000.0},
            {"project_name": "Invalid Effort", "size_fp": 150.0, "actual_hours": 0.0},
            {"project_name": "Valid 2", "size_fp": 300.0, "actual_hours": 3500.0},
        ]
    }
    resp = client.post("/api/v1/estimates/bulk-import", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_submitted"] == 4
    assert data["valid_count"] == 2
    assert data["error_count"] == 2
    assert len(data["errors"]) == 2
    assert data["errors"][0]["row_index"] == 2
    assert data["errors"][1]["row_index"] == 3
    assert data["calibration_preview"]["k_projects"] == 2


def test_bulk_import_empty_file_rejected():
    """Empty CSV file returns 400 Bad Request."""
    client, app = _make_client(role="editor")
    files = {"file": ("empty.csv", b"", "text/csv")}
    resp = client.post("/api/v1/estimates/bulk-import", files=files)
    assert resp.status_code == 400
    assert "empty" in resp.json()["detail"].lower()


def test_bulk_import_rbac_enforcement():
    """Viewer role is forbidden (403); Editor role succeeds (200)."""
    # Viewer
    viewer_client, _ = _make_client(role="viewer")
    payload = {"projects": [{"project_name": "P1", "size_fp": 100.0, "actual_hours": 1000.0}]}
    resp_viewer = viewer_client.post("/api/v1/estimates/bulk-import", json=payload)
    assert resp_viewer.status_code == 403

    # Editor
    editor_client, _ = _make_client(role="editor")
    resp_editor = editor_client.post("/api/v1/estimates/bulk-import", json=payload)
    assert resp_editor.status_code == 200


def test_calibration_preview_endpoint():
    """POST /api/v1/estimates/calibration-preview returns expected shrinkage metrics."""
    client, app = _make_client(role="viewer")  # Available to any authenticated user
    payload = {
        "projects": [
            {"project_name": "P1", "size_fp": 100.0, "actual_hours": 1200.0},
            {"project_name": "P2", "size_fp": 200.0, "actual_hours": 2200.0},
            {"project_name": "P3", "size_fp": 300.0, "actual_hours": 3100.0},
        ]
    }
    resp = client.post("/api/v1/estimates/calibration-preview", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["k_projects"] == 3
    assert 0.0 < data["shrinkage_weight"] < 1.0
    assert data["global_a"] > 0.0
    assert data["calibrated_a"] > 0.0
    assert data["scaling_ratio"] > 0.0
