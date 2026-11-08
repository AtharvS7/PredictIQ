"""Automated Model Sanity & Tamper Detection Suite for PredictIQ v2 (CP13).

Validates the frozen production artifact bundle (MultivariateMonotoneModel +
MondrianConformalPredictor) loaded via backend.ml.artifacts.loader:

1. Positive & Finite Predictions: All point and interval predictions strictly >= 1.0 hr.
2. Strict Functional Size Monotonicity: dE/dS > 0 strictly across dense grid (1 to 20,000 FP).
3. Quantile Monotonicity: 1.0 <= p10 <= p50 <= p90 everywhere across diverse inputs.
4. Fail-Closed Tamper Detection: Detects corrupted files, modified hashes, and revoked models.
5. Contract Compliance: Immediate rejection of banned features (T01-T15, Transactions, etc.).
6. Extreme Domain Extrapolation: Graceful handling of 0.01 FP, 100,000 FP, and negative durations.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402

from backend.ml.artifact_safety import (  # noqa: E402
    REVOKED_DATA_SHA256,
    REVOKED_MODEL_SHA256,
)
from backend.ml.artifacts.loader import (  # noqa: E402
    DEFAULT_PRODUCTION_ARTIFACTS_DIR,
    ProductionModelBundle,
    load_production_model,
)
from backend.ml.calibration.conformal import (  # noqa: E402
    MondrianConformalPredictor,
)
from backend.ml.track1.models import (  # noqa: E402
    BANNED_FEATURES,
    MonotonePowerLaw,
    MultivariateMonotoneModel,
)


@pytest.fixture(scope="module")
def bundle() -> ProductionModelBundle:
    """Fixture providing loaded and verified production bundle."""
    return load_production_model()


# =====================================================================
# 1. Positive & Finite Prediction Guarantees (>= 1.0 hr)
# =====================================================================


def test_loaded_model_produces_positive_finite_predictions(
    bundle: ProductionModelBundle,
) -> None:
    """Verify point and interval predictions are finite and clamped to >= 1.0 person-hour."""
    sizes = [1.0, 5.0, 25.0, 100.0, 350.0, 800.0, 2500.0, 10000.0]
    durations = [None, 1.0, 3.0, 6.0, 12.0, 24.0, 48.0]

    for s in sizes:
        for d in durations:
            df = pd.DataFrame({"size_fp": [s]})
            if d is not None:
                df["duration_months"] = [d]

            # Point estimate
            pred = bundle.predict(df)
            assert len(pred) == 1
            assert np.isfinite(pred[0]), f"Non-finite point prediction for size={s}, dur={d}"
            assert pred[0] >= 1.0, f"Prediction below 1.0 hr for size={s}, dur={d}: {pred[0]}"

            # Quantiles
            q = bundle.predict_quantiles(df)
            p10 = float(q["p10"][0])
            p50 = float(q["p50"][0])
            p90 = float(q["p90"][0])

            assert np.isfinite(p10) and np.isfinite(p50) and np.isfinite(p90)
            assert p10 >= 1.0, f"p10 below 1.0 hr: {p10}"
            assert p50 >= p10, f"p50 < p10: {p50} < {p10}"
            assert p90 >= p50, f"p90 < p50: {p90} < {p50}"


def test_dict_and_scalar_input_handling(bundle: ProductionModelBundle) -> None:
    """Verify bundle accepts dictionary and scalar input payloads."""
    payload = {"size_fp": 150.0, "duration_months": 8.0}
    pred = bundle.predict(payload)
    assert len(pred) == 1
    assert pred[0] >= 1.0

    quantiles = bundle.predict_quantiles(payload)
    assert quantiles["p10"][0] <= quantiles["p50"][0] <= quantiles["p90"][0]


# =====================================================================
# 2. Strict Functional Size Monotonicity (1 to 20,000 FP)
# =====================================================================


def test_strict_monotonicity_across_dense_size_grid(
    bundle: ProductionModelBundle,
) -> None:
    """Verify dE/dS > 0 strictly across a dense 2,000-point grid (1 to 20,000 FP)."""
    # Test on both linear and geometric size grids
    linear_grid = np.linspace(1.0, 20000.0, 2000)
    geom_grid = np.geomspace(1.0, 20000.0, 2000)

    for grid_name, grid in [("linear", linear_grid), ("geometric", geom_grid)]:
        # 1. Base Marginal Power Law (no duration)
        df_base = pd.DataFrame({"size_fp": grid})
        preds_base = bundle.predict(df_base)
        diffs_base = np.diff(preds_base)
        assert (diffs_base > 0).all(), (
            f"Strict monotonicity violated on {grid_name} grid without duration! "
            f"Min diff: {np.min(diffs_base)}"
        )

        # 2. Multivariate Model with fixed duration = 6.0 months
        df_dur = pd.DataFrame({"size_fp": grid, "duration_months": 6.0})
        preds_dur = bundle.predict(df_dur)
        diffs_dur = np.diff(preds_dur)
        assert (diffs_dur > 0).all(), (
            f"Strict monotonicity violated on {grid_name} grid with duration=6.0! "
            f"Min diff: {np.min(diffs_dur)}"
        )

        # 3. Quantile monotonicity (p10 <= p50 <= p90) holds at every point on the dense grid
        q = bundle.predict_quantiles(df_base)
        assert (q["p10"] <= q["p50"] + 1e-6).all(), f"p10 <= p50 violated on {grid_name} grid"
        assert (q["p50"] <= q["p90"] + 1e-6).all(), f"p50 <= p90 violated on {grid_name} grid"

        # 4. Within each Mondrian bucket, quantiles are strictly monotonic with size
        bucket_small = grid < 150.0
        bucket_medium = (grid >= 150.0) & (grid <= 750.0)
        bucket_large = grid > 750.0

        for b_name, mask in [("small", bucket_small), ("medium", bucket_medium), ("large", bucket_large)]:
            if np.sum(mask) > 1:
                p10_b = q["p10"][mask]
                p90_b = q["p90"][mask]
                assert (np.diff(p10_b) > 0).all(), f"p10 not strictly increasing within {b_name} bucket"
                assert (np.diff(p90_b) > 0).all(), f"p90 not strictly increasing within {b_name} bucket"


# =====================================================================
# 3. Quantile Monotonicity (p10 <= p50 <= p90)
# =====================================================================


def test_quantile_monotonicity_across_diverse_inputs(
    bundle: ProductionModelBundle,
) -> None:
    """Verify 1.0 <= p10 <= p50 <= p90 holds strictly for all inputs."""
    sizes = [
        1.0, 10.0, 45.0, 149.0, 150.0, 300.0, 749.0, 750.0, 751.0,
        1500.0, 5000.0, 20000.0
    ]
    durations = [None, 0.5, 1.0, 3.0, 6.0, 12.0, 24.0, 60.0]

    for s in sizes:
        for d in durations:
            row = {"size_fp": s}
            if d is not None:
                row["duration_months"] = d
            df = pd.DataFrame([row])

            q = bundle.predict_quantiles(df)
            p10 = float(q["p10"][0])
            p50 = float(q["p50"][0])
            p90 = float(q["p90"][0])
            point_pred = float(bundle.predict(df)[0])

            # Invariant 1: p10 >= 1.0
            assert p10 >= 1.0, f"p10 < 1.0 for s={s}, d={d}: {p10}"

            # Invariant 2: p10 <= p50
            assert p10 <= p50 + 1e-6, f"p10 > p50 for s={s}, d={d}: {p10} > {p50}"

            # Invariant 3: p50 <= p90
            assert p50 <= p90 + 1e-6, f"p50 > p90 for s={s}, d={d}: {p50} > {p90}"

            # Invariant 4: p50 coincides with point prediction
            assert abs(p50 - point_pred) < 1e-6, f"p50 ({p50}) != point_pred ({point_pred})"

            # Invariant 5: Non-empty interval width
            assert p90 - p10 > 0, f"Zero-width interval for s={s}, d={d}"


def test_predict_interval_returns_matching_tuple(
    bundle: ProductionModelBundle,
) -> None:
    """Verify predict_interval returns identical arrays to predict_quantiles."""
    df = pd.DataFrame({"size_fp": [50.0, 250.0, 1200.0]})
    p10, p50, p90 = bundle.predict_interval(df)
    q = bundle.predict_quantiles(df)

    np.testing.assert_allclose(p10, q["p10"])
    np.testing.assert_allclose(p50, q["p50"])
    np.testing.assert_allclose(p90, q["p90"])


# =====================================================================
# 4. Fail-Closed Tamper Detection
# =====================================================================


def test_fail_closed_on_corrupted_model_file(
    tmp_path: Path,
) -> None:
    """Verify corruption in model_params.json immediately raises RuntimeError."""
    test_dir = tmp_path / "tampered_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)

    # Flip bytes in model_params.json
    params_file = test_dir / "model_params.json"
    raw_bytes = bytearray(params_file.read_bytes())
    raw_bytes[10] = (raw_bytes[10] + 1) % 256
    params_file.write_bytes(bytes(raw_bytes))

    with pytest.raises(RuntimeError):
        load_production_model(test_dir)


def test_fail_closed_on_tampered_manifest_hashes(
    tmp_path: Path,
) -> None:
    """Verify modifying file hash in manifest.json triggers RuntimeError."""
    test_dir = tmp_path / "tampered_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)

    manifest_file = test_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["file_hashes"]["model_params.json"] = "0" * 64
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="SHA-256 checksum mismatch"):
        load_production_model(test_dir)


def test_fail_closed_on_missing_files(tmp_path: Path) -> None:
    """Verify missing artifact or manifest files trigger RuntimeError."""
    test_dir = tmp_path / "tampered_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)

    # Delete model_params.json
    (test_dir / "model_params.json").unlink()
    with pytest.raises(RuntimeError, match="Required production artifact file missing: model_params.json"):
        load_production_model(test_dir)

    # Re-copy and delete manifest.json
    shutil.rmtree(test_dir)
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)
    (test_dir / "manifest.json").unlink()
    with pytest.raises(RuntimeError, match="Production manifest file missing"):
        load_production_model(test_dir)


def test_fail_closed_on_revoked_hashes(tmp_path: Path) -> None:
    """Verify presence of any revoked checksum raises RuntimeError."""
    test_dir = tmp_path / "tampered_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)

    manifest_file = test_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))

    # Case 1: manifest references revoked dataset hash
    revoked_data_hash = next(iter(REVOKED_DATA_SHA256))
    manifest["dataset_sha256"] = revoked_data_hash
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError, match="revoked training dataset"):
        load_production_model(test_dir)

    # Case 2: artifact file has revoked model hash
    revoked_model_hash = next(iter(REVOKED_MODEL_SHA256))
    manifest["dataset_sha256"] = "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3"
    manifest["model_sha256"] = revoked_model_hash
    manifest["file_hashes"]["model_params.json"] = revoked_model_hash
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(RuntimeError):
        load_production_model(test_dir)


def test_environment_spec_does_not_block_startup(
    tmp_path: Path,
) -> None:
    """Verify Python environment version spec is informational and does not block."""
    test_dir = tmp_path / "tampered_bundle"
    shutil.copytree(DEFAULT_PRODUCTION_ARTIFACTS_DIR, test_dir)

    manifest_file = test_dir / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    manifest["environment"]["python_major_minor"] = "2.7"
    manifest_file.write_text(json.dumps(manifest), encoding="utf-8")

    bundle = load_production_model(test_dir)
    assert bundle.model_version == "2.0.0-rc.3"


def test_fail_closed_on_expected_manifest_hash_mismatch() -> None:
    """Verify explicit expected_manifest_hash check rejects invalid hashes."""
    with pytest.raises(RuntimeError, match="Manifest checksum mismatch"):
        load_production_model(expected_manifest_hash="f" * 64)


# =====================================================================
# 5. Contract Compliance & Banned Features Rejection
# =====================================================================


@pytest.mark.parametrize("banned_feature", sorted(list(BANNED_FEATURES)))
def test_banned_features_rejection(
    bundle: ProductionModelBundle,
    banned_feature: str,
) -> None:
    """Verify every banned feature from ml_contract.md is immediately rejected."""
    # Test uppercase and lowercase feature names
    for col_name in [banned_feature.lower(), banned_feature.upper()]:
        df = pd.DataFrame({"size_fp": [100.0], col_name: [5.0]})

        # Point estimator predict must reject
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            bundle.predict(df)

        # Conformal calibrator predict_quantiles must reject
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            bundle.predict_quantiles(df)

        # Dictionary payload must reject
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            bundle.predict({"size_fp": 100.0, col_name: 5.0})

        # Input validator must reject
        with pytest.raises(ValueError, match="ML Contract Violation: Forbidden feature"):
            bundle.validate_inputs(df)


# =====================================================================
# 6. Extreme Domain Extrapolation & Edge Cases
# =====================================================================


def test_extreme_domain_inputs(bundle: ProductionModelBundle) -> None:
    """Verify model gracefully handles extreme domain inputs."""
    # 1. Micro-project (0.01 FP)
    micro_df = pd.DataFrame({"size_fp": [0.01]})
    micro_pred = bundle.predict(micro_df)[0]
    assert np.isfinite(micro_pred)
    assert micro_pred >= 1.0

    micro_q = bundle.predict_quantiles(micro_df)
    assert 1.0 <= micro_q["p10"][0] <= micro_q["p50"][0] <= micro_q["p90"][0]

    # 2. Mega-project (100,000 FP)
    mega_df = pd.DataFrame({"size_fp": [100000.0]})
    mega_pred = bundle.predict(mega_df)[0]
    assert np.isfinite(mega_pred)
    assert mega_pred > bundle.predict(pd.DataFrame({"size_fp": [20000.0]}))[0]

    mega_q = bundle.predict_quantiles(mega_df)
    assert 1.0 <= mega_q["p10"][0] <= mega_q["p50"][0] <= mega_q["p90"][0]

    # 3. Non-positive or invalid duration: gracefully handled as missing duration
    for invalid_dur in [-12.0, -0.01, 0.0, np.nan]:
        dur_df = pd.DataFrame({"size_fp": [250.0], "duration_months": [invalid_dur]})
        base_df = pd.DataFrame({"size_fp": [250.0]})

        # When duration is invalid, model should evaluate base power law
        pred_dur = bundle.predict(dur_df)[0]
        pred_base = bundle.predict(base_df)[0]
        assert np.isclose(pred_dur, pred_base, rtol=1e-5), (
            f"Invalid duration ({invalid_dur}) did not gracefully fall back to base marginal model."
        )

    # 4. Non-positive size: must raise ValueError
    for bad_size in [0.0, -1.0, -100.0]:
        bad_df = pd.DataFrame({"size_fp": [bad_size]})
        with pytest.raises(ValueError, match="strictly positive and finite"):
            bundle.predict(bad_df)


# =====================================================================
# 7. Model Unpacking & Consistency
# =====================================================================


def test_bundle_unpacking_and_equality(bundle: ProductionModelBundle) -> None:
    """Verify bundle supports tuple unpacking: model, conformal = bundle."""
    model, conformal = bundle
    assert isinstance(model, (MonotonePowerLaw, MultivariateMonotoneModel))
    assert isinstance(conformal, MondrianConformalPredictor)

    df = pd.DataFrame({"size_fp": [120.0], "duration_months": [4.0]})
    pred_direct = model.predict(df)
    pred_bundle = bundle.predict(df)
    np.testing.assert_allclose(pred_direct, pred_bundle)

    q_direct = conformal.predict_quantiles(df)
    q_bundle = bundle.predict_quantiles(df)
    np.testing.assert_allclose(q_direct["p10"], q_bundle["p10"])
    np.testing.assert_allclose(q_direct["p50"], q_bundle["p50"])
    np.testing.assert_allclose(q_direct["p90"], q_bundle["p90"])
