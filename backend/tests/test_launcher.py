"""
Unit Tests for PredictIQ Demonstration Launcher and Port Allocation
"""

import json
import math
import socket
from pathlib import Path

from app.core.config import settings

ROOT = Path(__file__).resolve().parent.parent.parent
from run import (
    compute_canonical_json_sha256,
    find_free_port,
    is_pid_alive,
    is_port_free,
    kill_process,
    resolve_venv,
)


def test_resolve_venv():
    """Verify virtual environment detection returns valid python executable."""
    _, py_exe = resolve_venv()
    assert py_exe.is_file(), f"Python executable does not exist: {py_exe}"


def test_is_port_free_and_find_free_port():
    """Verify port detection finds free ports and respects avoided ports."""
    # Find an unbound port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        bound_port = s.getsockname()[1]

        # Port is currently bound
        assert not is_port_free(bound_port)

    # Now port should be free
    assert is_port_free(bound_port)

    # find_free_port avoids specified port
    free_port = find_free_port(8010, 8020, avoid={8000, 8010})
    assert free_port != 8000
    assert free_port != 8010
    assert 8011 <= free_port <= 8020


def test_model_params_canonical_hash():
    """Verify model parameters canonical hash matches manifest specification."""
    artifacts_dir = ROOT / "backend" / "ml" / "artifacts" / "production_v2"
    manifest_file = artifacts_dir / "manifest.json"
    params_file = artifacts_dir / "model_params.json"

    assert manifest_file.is_file()
    assert params_file.is_file()

    with manifest_file.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    expected_hash = manifest["file_hashes"]["model_params.json"]
    computed_hash = compute_canonical_json_sha256(params_file)

    assert computed_hash.lower() == expected_hash.lower()


def test_baseline_prediction_computation():
    """Verify mathematical baseline effort prediction for 50 FP (~616.1 hrs)."""
    artifacts_dir = ROOT / "backend" / "ml" / "artifacts" / "production_v2"
    params_file = artifacts_dir / "model_params.json"

    with params_file.open("r", encoding="utf-8") as f:
        params_data = json.load(f)

    p = params_data["parameters"]
    base = p.get("base_marginal", p)
    a = float(base.get("a", math.exp(float(base.get("beta0", 3.188036)))))
    b = float(base.get("b", 0.827027))

    effort = a * math.pow(50.0, b)
    assert 610.0 <= effort <= 625.0
    assert round(effort, 1) == 616.1


def test_cors_dynamic_ports():
    """Verify CORS origins include all preview and dev ports (5173-5179) in non-production."""
    cors = settings.cors_origins
    for port in range(5173, 5180):
        assert f"http://localhost:{port}" in cors
        assert f"http://127.0.0.1:{port}" in cors


def test_pid_lifecycle_safety():
    """Verify process lifecycle functions safely handle invalid or terminated PIDs."""
    assert not is_pid_alive(-999)
    assert not is_pid_alive(0)
    # Should not raise exception
    kill_process(-999)
    kill_process(0)
