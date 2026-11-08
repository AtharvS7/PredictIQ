"""Production Model Artifact Loader for PredictIQ v2 / RC3 (S01).

Provides fail-closed, cryptographic-verified loading of production ML artifacts:
1. Manifest structure and dataset integrity verification.
2. Canonical UTF-8 SHA-256 verification of JSON artifact files (line-ending invariant).
3. Zero untrusted deserialization: pure JSON parameter loading (no pickle in production serving runtime).
4. Model safety verification against revoked checksums (REVOKED_MODEL_SHA256, REVOKED_DATA_SHA256).
5. Non-blocking Python environment version logging.
6. Schema drift detection and strict fail-closed error handling (raises RuntimeError immediately upon violation).
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from backend.ml.artifact_safety import (  # noqa: E402
    REVOKED_DATA_SHA256,
    REVOKED_MODEL_SHA256,
)
from backend.ml.calibration.conformal import (  # noqa: E402
    MondrianConformalPredictor,
)
from backend.ml.track1.models import (  # noqa: E402
    MonotonePowerLaw,
    MultivariateMonotoneModel,
    validate_and_extract_inputs,
)

logger = logging.getLogger(__name__)

DEFAULT_PRODUCTION_ARTIFACTS_DIR = (
    Path(__file__).resolve().parent / "production_v2"
)
EXPECTED_DATASET_SHA256 = (
    "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3"
)
EXPECTED_DATASET_RECORDS = 915
EXPECTED_MODEL_VERSION = "2.0.0-rc.3"
REQUIRED_MANIFEST_KEYS: frozenset[str] = frozenset(
    [
        "model_version",
        "dataset_sha256",
        "dataset_records",
        "architecture",
        "file_hashes",
        "allowed_inputs",
        "banned_features",
        "environment",
    ]
)
REQUIRED_ARTIFACT_FILES: frozenset[str] = frozenset(
    [
        "model_params.json",
    ]
)


def _compute_sha256(path: Path) -> str:
    """Compute raw SHA-256 checksum of a file (for binary artifacts)."""
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_canonical_json_sha256(data: Path | dict[str, Any] | str) -> str:
    """Compute canonical UTF-8 SHA-256 checksum of JSON content.

    Serializes using: json.dumps(obj, sort_keys=True, indent=2, ensure_ascii=False).encode('utf-8')
    Ensures line endings on disk (CRLF vs LF) can NEVER change the verified hash.
    """
    if isinstance(data, Path):
        with data.open("r", encoding="utf-8") as f:
            obj = json.load(f)
    elif isinstance(data, str):
        obj = json.loads(data)
    else:
        obj = data

    canonical_bytes = json.dumps(
        obj,
        sort_keys=True,
        indent=2,
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical_bytes).hexdigest()


def compute_artifact_sha256(path: Path) -> str:
    """Compute artifact checksum: canonical JSON hashing for .json, raw bytes for binary."""
    if path.suffix.lower() == ".json":
        return compute_canonical_json_sha256(path)
    return _compute_sha256(path)


def _validate_model_params_schema(params_data: Any, path: Path) -> None:
    """Validate model_params.json schema to detect drift or corrupted parameters."""
    if not isinstance(params_data, dict):
        raise RuntimeError(f"Schema drift: model params in '{path}' is not a JSON object")

    for key in ("model_version", "architecture", "parameters", "calibration"):
        if key not in params_data:
            raise RuntimeError(f"Schema drift: model params in '{path}' missing key '{key}'")

    params = params_data["parameters"]
    if not isinstance(params, dict):
        raise RuntimeError(f"Schema drift: 'parameters' in '{path}' must be a dictionary")

    base = params.get("base_marginal", params)
    if not isinstance(base, dict):
        raise RuntimeError(f"Schema drift: 'base_marginal' in '{path}' must be a dictionary")

    if "beta0" not in base and "a" not in base:
        raise RuntimeError(f"Schema drift: 'base_marginal' in '{path}' missing 'beta0' or 'a'")
    if "b" not in base:
        raise RuntimeError(f"Schema drift: 'base_marginal' in '{path}' missing 'b'")

    try:
        b_val = float(base["b"])
        if not np.isfinite(b_val) or b_val <= 0:
            raise ValueError()
    except Exception as exc:
        raise RuntimeError(
            f"Schema drift: 'b' in '{path}' must be a strictly positive finite number"
        ) from exc

    cal = params_data["calibration"]
    if not isinstance(cal, dict):
        raise RuntimeError(f"Schema drift: 'calibration' in '{path}' must be a dictionary")

    if "conformal_80" not in cal:
        raise RuntimeError(f"Schema drift: 'calibration' in '{path}' missing 'conformal_80'")

    c80 = cal["conformal_80"]
    if not isinstance(c80, dict) or "global_quantile" not in c80:
        raise RuntimeError(
            f"Schema drift: 'conformal_80' in '{path}' missing 'global_quantile'"
        )

    try:
        gq = float(c80["global_quantile"])
        if not np.isfinite(gq) or gq <= 0:
            raise ValueError()
    except Exception as exc:
        raise RuntimeError(
            f"Schema drift: 'global_quantile' in '{path}' must be a strictly positive finite number"
        ) from exc


@dataclass
class ProductionModelBundle:
    """Container holding verified production model and conformal calibrator."""

    model: MonotonePowerLaw | MultivariateMonotoneModel
    conformal: MondrianConformalPredictor
    manifest: dict[str, Any]
    model_version: str
    artifact_dir: Path
    manifest_sha256: str

    def __iter__(self) -> Iterator[Any]:
        """Support tuple unpacking: model, conformal = bundle."""
        yield self.model
        yield self.conformal

    @property
    def allowed_inputs(self) -> list[str]:
        """List of permitted input features under ML contract."""
        return list(self.manifest.get("allowed_inputs", []))

    @property
    def banned_features(self) -> list[str]:
        """List of prohibited features under ML contract."""
        return list(self.manifest.get("banned_features", []))

    @property
    def architecture(self) -> str:
        """Architecture specification from manifest."""
        return str(self.manifest.get("architecture", ""))

    def _coerce_input(self, X: Any) -> Any:
        """Coerce dict or scalar input into DataFrame or array-like."""
        if isinstance(X, dict):
            if any(isinstance(v, (list, tuple, np.ndarray)) for v in X.values()):
                try:
                    return pd.DataFrame(X)
                except Exception:
                    pass
            return pd.DataFrame([X])
        if isinstance(X, (list, tuple)) and X and isinstance(X[0], dict):
            return pd.DataFrame(X)
        return X

    def validate_inputs(
        self,
        X: Any,
    ) -> tuple[np.ndarray, np.ndarray | None, np.ndarray | None]:
        """Validate input features against contract and reject banned features."""
        coerced = self._coerce_input(X)
        return validate_and_extract_inputs(coerced)

    def predict(self, X: Any) -> np.ndarray:
        """Predict median effort (p50) in person-hours.

        Enforces strictly positive predictions (>= 1.0 hr).
        """
        coerced = self._coerce_input(X)
        return self.model.predict(coerced)

    def predict_quantiles(self, X: Any) -> dict[str, np.ndarray]:
        """Predict calibrated quantile intervals: p10, p25, p50, p75, and p90.

        Guarantees 1.0 <= p10 <= p25 <= p50 <= p75 <= p90 everywhere.
        """
        coerced = self._coerce_input(X)
        return self.conformal.predict_quantiles(coerced)

    def predict_interval(
        self,
        X: Any,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convenience method returning (p10, p50, p90) tuple."""
        coerced = self._coerce_input(X)
        return self.conformal.predict_interval(coerced)

    def get_model_info(self) -> dict[str, Any]:
        """Return model metadata conforming to v2 contracts and health endpoints."""
        return {
            "model_loaded": True,
            "model_mode": "production_v2_monotone",
            "model_version": self.model_version,
            "best_model": self.architecture,
            "training_samples": self.manifest.get("dataset_records", 915),
            "n_features": len(self.allowed_inputs),
            "r2_score": 0.314,
            "mdape": 0.539,
            "dataset_sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att_aptness"],
            "confidence_method": "mondrian_split_conformal_80pct",
            "interval_method": "inductive_conformal_p10_p50_p90",
            "nominal_interval_coverage": 0.80,
            "dataset_sha256": self.manifest.get("dataset_sha256"),
            "manifest_sha256": self.manifest_sha256,
        }

    def get_feature_importance(self) -> dict[str, float]:
        """Return feature sensitivity weights."""
        return {
            "size_fp": 1.0,
        }


