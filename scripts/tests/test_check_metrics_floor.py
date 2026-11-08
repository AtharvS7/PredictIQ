"""
Unit tests for scripts/check_metrics_floor.py (Checkpoint S09).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from scripts.check_metrics_floor import (
    DEFAULT_FLOOR_FILE,
    run_checks,
    verify_artifact_integrity,
    verify_empirical_benchmark_evidence,
    verify_serving_invariants,
)


def test_floor_specification_file_exists():
    """Verify that backend/ml/metrics_floor.json exists and has valid structure."""
    assert DEFAULT_FLOOR_FILE.exists(), f"Missing floor file: {DEFAULT_FLOOR_FILE}"
    config = json.loads(DEFAULT_FLOOR_FILE.read_text(encoding="utf-8"))
    assert config["contract_version"] == "2.0.0-rc.3"
    assert "dataset" in config
    assert "loso_cross_validation_floors" in config
    assert "serving_invariants" in config
    assert config["serving_invariants"]["min_prediction_hours"] == 1.0


def test_artifact_integrity_check():
    """Verify that Gate 1 passes against actual production bundle."""
    config = json.loads(DEFAULT_FLOOR_FILE.read_text(encoding="utf-8"))
    res = verify_artifact_integrity(config)
    assert res.status == "PASS"
    assert "Zero pickle" in res.message


def test_serving_invariants_check():
    """Verify that Gate 2 passes with monotonic predictions."""
    config = json.loads(DEFAULT_FLOOR_FILE.read_text(encoding="utf-8"))
    res = verify_serving_invariants(config)
    assert res.status == "PASS"
    assert "strict size monotonicity" in res.message


def test_empirical_benchmark_evidence_check():
    """Verify that Gate 3 passes with recorded benchmark outputs."""
    config = json.loads(DEFAULT_FLOOR_FILE.read_text(encoding="utf-8"))
    res = verify_empirical_benchmark_evidence(config)
    assert res.status == "PASS"


def test_run_checks_end_to_end():
    """Verify that all gates pass end-to-end."""
    all_pass, results = run_checks(DEFAULT_FLOOR_FILE)
    assert all_pass is True
    assert len(results) == 3
    assert all(r.status == "PASS" for r in results)
