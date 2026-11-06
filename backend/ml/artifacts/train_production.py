"""Production Model Artifact Bundling Pipeline (CP12).

Trains the frozen primary production model:
- Primary Estimator: Track 1 MultivariateMonotoneModel (with MonotonePowerLaw base)
- Calibrator: MondrianConformalPredictor (80% nominal coverage with size buckets < 150, 150-750, > 750)

Trained on the complete harmonized dataset:
- Dataset: backend/ml/data/projects_v2.csv (915 records)
- Frozen SHA-256: b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3

Outputs to backend/ml/artifacts/production_v2/:
- model.pkl (fitted estimator)
- conformal.pkl (fitted calibrator)
- manifest.json (metadata, checksums, contract specifications)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402

from backend.ml.artifact_safety import (  # noqa: E402
    REVOKED_DATA_SHA256,
    REVOKED_MODEL_SHA256,
)
from backend.ml.calibration.conformal import (  # noqa: E402
    MONDRIAN_BUCKETS,
    SIZE_BUCKET_THRESHOLDS,
    MondrianConformalPredictor,
)
from backend.ml.eval.protocol import load_dataset  # noqa: E402
from backend.ml.track1.models import (  # noqa: E402
    BANNED_FEATURES,
    MultivariateMonotoneModel,
)

logger = logging.getLogger(__name__)

EXPECTED_DATASET_SHA256 = (
    "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3"
)
EXPECTED_DATASET_RECORDS = 915
PRODUCTION_MODEL_VERSION = "2.0.0-rc.1"
DEFAULT_ARTIFACTS_DIR = Path(__file__).resolve().parent / "production_v2"


def compute_file_sha256(file_path: Path) -> str:
    """Compute the SHA-256 checksum of a file in binary mode."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def train_and_bundle_production_model(
    dataset_path: Path | str | None = None,
    output_dir: Path | str | None = None,
    alpha: float = 0.20,
    cal_size: float = 0.20,
    random_state: int = 42,
) -> tuple[MultivariateMonotoneModel, MondrianConformalPredictor, dict[str, Any]]:
    """Train and bundle the production model artifacts into production_v2/.

    Parameters
    ----------
    dataset_path : Path | str | None
        Path to projects_v2.csv. Defaults to backend/ml/data/projects_v2.csv.
    output_dir : Path | str | None
        Directory where artifacts are bundled. Defaults to backend/ml/artifacts/production_v2/.
    alpha : float
        Significance level for conformal calibration (default 0.20 -> 80% coverage).
    cal_size : float
        Fraction of training observations allocated to calibration (default 0.20).
    random_state : int
        Seed for reproducible train/calibration split (default 42).

    Returns
    -------
    tuple[MultivariateMonotoneModel, MondrianConformalPredictor, dict[str, Any]]
        The fitted estimator, fitted calibrator, and manifest dictionary.
    """
    out_path = Path(output_dir) if output_dir is not None else DEFAULT_ARTIFACTS_DIR
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Dataset verification
    resolved_ds_path = (
        Path(dataset_path)
        if dataset_path is not None
        else Path(__file__).resolve().parent.parent / "data" / "projects_v2.csv"
    )
    if not resolved_ds_path.exists():
        raise FileNotFoundError(f"Dataset not found at: {resolved_ds_path}")

    actual_sha256 = compute_file_sha256(resolved_ds_path)
    if actual_sha256 in REVOKED_DATA_SHA256:
        raise ValueError(
            f"Dataset at {resolved_ds_path} has revoked SHA-256 checksum: {actual_sha256}"
        )

    if actual_sha256 != EXPECTED_DATASET_SHA256:
        raise ValueError(
            f"Dataset SHA-256 mismatch. Expected {EXPECTED_DATASET_SHA256}, got {actual_sha256}"
        )

    df = load_dataset(resolved_ds_path)
    if len(df) != EXPECTED_DATASET_RECORDS:
        raise ValueError(
            f"Dataset records mismatch. Expected {EXPECTED_DATASET_RECORDS}, got {len(df)}"
        )

    logger.info(
        "Dataset verified: %d records, SHA-256=%s",
        len(df),
        actual_sha256,
    )

    # 2. Train Primary Estimator and Calibrate Conformal Predictor
    y = df["effort_hours"].to_numpy(dtype=np.float64)

    base_estimator = MultivariateMonotoneModel(
        b_min=1e-4,
        c_bounds=(0.0, 1.2),
        delta=1.35,
        max_iter=500,
    )

    calibrator = MondrianConformalPredictor(
        estimator=base_estimator,
        alpha=alpha,
        score_type="log_residual",
        cal_size=cal_size,
        min_bucket_samples=5,
        random_state=random_state,
    )

    logger.info("Fitting and calibrating MondrianConformalPredictor...")
    calibrator.fit(df, y)

    estimator: MultivariateMonotoneModel = calibrator.estimator_
    if estimator.a_base_ is None or estimator.b_base_ is None:
        raise RuntimeError("Base estimator fitting failed.")

    logger.info(
        "Model fitted: base_a=%.4f, base_b=%.4f, multi_a=%.4f, multi_b=%.4f, multi_c=%.4f",
        estimator.a_base_,
        estimator.b_base_,
        estimator.a_ or 0.0,
        estimator.b_ or 0.0,
        estimator.c_ or 0.0,
    )
    logger.info(
        "Calibration quantiles: global=%.4f, buckets=%s",
        calibrator.global_quantile_ or 0.0,
        calibrator.bucket_quantiles_,
    )

    # 3. Serialize Artifacts
    model_path = out_path / "model.pkl"
    conformal_path = out_path / "conformal.pkl"

    with model_path.open("wb") as f_model:
        pickle.dump(estimator, f_model, protocol=5)

    with conformal_path.open("wb") as f_conf:
        pickle.dump(calibrator, f_conf, protocol=5)

    # 4. Compute Artifact Hashes and Safety Audit
    model_sha256 = compute_file_sha256(model_path)
    conformal_sha256 = compute_file_sha256(conformal_path)

    if model_sha256 in REVOKED_MODEL_SHA256:
        raise RuntimeError(
            f"Model artifact produced revoked checksum: {model_sha256}"
        )
    if conformal_sha256 in REVOKED_MODEL_SHA256:
        raise RuntimeError(
            f"Conformal artifact produced revoked checksum: {conformal_sha256}"
        )

    # 5. Build and Write Manifest
    manifest: dict[str, Any] = {
        "model_version": PRODUCTION_MODEL_VERSION,
        "dataset_sha256": actual_sha256,
        "dataset_records": len(df),
        "architecture": "MultivariateMonotoneModel + MondrianConformalPredictor",
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "file_hashes": {
            "model.pkl": model_sha256,
            "conformal.pkl": conformal_sha256,
        },
        "allowed_inputs": ["size_fp", "duration_months", "team_size"],
        "banned_features": sorted(list(BANNED_FEATURES)),
        "environment": {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "python_major_minor": f"{sys.version_info.major}.{sys.version_info.minor}",
            "scikit-learn": sklearn.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "model_parameters": {
            "base_marginal": {
                "beta0": estimator.beta0_base_,
                "a": estimator.a_base_,
                "b": estimator.b_base_,
            },
            "multivariate": {
                "beta0": estimator.beta0_,
                "a": estimator.a_,
                "b": estimator.b_,
                "c": estimator.c_,
            },
            "has_duration": estimator.has_duration_,
            "n_valid_duration_train": estimator.n_valid_duration_train_,
        },
        "calibration_spec": {
            "nominal_coverage": 1.0 - alpha,
            "alpha": alpha,
            "score_type": "log_residual",
            "global_quantile": calibrator.global_quantile_,
            "bucket_quantiles": calibrator.bucket_quantiles_,
            "bucket_thresholds": list(SIZE_BUCKET_THRESHOLDS),
            "buckets": list(MONDRIAN_BUCKETS),
            "cal_size": cal_size,
            "random_state": random_state,
        },
    }

    manifest_path = out_path / "manifest.json"
    with manifest_path.open("w", encoding="utf-8") as f_man:
        json.dump(manifest, f_man, indent=2)
        f_man.write("\n")

    manifest_sha256 = compute_file_sha256(manifest_path)
    logger.info("Manifest created: %s (SHA-256=%s)", manifest_path, manifest_sha256)

    return estimator, calibrator, manifest


def main() -> None:
    """CLI entrypoint for production model training and bundling."""
    parser = argparse.ArgumentParser(
        description="Bundle production ML artifacts for PredictIQ v2."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=None,
        help="Path to harmonized projects_v2.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to save production bundle",
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.20,
        help="Conformal calibration significance level (default: 0.20 -> 80% coverage)",
    )
    parser.add_argument(
        "--cal-size",
        type=float,
        default=0.20,
        help="Fraction of data allocated to calibration (default: 0.20)",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for calibration split (default: 42)",
    )

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    _, _, manifest = train_and_bundle_production_model(
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        alpha=args.alpha,
        cal_size=args.cal_size,
        random_state=args.random_state,
    )

    print("\n=== Production ML Bundle Successfully Built ===")
    print(f"Version:      {manifest['model_version']}")
    print(f"Architecture: {manifest['architecture']}")
    print(f"Dataset:      {manifest['dataset_records']} records ({manifest['dataset_sha256'][:16]}...)")
    print(f"Files:        {list(manifest['file_hashes'].keys())}")
    for fname, fhash in manifest["file_hashes"].items():
        print(f"  - {fname}: {fhash}")


if __name__ == "__main__":
    main()