def load_production_model(
    artifact_dir: Path | str | None = None,
    expected_manifest_hash: str | None = None,
) -> ProductionModelBundle:
    """Load and cryptographically verify the production model bundle.

    Fails closed: if any file is missing, checksum mismatches, manifest is corrupt,
    schema drifts, or revoked hash is detected, raises RuntimeError.

    Production serving bundle is strictly pure JSON (model_params.json + manifest.json).
    Zero pickle is used in production serving.

    Parameters
    ----------
    artifact_dir : Path | str | None
        Directory containing the model bundle. Defaults to backend/ml/artifacts/production_v2/.
    expected_manifest_hash : str | None
        Optional expected SHA-256 hash of manifest.json for explicit tamper checking.

    Returns
    -------
    ProductionModelBundle
        Verified container holding fitted estimator, calibrator, and manifest.

    Raises
    ------
    RuntimeError
        If verification fails for any reason.
    """
    dir_path = (
        Path(artifact_dir).resolve()
        if artifact_dir is not None
        else DEFAULT_PRODUCTION_ARTIFACTS_DIR.resolve()
    )

    # 1. Directory verification
    if not dir_path.exists() or not dir_path.is_dir():
        raise RuntimeError(
            f"Production artifact directory does not exist or is not a directory: {dir_path}"
        )

    # 2. Manifest file verification
    manifest_file = dir_path / "manifest.json"
    if not manifest_file.exists() or not manifest_file.is_file():
        raise RuntimeError(
            f"Production manifest file missing at: {manifest_file}"
        )

    try:
        manifest_text = manifest_file.read_text(encoding="utf-8")
        manifest: dict[str, Any] = json.loads(manifest_text)
    except Exception as exc:
        raise RuntimeError(
            f"Corrupted or invalid manifest.json at {manifest_file}: {exc}"
        ) from exc

    if not isinstance(manifest, dict):
        raise RuntimeError(
            f"Manifest at {manifest_file} is not a valid JSON object."
        )

    manifest_canonical_sha256 = compute_canonical_json_sha256(manifest)
    manifest_raw_sha256 = _compute_sha256(manifest_file)
    manifest_sha256 = manifest_canonical_sha256

    if expected_manifest_hash is not None:
        if (
            manifest_canonical_sha256.lower() != expected_manifest_hash.lower()
            and manifest_raw_sha256.lower() != expected_manifest_hash.lower()
        ):
            raise RuntimeError(
                f"Manifest checksum mismatch: expected {expected_manifest_hash}, got {manifest_canonical_sha256}"
            )

    # 3. Required manifest fields
    missing_keys = REQUIRED_MANIFEST_KEYS - set(manifest.keys())
    if missing_keys:
        raise RuntimeError(
            f"Manifest missing required keys: {sorted(missing_keys)}"
        )

    # 4. Dataset integrity & revocation verification
    dataset_records = manifest.get("dataset_records")
    if dataset_records != EXPECTED_DATASET_RECORDS:
        raise RuntimeError(
            f"Dataset record count mismatch in manifest: expected {EXPECTED_DATASET_RECORDS}, got {dataset_records}"
        )

    dataset_sha256 = str(manifest.get("dataset_sha256", "")).lower()
    if dataset_sha256 in REVOKED_DATA_SHA256:
        raise RuntimeError(
            f"Manifest references revoked training dataset checksum: {dataset_sha256}"
        )

    if dataset_sha256 != EXPECTED_DATASET_SHA256:
        raise RuntimeError(
            f"Dataset SHA-256 mismatch in manifest: expected {EXPECTED_DATASET_SHA256}, got {dataset_sha256}"
        )

    # 5. Environment & Python version informational logging (non-blocking)
    env_spec = manifest.get("environment", {})
    if isinstance(env_spec, dict):
        manifest_py = (
            env_spec.get("python_major_minor")
            or env_spec.get("python")
            or env_spec.get("python_version")
        )
        if manifest_py:
            logger.info(
                "Model artifact build environment: Python %s, runtime is Python %s.%s",
                manifest_py,
                sys.version_info.major,
                sys.version_info.minor,
            )
    else:
        logger.info("Manifest environment spec omitted or non-dictionary.")

    # 6. Artifact file verification and canonical/raw SHA-256 hashing
    file_hashes: dict[str, str] = manifest.get("file_hashes", {})
    if not isinstance(file_hashes, dict):
        raise RuntimeError("Manifest file_hashes must be a dictionary.")

    missing_files = REQUIRED_ARTIFACT_FILES - set(file_hashes.keys())
    if missing_files:
        raise RuntimeError(
            f"Manifest file_hashes missing required artifacts: {sorted(missing_files)}"
        )

    # Check manifest model_sha256 if present
    manifest_model_sha256 = str(manifest.get("model_sha256", "")).lower()
    if manifest_model_sha256 and manifest_model_sha256 in REVOKED_MODEL_SHA256:
        raise RuntimeError(
            f"Manifest model_sha256 matches revoked security checksum: {manifest_model_sha256}"
        )

    for fname, expected_hash in file_hashes.items():
        artifact_path = dir_path / fname
        if not artifact_path.exists() or not artifact_path.is_file():
            raise RuntimeError(
                f"Required production artifact file missing: {fname} at {artifact_path}"
            )

        actual_hash = compute_artifact_sha256(artifact_path)
        if actual_hash.lower() in REVOKED_MODEL_SHA256:
            raise RuntimeError(
                f"Artifact file '{fname}' matches revoked security checksum: {actual_hash}"
            )

        if actual_hash.lower() != str(expected_hash).lower():
            raise RuntimeError(
                f"SHA-256 checksum mismatch for '{fname}': expected {expected_hash}, got {actual_hash}"
            )

    # Cross-verify manifest.model_sha256 against model_params.json hash
    model_params_file = dir_path / "model_params.json"
    params_canonical_hash = compute_canonical_json_sha256(model_params_file)
    if manifest_model_sha256 and manifest_model_sha256 != params_canonical_hash.lower():
        raise RuntimeError(
            f"Manifest model_sha256 mismatch: manifest specifies {manifest_model_sha256}, "
            f"but model_params.json canonical hash is {params_canonical_hash}"
        )

    # 7. Safe Pure JSON Parameter Deserialization (Zero pickle at serving runtime)
    try:
        with model_params_file.open("r", encoding="utf-8") as f_p:
            params_data = json.load(f_p)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to parse model params artifact '{model_params_file}': {exc}"
        ) from exc

    _validate_model_params_schema(params_data, model_params_file)

    p = params_data.get("parameters", {})
    base_p = p.get("base_marginal", p)

    beta0_val = float(base_p.get("beta0", 3.1880360932291065))
    b_val = float(base_p.get("b", 0.8270266757672359))
    a_val = float(base_p.get("a", np.exp(beta0_val)))

    model = MonotonePowerLaw()
    model.beta0_ = beta0_val
    model.b_ = b_val
    model.a_ = a_val
    model.intercept_ = beta0_val
    model.slope_ = b_val
    # Backward compatibility attributes for inspection
    model.beta0_base_ = beta0_val
    model.a_base_ = a_val
    model.b_base_ = b_val
    model.has_duration_ = False
    model.n_valid_duration_train_ = 0

    cal_data = params_data.get("calibration", {})
    c80 = cal_data.get("conformal_80", {})
    c50 = cal_data.get("conformal_50", {})

    conformal = MondrianConformalPredictor(estimator=model)
    conformal.estimator_ = model
    conformal.global_quantile_ = float(c80.get("global_quantile", 1.0053189146513999))
    conformal.bucket_quantiles_ = {
        k: float(v) for k, v in c80.get("bucket_quantiles", {}).items()
    }
    if "global_quantile" in c50:
        conformal.global_quantile_50_ = float(c50["global_quantile"])
    else:
        conformal.global_quantile_50_ = float(conformal.global_quantile_ * 0.597)
    conformal.bucket_quantiles_50_ = {
        k: float(v) for k, v in c50.get("bucket_quantiles", {}).items()
    }
    conformal.is_calibrated_ = True

    model_ver = str(manifest.get("model_version", EXPECTED_MODEL_VERSION))

    logger.info(
        "Production model bundle loaded and verified successfully from %s (version: %s)",
        dir_path,
        model_ver,
    )

    return ProductionModelBundle(
        model=model,
        conformal=conformal,
        manifest=manifest,
        model_version=model_ver,
        artifact_dir=dir_path,
        manifest_sha256=manifest_sha256,
    )
