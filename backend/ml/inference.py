"""
Predictify Production Inference Module v2.0
============================================
Loads trained model at server startup (via FastAPI lifespan).
Provides predict() method used by ml_service.py.
Fails closed if artifacts or inference are invalid.

Updated for 740-project multi-source dataset.
Effort clamp range: 1-9587 hours (matching dataset bounds).

The predictor singleton is loaded once at startup. Artifact failures
disable readiness until the service is restarted or artifacts reloaded.
"""

import json
import logging
import pickle
import warnings
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.exceptions import InconsistentVersionWarning

from ml.artifact_safety import REVOKED_MODEL_SHA256, require_unrevoked

logger = logging.getLogger(__name__)
ML_DIR = Path(__file__).parent

EXPECTED_FEATURES = [
    "TeamExp", "ManagerExp", "duration_months", "Transactions", "Entities",
    "PointsNonAdjust", "Adjustment", "size_fp",
    *[f"T{i:02d}" for i in range(1, 16)],
    "log_size_fp", "complexity_score", "team_skill_avg", "risk_score",
]


class MLUnavailableError(RuntimeError):
    """No trustworthy model prediction can be produced."""


class PredictifyInference:
    """
    Production ML inference engine.

    Loads model artifacts once at startup. Provides predict()
    for concurrent request processing. Runtime failures disable readiness.
    """

    def __init__(self) -> None:
        self.model: Any | None = None
        self.scaler: Any | None = None
        self.feature_names: list[str] | None = None
        self.model_report: dict | None = None
        self.training_report: dict | None = None
        self.is_ready: bool = False
        self.model_name: str = "unknown"
        self.n_features: int = 0

    def load(self, model_path=None, scaler_path=None, feature_path=None) -> bool:
        """
        Load model artifacts from backend/ml/.
        Returns True only for a compatible, complete artifact bundle.
        """
        self.is_ready = False
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_report = None
        self.training_report = None
        self.model_name = "unknown"
        self.n_features = 0

        def artifact_path(value, filename):
            path = Path(value) if value is not None else ML_DIR / filename
            return path if path.is_absolute() else ML_DIR.parent / path

        model_path = artifact_path(model_path, "predictiq_best_model.pkl")
        scaler_path = artifact_path(scaler_path, "predictiq_scaler.pkl")
        feature_path = artifact_path(feature_path, "predictiq_features.json")
        report_path = model_path.parent / "predictiq_model_report.json"
        training_report_path = model_path.parent / "training_report.json"

        missing = [
            p.name for p in [model_path, scaler_path, feature_path]
            if not p.exists()
        ]

        if missing:
            logger.warning(
                "ML artifacts missing: %s. Predictions unavailable. "
                "Run `python backend/ml/train.py` to generate artifacts.",
                missing,
            )
            self.is_ready = False
            return False

        try:
            require_unrevoked(model_path, REVOKED_MODEL_SHA256)
            with warnings.catch_warnings():
                warnings.simplefilter("error", InconsistentVersionWarning)
                with open(model_path, "rb") as model_file:
                    self.model = pickle.load(model_file)
                with open(scaler_path, "rb") as scaler_file:
                    self.scaler = pickle.load(scaler_file)
            with open(feature_path, "r") as feature_file:
                self.feature_names = json.load(feature_file)

            if self.feature_names != EXPECTED_FEATURES:
                raise ValueError("Unsupported feature names or order")
            for artifact in (self.scaler, self.model):
                if getattr(artifact, "n_features_in_", None) != len(EXPECTED_FEATURES):
                    raise ValueError("Artifact feature count mismatch")
                names = getattr(artifact, "feature_names_in_", None)
                if names is not None and list(names) != self.feature_names:
                    raise ValueError("Artifact feature order mismatch")

            if report_path.exists():
                with open(report_path, "r") as f:
                    self.model_report = json.load(f)

            # Load training_report.json (new in v2)
            if training_report_path.exists():
                with open(training_report_path, "r") as f:
                    self.training_report = json.load(f)
            elif self.model_report:
                # Fallback: use model_report as training_report
                self.training_report = self.model_report
            else:
                logger.warning(
                    "training_report.json not found. "
                    "Health endpoint will use hardcoded defaults."
                )

            self.n_features = len(self.feature_names)
            self.model_name = type(self.model).__name__
            if self.training_report:
                if self.training_report.get("n_features", self.n_features) != self.n_features:
                    raise ValueError("Training report feature count mismatch")
                if self.training_report.get("feature_list", self.feature_names) != self.feature_names:
                    raise ValueError("Training report feature order mismatch")
            self.is_ready = True
            # Exercise preprocessing and prediction before advertising readiness.
            self.predict(dict.fromkeys(self.feature_names, 1.0))

            logger.info(
                "ML model loaded: %s | Features: %d | Samples: %s",
                self.model_name, self.n_features,
                self._get_training_samples(),
            )
            return True

        except Exception as e:
            logger.error("Failed to load ML model: %s", e)
            self.is_ready = False
            return False

    def _get_training_samples(self) -> int:
        """Get training sample count from report or default."""
        if self.training_report:
            return self.training_report.get("training_samples", 740)
        if self.model_report:
            ds = self.model_report.get("dataset_shape", [740])
            return ds[0] if isinstance(ds, list) else 740
        return 740

    def predict(self, feature_dict: dict) -> dict:
        """
        Run inference on a feature dictionary.

        Args:
            feature_dict: Keys matching Predictify_features.json.
                          Every trained feature is required and must be finite.

        Returns:
            Dict with effort_hours (min/likely/max),
            confidence_pct, and model_mode.
        """
        if not self.is_ready:
            raise MLUnavailableError("Prediction service is unavailable")

        model_executed = False
        try:
            # Build vector in exact training order
            assert self.feature_names is not None
            if self.scaler is None or self.model is None:
                raise MLUnavailableError("Prediction artifacts are unavailable")
            if set(feature_dict) != set(self.feature_names):
                raise ValueError("Prediction features do not match trained features")
            vector = np.array(
                [float(feature_dict[feat]) for feat in self.feature_names],
                dtype=np.float64,
            ).reshape(1, -1)

            if not np.isfinite(vector).all():
                raise ValueError("Prediction features must be finite")

            # Scale using fitted scaler
            model_executed = True
            vector_scaled = self.scaler.transform(vector)
            if np.shape(vector_scaled) != vector.shape or not np.isfinite(vector_scaled).all():
                raise ValueError("Invalid scaler output")

            # Predict in log space
            prediction = np.asarray(self.model.predict(vector_scaled))
            if prediction.shape != (1,) or not np.isfinite(prediction).all():
                raise ValueError("Invalid model output")
            log_pred = float(prediction[0])
            if log_pred < 0:
                raise ValueError("Model predicted negative effort")

            # Convert back to effort hours
            with np.errstate(over="raise", invalid="raise"):
                effort_likely = float(np.expm1(log_pred))

            # Heuristic scenario bounds, not calibrated confidence intervals.
            effort_min = effort_likely * 0.80
            effort_max = effort_likely * 1.40

            # Clamp to dataset range (1-9587 hours)
            effort_likely = min(max(effort_likely, 1), 9587)
            effort_min = min(max(effort_min, 1), 7670)
            effort_max = min(max(effort_max, 1), 13422)

            # Derive confidence
            confidence = self._estimate_confidence(effort_likely, feature_dict)

            return {
                "effort_hours_likely": round(effort_likely, 1),
                "effort_hours_min": round(effort_min, 1),
                "effort_hours_max": round(effort_max, 1),
                "confidence_pct": confidence,
                "confidence_method": "heuristic_not_calibrated_probability",
                "interval_method": "heuristic_0.8x_1.4x_with_clamps",
                "model_mode": "live",
                "model_name": self.model_name,
                "log_pred": round(log_pred, 4),
            }

        except Exception as e:
            if model_executed:
                self.is_ready = False
            logger.error("Inference failed: %s", type(e).__name__)
            raise MLUnavailableError("Prediction service is unavailable") from e

    def _estimate_confidence(
        self, effort_likely: float, feature_dict: dict
    ) -> float:
        """
        Compute a legacy heuristic score, not a probability of correctness.
        It is not calibrated and does not quantify prediction interval coverage.
        Inputs:
        - Model RÂ² from training report
        - How well features were extracted (non-zero count)
        - Whether size_fp is in training distribution
        """
        # Start with base from model performance
        base_r2 = 0.70
        if self.training_report:
            base_r2 = self.training_report.get("r2_score", 0.70)
        elif self.model_report:
            for result in self.model_report.get("results", []):
                if result.get("Model") == self.model_report.get("best_model"):
                    base_r2 = result.get("R2", 0.70)
                    break

        base_confidence = base_r2 * 100 + 10
        if not np.isfinite(base_confidence):
            raise ValueError("Invalid confidence metadata")

        # Bonus for well-populated feature vectors
        non_zero = sum(
            1 for v in feature_dict.values() if float(v or 0) != 0
        )
        feature_ratio = non_zero / max(self.n_features, 1)
        confidence = base_confidence + (feature_ratio * 12)

        # Bonus if size_fp is within training range
        size_fp = float(feature_dict.get("size_fp", 0))
        if 50 <= size_fp <= 3643:
            confidence += 5
        elif size_fp == 0:
            confidence -= 10

        return round(min(95.0, max(45.0, confidence)), 1)

    def get_feature_importance(self) -> dict:
        """Return top feature importances from the model report."""
        report = self.training_report or self.model_report
        if report:
            return report.get("top_features", {})
        return {}

    def get_model_info(self) -> dict:
        """Return model metadata for health endpoint."""
        info: dict[str, Any] = {
            "model_loaded": self.is_ready,
            "model_mode": "live" if self.is_ready else "unavailable",
            "model_version": "2.0.0",
            "confidence_method": "heuristic_not_calibrated_probability",
            "interval_method": "heuristic_0.8x_1.4x_with_clamps",
        }

        report = self.training_report or self.model_report
        if report:
            info["best_model"] = report.get("best_model", "unknown")
            info["training_samples"] = report.get("training_samples", 740)
            info["n_features"] = report.get("n_features", self.n_features)
            info["r2_score"] = report.get("r2_score", 0.0)
            info["pred25"] = report.get("pred25", 0.0)
            info["mmre"] = report.get("mmre", 0.0)
            info["dataset_sources"] = report.get(
                "dataset_sources",
                ["albrecht", "china", "existing_desharnais_maxwell", "nasa93"]
            )
        else:
            info["best_model"] = self.model_name if self.is_ready else "unavailable"
            info["training_samples"] = 740
            info["n_features"] = self.n_features or 27
            info["r2_score"] = 0.0
            info["pred25"] = 0.0
            info["mmre"] = 0.0
            info["dataset_sources"] = []
        return info


# Module-level singleton -- import this from anywhere
predictor = PredictifyInference()

