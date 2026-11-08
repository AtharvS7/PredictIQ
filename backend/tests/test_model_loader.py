"""Unit and integration tests for Hardened Production Model Loader (S01 / WS_PORT).

Validates:
1. Canonical UTF-8 SHA-256 verification of JSON artifacts.
2. Cross-platform LF vs CRLF newline tolerance: identical hash across Windows and Linux.
3. Zero-pickle pure JSON parameter serving runtime.
4. Fail-closed behavior on:
   - Tampered model parameters.
   - Tampered manifest hashes.
   - Missing manifest or model_params.json.
   - Schema drift (missing keys, invalid parameters, negative slopes).
   - Revoked SHA-256 digests.
5. Non-blocking Python environment version logging.
6. Service readiness: GET /api/v1/ready returns 200 on verified bundle and 503 on tampered bundle.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.ml.artifact_safety import (
    REVOKED_DATA_SHA256,
    REVOKED_MODEL_SHA256,
)
from backend.ml.artifacts.loader import (
    DEFAULT_PRODUCTION_ARTIFACTS_DIR,
    EXPECTED_DATASET_SHA256,
    ProductionModelBundle,
    compute_canonical_json_sha256,
    load_production_model,
)
from backend.ml.calibration.conformal import (
    MondrianConformalPredictor,
)
from backend.ml.track1.models import (
    MonotonePowerLaw,
)


# =====================================================================
# 1. Production Bundle Clean Load & Contract Conformance
# =====================================================================


def test_production_bundle_loads_cleanly() -> None:
    """Verify production bundle loads with 100% verified integrity and valid contracts."""
    bundle = load_production_model()

    assert isinstance(bundle, ProductionModelBundle)
    assert bundle.model_version == "2.0.0-rc.3"
    assert bundle.architecture == "MonotonePowerLaw + MondrianConformal"
    assert bundle.allowed_inputs == ["size_fp"]
    assert "t01" in bundle.banned_features

    # Estimator & Conformal Predictor types
    assert isinstance(bundle.model, MonotonePowerLaw)
    assert isinstance(bundle.conformal, MondrianConformalPredictor)

    # Inference verification
    pred = bundle.predict({"size_fp": 150.0})
    assert len(pred) == 1
    assert pred[0] >= 1.0

    quantiles = bundle.predict_quantiles({"size_fp": 150.0})
    p10 = float(quantiles["p10"][0])
    p25 = float(quantiles["p25"][0])
    p50 = float(quantiles["p50"][0])
    p75 = float(quantiles["p75"][0])
    p90 = float(quantiles["p90"][0])

    assert 1.0 <= p10 <= p25 <= p50 <= p75 <= p90
    assert abs(p50 - pred[0]) < 1e-5


def test_tuple_unpacking() -> None:
    """Verify bundle supports tuple unpacking: model, conformal = bundle."""
    bundle = load_production_model()
    model, conformal = bundle
    assert isinstance(model, MonotonePowerLaw)
    assert isinstance(conformal, MondrianConformalPredictor)


# =====================================================================
# 2. Canonical Bytes Hashing & Line-Ending Invariance (LF vs CRLF)
# =====================================================================


def test_canonical_json_hash_is_newline_invariant(tmp_path: Path) -> None:
    """Canonical JSON hashing must produce identical SHA-256 for LF and CRLF on disk."""
    prod_params = DEFAULT_PRODUCTION_ARTIFACTS_DIR / "model_params.json"
    raw_text = prod_params.read_text(encoding="utf-8")

    # Construct strict LF and strict CRLF variations
    text_lf = raw_text.replace("\r\n", "\n")
    text_crlf = raw_text.replace("\r\n", "\n").replace("\n", "\r\n")

    lf_file = tmp_path / "params_lf.json"
    crlf_file = tmp_path / "params_crlf.json"

    # Write binary bytes to ensure exact disk representation
    lf_file.write_bytes(text_lf.encode("utf-8"))
    crlf_file.write_bytes(text_crlf.encode("utf-8"))

    # Raw file sizes differ due to \r\n vs \n
    assert lf_file.stat().st_size != crlf_file.stat().st_size

    # Canonical hashes MUST be strictly identical
    hash_lf = compute_canonical_json_sha256(lf_file)
    hash_crlf = compute_canonical_json_sha256(crlf_file)

    assert hash_lf == hash_crlf
    assert len(hash_lf) == 64


def test_bundle_loads_identically_with_crlf_or_lf_files(tmp_path: Path) -> None:
    """Bundle must verify and load with zero errors on both Windows (CRLF) and Linux (LF)."""
    prod_params = DEFAULT_PRODUCTION_ARTIFACTS_DIR / "model_params.json"
    raw_text = prod_params.read_text(encoding="utf-8")

    text_lf = raw_text.replace("\r\n", "\n")
    text_crlf = raw_text.replace("\r\n", "\n").replace("\n", "\r\n")

    for newline_mode, content in [("linux_lf", text_lf), ("windows_crlf", text_crlf)]:
        bundle_dir = tmp_path / newline_mode
        bundle_dir.mkdir()

        # Copy manifest
        shutil.copy(DEFAULT_PRODUCTION_ARTIFACTS_DIR / "manifest.json", bundle_dir / "manifest.json")

        # Write model_params.json with specific line endings
        (bundle_dir / "model_params.json").write_bytes(content.encode("utf-8"))

        loaded = load_production_model(bundle_dir)
        assert loaded.model_version == "2.0.0-rc.3"

        pred = loaded.predict({"size_fp": 200.0})
        assert pred[0] >= 1.0


# =====================================================================
# 3. Fail-Closed Tamper Detection
# =====================================================================


def test_fail_closed_on_tampered_model_parameters(tmp_path: Path) -> None:
    """Altering numeric parameters in model_params.json must trigger immediate RuntimeError."""
    bundle_dir = tmp_path / "tampered_params"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    params_file = bundle_dir / "model_params.json"
    data = json.loads(params_file.read_text(encoding="utf-8"))
    data["parameters"]["base_marginal"]["b"] = 1.999999
    params_file.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(RuntimeError, match="SHA-256 checksum mismatch for 'model_params.json'"):
        load_production_model(bundle_dir)


def test_fail_closed_on_tampered_manifest_hashes(tmp_path: Path) -> None:
    """Altering expected checksum in manifest file_hashes must trigger RuntimeError."""
    bundle_dir = tmp_path / "tampered_manifest"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    manifest_file = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["file_hashes"]["model_params.json"] = "a" * 64
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="SHA-256 checksum mismatch for 'model_params.json'"):
        load_production_model(bundle_dir)


def test_fail_closed_on_tampered_manifest_model_sha256(tmp_path: Path) -> None:
    """Altering top-level model_sha256 in manifest must trigger RuntimeError."""
    bundle_dir = tmp_path / "tampered_model_sha256"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    manifest_file = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["model_sha256"] = "b" * 64
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="Manifest model_sha256 mismatch"):
        load_production_model(bundle_dir)


def test_fail_closed_on_missing_manifest(tmp_path: Path) -> None:
    """Missing manifest.json must trigger RuntimeError."""
    bundle_dir = tmp_path / "missing_manifest"
    bundle_dir.mkdir()
    shutil.copy(DEFAULT_PRODUCTION_ARTIFACTS_DIR / "model_params.json", bundle_dir / "model_params.json")

    with pytest.raises(RuntimeError, match="Production manifest file missing"):
        load_production_model(bundle_dir)


def test_fail_closed_on_missing_model_params(tmp_path: Path) -> None:
    """Missing model_params.json must trigger RuntimeError."""
    bundle_dir = tmp_path / "missing_params"
    bundle_dir.mkdir()
    shutil.copy(DEFAULT_PRODUCTION_ARTIFACTS_DIR / "manifest.json", bundle_dir / "manifest.json")

    with pytest.raises(RuntimeError, match="Required production artifact file missing: model_params.json"):
        load_production_model(bundle_dir)


def test_fail_closed_on_revoked_hashes(tmp_path: Path) -> None:
    """Presence of any revoked checksum must trigger RuntimeError."""
    bundle_dir = tmp_path / "revoked_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    manifest_file = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    # Case 1: Revoked dataset SHA-256
    revoked_data_hash = next(iter(REVOKED_DATA_SHA256))
    manifest["dataset_sha256"] = revoked_data_hash
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="revoked training dataset checksum"):
        load_production_model(bundle_dir)

    # Case 2: Revoked model SHA-256
    revoked_model_hash = next(iter(REVOKED_MODEL_SHA256))
    manifest["dataset_sha256"] = EXPECTED_DATASET_SHA256
    manifest["model_sha256"] = revoked_model_hash
    manifest["file_hashes"]["model_params.json"] = revoked_model_hash
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="revoked security checksum"):
        load_production_model(bundle_dir)


# =====================================================================
# 4. Schema Drift & Non-Blocking Environment Pins
# =====================================================================


@pytest.mark.parametrize(
    "drift_mutator,error_match",
    [
        (lambda d: d.pop("parameters"), "Schema drift: model params in .* missing key 'parameters'"),
        (lambda d: d["parameters"].pop("base_marginal"), "Schema drift: 'base_marginal' in .* missing 'beta0' or 'a'"),
        (lambda d: d["parameters"]["base_marginal"].pop("b"), "Schema drift: 'base_marginal' in .* missing 'b'"),
        (lambda d: d["parameters"]["base_marginal"].update({"b": -0.5}), "Schema drift: 'b' in .* must be a strictly positive"),
        (lambda d: d.pop("calibration"), "Schema drift: model params in .* missing key 'calibration'"),
        (lambda d: d["calibration"].pop("conformal_80"), "Schema drift: 'calibration' in .* missing 'conformal_80'"),
        (lambda d: d["calibration"]["conformal_80"].pop("global_quantile"), "Schema drift: 'conformal_80' in .* missing 'global_quantile'"),
    ],
)
def test_fail_closed_on_schema_drift(tmp_path: Path, drift_mutator, error_match) -> None:
    """Schema drift must raise RuntimeError even if manifest hash matches the drifted artifact."""
    bundle_dir = tmp_path / "drifted_bundle"
    if bundle_dir.exists():
        shutil.rmtree(bundle_dir)
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    params_file = bundle_dir / "model_params.json"
    manifest_file = bundle_dir / "manifest.json"

    data = json.loads(params_file.read_text(encoding="utf-8"))
    drift_mutator(data)
    params_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # Update manifest hash to match drifted content to ensure the drift check catches it
    drifted_hash = compute_canonical_json_sha256(params_file)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["file_hashes"]["model_params.json"] = drifted_hash
    manifest["model_sha256"] = drifted_hash
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with pytest.raises(RuntimeError, match=error_match):
        load_production_model(bundle_dir)


def test_environment_spec_does_not_block_startup(tmp_path: Path) -> None:
    """Python environment version differences should be logged, not block startup."""
    bundle_dir = tmp_path / "env_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, bundle_dir)

    manifest_file = bundle_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["environment"]["python_major_minor"] = "3.99"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    bundle = load_production_model(bundle_dir)
    assert bundle.model_version == "2.0.0-rc.3"


# =====================================================================
# 5. Service Readiness HTTP Probes (200 on bundle, 503 on tamper)
# =====================================================================


@pytest.fixture
def test_client_with_mocks():
    """Create a TestClient with mocked DB pool and Firebase."""
    with patch("main.init_firebase"), \
         patch("main.init_db_pool", new_callable=AsyncMock), \
         patch("main.close_db_pool", new_callable=AsyncMock), \
         patch("app.api.v1.health.get_db") as mock_get_db, \
         patch("firebase_admin.get_app", return_value=True):

        mock_pool = AsyncMock()
        mock_pool.fetchval.return_value = 1
        mock_pool.execute.return_value = None
        mock_get_db.return_value = mock_pool

        from main import app
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client


def test_ready_returns_200_with_valid_bundle(test_client_with_mocks) -> None:
    """GET /api/v1/ready returns HTTP 200 with the active production bundle."""
    client = test_client_with_mocks
    resp = client.get("/api/v1/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["model_version"] == "2.0.0-rc.3"
    assert data["best_model"] == "MonotonePowerLaw + MondrianConformal"
    assert data["capabilities"]["automatic_prediction"] is True


def test_ready_returns_503_when_tampered(test_client_with_mocks) -> None:
    """GET /api/v1/ready returns HTTP 503 when the bundle is tampered or unverified."""
    client = test_client_with_mocks

    with patch("app.api.v1.health.ml_service.is_ready", return_value=False), \
         patch("app.api.v1.health.ml_service.get_model_info", return_value={
             "model_loaded": False,
             "model_mode": "unavailable",
             "model_version": None,
             "error": "Model bundle unavailable or failed verification",
         }):

        resp = client.get("/api/v1/ready")
        assert resp.status_code == 503
        data = resp.json()
        assert data["status"] == "degraded"
        assert data["capabilities"]["automatic_prediction"] is False
        assert data["services"]["ml_model"] == "not_loaded"
