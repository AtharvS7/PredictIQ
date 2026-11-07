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

try:
    from backend.ml.artifacts.loader import ProductionModelBundle, load_production_model
except ModuleNotFoundError:
    from ml.artifacts.loader import ProductionModelBundle, load_production_model

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

    def get_model_native_explanation(
        self, params: dict[str, Any] | None = None, effort_hours: float = 0.0
    ) -> dict[str, Any]:
        """Return model-native explanation including fitted elasticities and calibration bucket quantiles."""
        manifest = self.bundle.manifest
        model_params = manifest.get("model_parameters", {})
        base = model_params.get("base_marginal", {})
        cal_spec = manifest.get("calibration_spec", {})

        size_b = base.get("b", 0.827)
        bucket_quantiles = cal_spec.get("bucket_quantiles", {})

        return {
            "model_version": self.bundle.model_version,
            "architecture": self.bundle.architecture,
            "size_elasticity_b": round(float(size_b), 4),
            "duration_elasticity_c": None,  # Strictly size-only point estimate per R03 frozen decision
            "bucket_quantiles": bucket_quantiles,
            "dataset_records": manifest.get("dataset_records", 915),
        }

    def get_model_explanation_text(self, params: dict[str, Any], effort_hours: float) -> str:
        """Generate human-readable model explanation using real model parameters."""
        size_fp = params.get("size_fp", 0)
        if isinstance(size_fp, dict):
            size_fp = size_fp.get("value", 0)
        size_fp = float(size_fp or 0)

        expl = self.get_model_native_explanation(params, effort_hours)
        b = expl["size_elasticity_b"]

        text = (
            f"The estimated effort of {effort_hours:,.0f} hours is produced by a monotone power-law model "
            f"(version {expl['model_version']}) trained on {expl['dataset_records']} empirical software projects. "
            f"Effort scales with functional size at an elasticity of b={b:.3f}."
        )
        if params.get("duration_months"):
            text += " Planned duration is used for schedule and timeline planning; it does not alter raw effort estimates."
        return text

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
                raise HTTPException(
                    status_code=422,
                    detail="Project size (size_fp) is required. Provide size_fp or requirements/features for estimation.",
                )

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
        elif size_source in ("nlp", "default"):
            nlp_conf = (
                params.get("feature_count", {}).get("confidence", 0.6)
                if isinstance(params.get("feature_count"), dict)
                else 0.6
            )
            tier = "B" if nlp_conf >= 0.50 else "C"
        else:
            tier = "A"

        # 6. Execute ML prediction through verified production bundle
        # Model input is strictly size-only per frozen R03 decision rule
        input_data: dict[str, Any] = {"size_fp": size_fp}

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
        effort_p25 = float(quantiles.get("p25", [effort_p10])[0])
        effort_p75 = float(quantiles.get("p75", [effort_p90])[0])

        # Size uncertainty
        if size_source == "nlp":
            size_p10 = round(0.85 * size_fp, 1)
            size_p50 = round(size_fp, 1)
            size_p90 = round(1.15 * size_fp, 1)
        elif isinstance(params.get("size_fp"), dict) and "uncertainty" in params["size_fp"]:
            unc = params["size_fp"]["uncertainty"]
            size_p10 = float(unc.get("p10", size_fp))
            size_p50 = float(unc.get("p50", size_fp))
            size_p90 = float(unc.get("p90", size_fp))
        else:
            size_p10 = round(size_fp, 1)
            size_p50 = round(size_fp, 1)
            size_p90 = round(size_fp, 1)

        # Propagate size uncertainty into effort intervals (R04, R08)
        if size_p10 > 0 and size_p90 > size_p10 and (size_p10 < size_fp or size_p90 > size_fp):
            # Log-space variance combination: Var(ln E) ~= b^2 * Var(ln S) + Var(residuals)
            b = float(self.get_model_native_explanation().get("size_elasticity_b", 0.827))
            delta_s = 0.5 * (np.log(size_p90) - np.log(size_p10))
            delta_e_size = b * delta_s

            # Outer 80% conformal band combination
            q80_model = 0.5 * (np.log(effort_p90) - np.log(effort_p10))
            q80_combined = float(np.sqrt(q80_model**2 + delta_e_size**2))

            effort_p10 = effort_p50 * np.exp(-q80_combined)
            effort_p90 = effort_p50 * np.exp(q80_combined)

            # Inner 50% likely band combination
            q50_model = 0.5 * (np.log(effort_p75) - np.log(effort_p25))
            q50_combined = float(np.sqrt(q50_model**2 + (0.526 * delta_e_size)**2))

            effort_p25 = effort_p50 * np.exp(-q50_combined)
            effort_p75 = effort_p50 * np.exp(q50_combined)

        # Empirical-Bayes shrinkage to organization actuals (R05)
        # Evaluated in R05: Relative MdAPE gain = 11.9% at k=3, 14.9% at k=5, 19.5% at k=10
        org_calibration = {
            "applied": False,
            "k_actuals": 0,
            "shrinkage_weight": 0.0,
            "multiplier": 1.0,
        }
        actuals = params.get("org_actuals") or flat.get("org_actuals")
        if actuals and isinstance(actuals, list):
            valid_actuals = [
                a for a in actuals
                if isinstance(a, dict)
                and float(a.get("size_fp", 0) or 0) > 0
                and float(a.get("effort_hours", 0) or 0) > 0
            ]
            k_count = len(valid_actuals)
            if k_count > 0:
                # Variance ratio sigma^2 / tau^2 from 6-fold cross-validation
                PRIOR_RATIO = 2.83
                w_k = float(k_count / (k_count + PRIOR_RATIO))

                residuals = []
                for act in valid_actuals:
                    s_act = float(act["size_fp"])
                    e_act = float(act["effort_hours"])
                    pred_act = float(self.bundle.predict_quantiles({"size_fp": s_act})["p50"][0])
                    residuals.append(np.log(e_act) - np.log(pred_act))

                mean_res = float(np.mean(residuals))
                gamma_org = float(np.exp(w_k * mean_res))
                gamma_org = float(np.clip(gamma_org, 0.33, 3.0))

                effort_p10 *= gamma_org
                effort_p25 *= gamma_org
                effort_p50 *= gamma_org
                effort_p75 *= gamma_org
                effort_p90 *= gamma_org

                org_calibration = {
                    "applied": True,
                    "k_actuals": k_count,
                    "shrinkage_weight": round(w_k, 3),
                    "multiplier": round(gamma_org, 3),
                }

        # Strict non-crossing guarantee: 1.0 <= p10 <= p25 <= p50 <= p75 <= p90
        effort_p10 = max(1.0, float(effort_p10))
        effort_p25 = max(effort_p10, float(effort_p25))
        effort_p50 = max(effort_p25, float(effort_p50))
        effort_p75 = max(effort_p50, float(effort_p75))
        effort_p90 = max(effort_p75, float(effort_p90))

        # Person-months at 152 hrs/PM
        pm_p10 = round(effort_p10 / HOURS_PER_PERSON_MONTH, 2)
        pm_p25 = round(effort_p25 / HOURS_PER_PERSON_MONTH, 2)
        pm_p50 = round(effort_p50 / HOURS_PER_PERSON_MONTH, 2)
        pm_p75 = round(effort_p75 / HOURS_PER_PERSON_MONTH, 2)
        pm_p90 = round(effort_p90 / HOURS_PER_PERSON_MONTH, 2)

        manifest = self.bundle.manifest
        model_hash = (
            manifest.get("file_hashes", {}).get("model_params.json")
            or manifest.get("file_hashes", {}).get("model.pkl")
            or manifest.get("dataset_sha256", "")
        )
        result = {
            # Legacy fields for backward compatibility
            "effort_hours_likely": round(effort_p50, 1),
            "effort_hours_min": round(effort_p10, 1),
            "effort_hours_max": round(effort_p90, 1),
            "effort_hours_p25": round(effort_p25, 1),
            "effort_hours_p75": round(effort_p75, 1),
            "confidence_pct": 80.0,
            "nominal_interval_coverage": 0.80,
            "likely_band_coverage": 0.50,
            "model_mode": "production_v2_monotone",
            "model_version": self.bundle.model_version,
            "org_calibration": org_calibration,

            # v2 Contract fields
            "effort_hours": {
                "p10": round(effort_p10, 1),
                "p25": round(effort_p25, 1),
                "p50": round(effort_p50, 1),
                "p75": round(effort_p75, 1),
                "p90": round(effort_p90, 1),
            },
            "person_months": {
                "p10": pm_p10,
                "p25": pm_p25,
                "p50": pm_p50,
                "p75": pm_p75,
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
                "sha256": model_hash,
                "model_sha256": manifest.get("file_hashes", {}).get("model.pkl", model_hash),
                "dataset_sha256": manifest.get("dataset_sha256", ""),
                "trained_on_rows": manifest.get("dataset_records", 915),
                "sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att_aptness"],
                "metrics_ref": "docs/MODEL_VALIDATION_SUMMARY.md",
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
