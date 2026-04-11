"""
PredictIQ ML Service
=====================
Bridges FastAPI estimation endpoints with the ML inference module.
Builds 27-feature vectors from extracted project parameters and
calls predictor.predict() for effort estimation.

Used by estimates.py via: ml_service.predict(params)
"""

import numpy as np
import structlog
from typing import Any

from ml.inference import predictor

logger = structlog.get_logger()


# ── T-factor mappings ─────────────────────────────────────────────────
# Convert human-readable complexity/methodology to 1–5 ordinal scale

COMPLEXITY_MAP: dict[str, float] = {
    "Low": 1.0,
    "Medium": 2.5,
    "High": 4.0,
    "Very High": 5.0,
}

METHODOLOGY_T04: dict[str, float] = {
    "Agile": 4.0,
    "Waterfall": 3.0,
    "Hybrid": 3.0,
}

METHODOLOGY_T05: dict[str, float] = {
    "Agile": 4.0,
    "Waterfall": 4.0,
    "Hybrid": 3.0,
}


def _team_size_to_exp(team_size: int) -> float:
    """Map team size to experience proxy (1–4 scale)."""
    if team_size <= 2:
        return 1.0
    if team_size <= 4:
        return 2.0
    if team_size <= 8:
        return 3.0
    return 4.0


class MLService:
    """Handles feature vector construction and ML prediction."""

    def predict(self, params: dict) -> dict:
        """
        Build feature vector from extracted parameters and run prediction.

        Args:
            params: Dictionary containing project parameters:
                - project_type, team_size, duration_months
                - complexity, methodology, tech_stack
                - size_fp, feature_count

        Returns:
            Prediction result dict with effort_hours_likely/min/max,
            confidence_pct, model_mode.
        """
        feature_vector = self._build_feature_vector(params)

        result = predictor.predict(feature_vector)

        logger.info(
            "ml_prediction_complete",
            mode=result.get("model_mode"),
            effort_likely=result.get("effort_hours_likely"),
            confidence=result.get("confidence_pct"),
        )
        return result

    def _build_feature_vector(self, params: dict) -> dict[str, float]:
        """
        Construct a 27-feature dictionary matching predictiq_features.json.

        Maps extracted project parameters to the exact model features:
        TeamExp, ManagerExp, duration_months, Transactions, Entities,
        PointsNonAdjust, Adjustment, size_fp, T01–T15,
        log_size_fp, complexity_score, team_skill_avg, risk_score.
        """
        size_fp = float(params.get("size_fp", 150.0))
        duration = float(params.get("duration_months", 6.0))
        team_size = int(params.get("team_size", 4))
        complexity = params.get("complexity", "Medium")
        methodology = params.get("methodology", "Agile")

        # Map complexity to T-factor scale (1–5)
        c_score = COMPLEXITY_MAP.get(complexity, 2.5)

        # Team experience proxy from team size
        team_exp = _team_size_to_exp(team_size)
        manager_exp = min(4.0, team_exp + 0.5)

        # Derived FP components
        transactions = size_fp * 0.85
        entities = size_fp * 0.30
        raw_fp = size_fp / max(0.8 + c_score * 0.04, 0.01)  # Approx unadjusted
        adjustment = size_fp / max(raw_fp, 1.0)

        # T-factors: systematic mapping from project characteristics
        t01 = min(5.0, max(1.0, c_score * 0.9))       # Data communication
        t02 = min(5.0, max(1.0, c_score * 0.8))       # Distributed processing
        t03 = min(5.0, max(1.0, c_score * 0.85))      # Performance
        t04 = METHODOLOGY_T04.get(methodology, 3.0)    # Configuration reuse
        t05 = METHODOLOGY_T05.get(methodology, 3.0)    # Transaction rate
        t06 = 3.0                                       # Online data entry
        t07 = c_score                                   # End-user efficiency
        t08 = min(5.0, max(1.0, 5 - team_exp))         # Req volatility (inverse exp)
        t09 = c_score                                   # Processing complexity
        t10 = min(5.0, max(1.0, c_score * 0.9))        # Reusability
        t11 = min(5.0, max(1.0, c_score * 0.85))       # Installation ease
        t12 = team_exp                                  # Operational ease
        t13 = min(5.0, max(1.0, team_exp * 0.8))       # Multiple sites
        t14 = min(5.0, max(1.0, team_exp))              # Facilitate change
        t15 = min(5.0, max(1.0, team_exp * 0.9))        # Decision support

        complexity_score = (t07 + t10 + t11) / 3
        team_skill_avg = (t12 + t13 + t14 + t15) / 4
        risk_score = (t08 + t09) / 2
        log_size_fp = float(np.log1p(size_fp))

        return {
            "TeamExp": team_exp,
            "ManagerExp": manager_exp,
            "duration_months": duration,
            "Transactions": transactions,
            "Entities": entities,
            "PointsNonAdjust": raw_fp,
            "Adjustment": adjustment,
            "size_fp": size_fp,
            "T01": t01,
            "T02": t02,
            "T03": t03,
            "T04": t04,
            "T05": t05,
            "T06": t06,
            "T07": t07,
            "T08": t08,
            "T09": t09,
            "T10": t10,
            "T11": t11,
            "T12": t12,
            "T13": t13,
            "T14": t14,
            "T15": t15,
            "log_size_fp": log_size_fp,
            "complexity_score": complexity_score,
            "team_skill_avg": team_skill_avg,
            "risk_score": risk_score,
        }

    def is_ready(self) -> bool:
        """Check if the ML model is loaded and ready."""
        return predictor.is_ready

    def get_model_info(self) -> dict:
        """Get model information for health checks."""
        return predictor.get_model_info()


ml_service = MLService()
