"""
PredictIQ ML Serving Service v2 (CP14)
=====================================
Bridges FastAPI estimation endpoints with verified production ML artifacts.
Strictly conforms to ML Contract v2.0:
- Permitted inputs: size_fp, duration_months, team_size
- Strictly forbidden: T01-T15, Transactions, Entities, TeamExp, ManagerExp
- Quantile predictions: p10, p50, p90 (effort hours and person-months)
- Conformal calibration and Out-of-Distribution (OOD) diagnostics
- Data Quality Tiers: A (User/Empirical), B (NLP/Extrapolated), C (OOD/Uncertain)
"""

from __future__ import annotations

from typing import Any

import numpy as np
import structlog
from fastapi import HTTPException

from backend.ml.artifacts.loader import ProductionModelBundle, load_production_model

logger = structlog.get_logger()

# Standard software engineering productivity conversion
HOURS_PER_PERSON_MONTH = 152.0

# Empirical dataset bounds from projects_v2.csv
DATASET_MIN_FP = 4.0
DATASET_MAX_FP = 4100.0


class MLService:
    """Handles production ML inference and uncertainty estimation."""

    def __init__(self, bundle: ProductionModelBundle | None = None) -> None:
        self._bundle: ProductionModelBundle | None = bundle

    @property
    def bundle(self) -> ProductionModelBundle:
        """Lazily load and verify production model bundle."""
        if self._bundle is None:
            try:
                self._bundle = load_production_model()
            except Exception as exc:
                logger.error("ml_service_load_failed", error=str(exc))
                raise HTTPException(
                    status_code=503,
                    detail="Prediction service is unavailable: ML artifacts failed verification",
                ) from exc
        return self._bundle

    def is_ready(self) -> bool:
        """Check if production model is verified and operational."""
        try:
            return self.bundle is not None
        except Exception:
            return False

    def get_model_info(self) -> dict[str, Any]:
        """Return model metadata for health/monitoring endpoints."""
        if not self.is_ready():
            return {
                "model_loaded": False,
                "model_mode": "unavailable",
                "model_version": None,
                "error": "Model bundle unavailable or failed verification",
            }
        return self.bundle.get_model_info()

    def predict(self, params: dict[str, Any]) -> dict[str, Any]:
        """
        Run calibrated effort estimation conforming to ML Contract v2.0.

        Args:
            params: Dictionary containing project parameters:
                - size_fp (float, required)
                - duration_months (float, optional)
                - team_size (int, optional)
                - project_name, project_type, hourly_rate_usd, etc.

        Returns:
            Dictionary with calibrated quantiles, data quality tier,
            OOD flags, and backwards-compatible legacy fields.
        """
        # 1. Extract and flatten parameters
        flat: dict[str, Any] = {}
        for k, v in params.items():
            if isinstance(v, dict) and "value" in v:
                flat[k] = v["value"]
            else:
                flat[k] = v

        # 2. Extract and validate size_fp
        size_source = "user"
        if isinstance(params.get("size_fp"), dict) and "source" in params["size_fp"]:
            size_source = params["size_fp"]["source"]
        elif flat.get("size_source") in ("nlp", "user"):
            size_source = flat["size_source"]
        size_fp_val = flat.get("size_fp")
        if size_fp_val is None:
            # Check NLP derivation fallback
            fc = flat.get("feature_count")
            if fc is not None and float(fc) > 0:
                integ = flat.get("integration_count", 2) or 2
                size_fp_val = float(fc) * 8.0 + float(integ) * 5.0
                size_source = "nlp"
            else:
                size_fp_val = 150.0
                size_source = "default"

        try:
            size_fp = float(size_fp_val)
        except (ValueError, TypeError) as exc:
            raise HTTPException(
                status_code=422,
                detail="Project size (size_fp) must be a valid number",
            ) from exc

        if not np.isfinite(size_fp) or size_fp <= 0:
            raise HTTPException(
                status_code=422,
                detail="Project size (size_fp) must be strictly positive and finite",
            )

        # 3. Optional covariates
        duration_months: float | None = None
        if flat.get("duration_months") is not None:
            try:
                dm = float(flat["duration_months"])
                if np.isfinite(dm) and dm > 0:
                    duration_months = dm
            except (ValueError, TypeError):
                pass

        team_size: int | None = None
        if flat.get("team_size") is not None:
            try:
                ts = int(flat["team_size"])
                if ts >= 1:
                    team_size = ts
            except (ValueError, TypeError):
                pass

        # 4. Out-of-Distribution (OOD) Diagnostics
        ood_flags: list[str] = []
        if size_fp < DATASET_MIN_FP:
            ood_flags.append(f"size_fp_below_training_min ({size_fp:.1f} < {DATASET_MIN_FP})")
        elif size_fp > DATASET_MAX_FP:
            ood_flags.append(f"size_fp_exceeds_training_max ({size_fp:.1f} > {DATASET_MAX_FP})")

        if duration_months is not None:
            if duration_months < 1.0 or duration_months > 60.0:
                ood_flags.append(f"duration_months_extreme ({duration_months:.1f} mo)")

        if team_size is not None:
            if team_size < 1 or team_size > 50:
                ood_flags.append(f"team_size_extreme ({team_size} people)")

        # 5. Data Quality Tier
        if ood_flags or size_fp > DATASET_MAX_FP:
            tier = "C"
        elif size_source == "nlp":
            nlp_conf = (
                params.get("feature_count", {}).get("confidence", 0.6)
                if isinstance(params.get("feature_count"), dict)
                else 0.6
            )
            tier = "B" if nlp_conf >= 0.50 else "C"
        else:
            tier = "A"

        # 6. Execute ML prediction through verified production bundle
        input_data: dict[str, Any] = {"size_fp": size_fp}
        if duration_months is not None:
            input_data["duration_months"] = duration_months
        if team_size is not None:
            input_data["team_size"] = team_size

        try:
            quantiles = self.bundle.predict_quantiles(input_data)
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Inference error: {exc}",
            ) from exc
        except Exception as exc:
            logger.error("inference_execution_failed", error=str(exc))
            raise HTTPException(
                status_code=503,
                detail="Prediction service runtime failure",
            ) from exc

        effort_p10 = float(quantiles["p10"][0])
        effort_p50 = float(quantiles["p50"][0])
        effort_p90 = float(quantiles["p90"][0])

        # Strict non-crossing guarantee: 1.0 <= p10 <= p50 <= p90
        effort_p10 = max(1.0, effort_p10)
        effort_p50 = max(effort_p10, effort_p50)
        effort_p90 = max(effort_p50, effort_p90)

        # Person-months at 152 hrs/PM
        pm_p10 = round(effort_p10 / HOURS_PER_PERSON_MONTH, 2)
        pm_p50 = round(effort_p50 / HOURS_PER_PERSON_MONTH, 2)
        pm_p90 = round(effort_p90 / HOURS_PER_PERSON_MONTH, 2)

        # Size uncertainty
        if size_source == "nlp":
            size_p10 = round(0.85 * size_fp, 1)
            size_p50 = round(size_fp, 1)
            size_p90 = round(1.15 * size_fp, 1)
        else:
            size_p10 = round(size_fp, 1)
            size_p50 = round(size_fp, 1)
            size_p90 = round(size_fp, 1)

        manifest = self.bundle.manifest
        result = {
            # Legacy fields for backward compatibility
            "effort_hours_likely": round(effort_p50, 1),
            "effort_hours_min": round(effort_p10, 1),
            "effort_hours_max": round(effort_p90, 1),
            "confidence_pct": 80.0,
            "model_mode": "production_v2_monotone",
            "model_version": self.bundle.model_version,

            # v2 Contract fields
            "effort_hours": {
                "p10": round(effort_p10, 1),
                "p50": round(effort_p50, 1),
                "p90": round(effort_p90, 1),
            },
            "person_months": {
                "p10": pm_p10,
                "p50": pm_p50,
                "p90": pm_p90,
            },
            "size": {
                "value": round(size_fp, 1),
                "source": size_source,
                "uncertainty": {
                    "p10": size_p10,
                    "p50": size_p50,
                    "p90": size_p90,
                },
            },
            "data_quality_tier": tier,
            "ood_flags": ood_flags,
            "model": {
                "version": self.bundle.model_version,
                "sha256": manifest.get("dataset_sha256", ""),
                "trained_on_rows": manifest.get("dataset_records", 915),
                "sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att"],
                "metrics_ref": "docs/evidence/model_validation_summary.md",
            },
        }

        logger.info(
            "ml_prediction_v2_complete",
            size_fp=size_fp,
            p50_effort=effort_p50,
            tier=tier,
            ood_count=len(ood_flags),
        )
        return result


ml_service = MLService()
