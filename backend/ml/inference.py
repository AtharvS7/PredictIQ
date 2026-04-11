"""
PredictIQ Production Inference Module v2.0
============================================
Loads trained model at server startup (via FastAPI lifespan).
Provides predict() method used by ml_service.py.
Falls back to demo mode if pkl artifacts are missing.

Updated for 740-project multi-source dataset.
Effort clamp range: 1-9587 hours (matching dataset bounds).

Thread-safe: the predictor singleton is loaded once at startup
and is read-only during request processing.
"""

import pickle
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional, Any

logger = logging.getLogger(__name__)
ML_DIR = Path(__file__).parent

# Demo-mode plausible predictions keyed by size_fp bucket
_DEMO_EFFORT_LOOKUP: dict[str, dict[str, float]] = {
    "small":  {"likely": 800,  "min": 640,  "max": 1120},
    "medium": {"likely": 2500, "min": 2000, "max": 3500},
    "large":  {"likely": 5000, "min": 4000, "max": 7000},
    "xlarge": {"likely": 8000, "min": 6400, "max": 9587},
}


class PredictIQInference:
    """
    Production ML inference engine.

    Loads model artifacts once at startup. Provides predict()
    for concurrent request processing without locks (read-only).
    """

    def __init__(self) -> None:
        self.model: Optional[Any] = None
        self.scaler: Optional[Any] = None
        self.feature_names: Optional[list[str]] = None
        self.model_report: Optional[dict] = None
        self.training_report: Optional[dict] = None
        self.is_ready: bool = False
        self.model_name: str = "unknown"
        self.n_features: int = 0

    def load(self) -> bool:
        """
        Load model artifacts from backend/ml/.
        Returns True if loaded successfully, False → demo mode.
        """
        model_path = ML_DIR / "predictiq_best_model.pkl"
        scaler_path = ML_DIR / "predictiq_scaler.pkl"
        feature_path = ML_DIR / "predictiq_features.json"
        report_path = ML_DIR / "predictiq_model_report.json"
        training_report_path = ML_DIR / "training_report.json"

        missing = [
            p.name for p in [model_path, scaler_path, feature_path]
            if not p.exists()
        ]

        if missing:
            logger.warning(
                "ML artifacts missing: %s. Running in DEMO MODE. "
                "Run `python backend/ml/train.py` to generate artifacts.",
                missing,
            )
            self.is_ready = False
            return False

        try:
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
            with open(scaler_path, "rb") as f:
                self.scaler = pickle.load(f)
            with open(feature_path, "r") as f:
                self.feature_names = json.load(f)

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
            self.is_ready = True

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
            feature_dict: Keys matching predictiq_features.json.
                          Missing keys are zero-filled.

        Returns:
            Dict with effort_hours (min/likely/max),
            confidence_pct, and model_mode.
        """
        if not self.is_ready:
            return self._demo_predict(feature_dict)

        try:
            # Build vector in exact training order
            assert self.feature_names is not None
            vector = np.array(
                [float(feature_dict.get(feat, 0.0)) for feat in self.feature_names],
                dtype=np.float64,
            ).reshape(1, -1)

            # Replace any inf/-inf/nan
            vector = np.nan_to_num(vector, nan=0.0, posinf=0.0, neginf=0.0)

            # Scale using fitted scaler
            vector_scaled = self.scaler.transform(vector)

            # Predict in log space
            log_pred = float(self.model.predict(vector_scaled)[0])

            # Convert back to effort hours
            effort_likely = float(np.expm1(log_pred))

            # Confidence intervals -- asymmetric (conservative side wider)
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
                "model_mode": "live",
                "model_name": self.model_name,
                "log_pred": round(log_pred, 4),
            }

        except Exception as e:
            logger.error("Inference error: %s", e)
            return self._demo_predict(feature_dict)

    def _estimate_confidence(
        self, effort_likely: float, feature_dict: dict
    ) -> float:
        """
        Estimate prediction confidence based on:
        - Model R² from training report
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

    def _demo_predict(self, feature_dict: dict) -> dict:
        """
        Demo mode: return realistic values based on size_fp.
        Used when model artifacts are absent.
        """
        size_fp = float(feature_dict.get("size_fp", 150))

        if size_fp <= 100:
            bucket = "small"
        elif size_fp <= 300:
            bucket = "medium"
        elif size_fp <= 600:
            bucket = "large"
        else:
            bucket = "xlarge"

        effort = _DEMO_EFFORT_LOOKUP[bucket]
        return {
            "effort_hours_likely": float(effort["likely"]),
            "effort_hours_min": float(effort["min"]),
            "effort_hours_max": float(effort["max"]),
            "confidence_pct": 60.0,
            "model_mode": "demo",
            "model_name": "DemoMode",
            "log_pred": float(np.log1p(effort["likely"])),
        }

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
            "model_mode": "live" if self.is_ready else "demo",
            "model_version": "2.0.0",
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
            info["best_model"] = self.model_name if self.is_ready else "DemoMode"
            info["training_samples"] = 740
            info["n_features"] = self.n_features or 27
            info["r2_score"] = 0.0
            info["pred25"] = 0.0
            info["mmre"] = 0.0
            info["dataset_sources"] = []
        return info


# Module-level singleton -- import this from anywhere
predictor = PredictIQInference()
