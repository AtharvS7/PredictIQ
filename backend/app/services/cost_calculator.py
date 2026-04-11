"""
PredictIQ Cost Calculator Service
Implements the 3-layer hybrid estimation pipeline:
Layer 1: IFPUG Function Point Estimation
Layer 2: XGBoost ML Prediction (via ml_service)
Layer 3: Parametric Cost Conversion
"""
import numpy as np
import structlog
from typing import Optional

logger = structlog.get_logger()

# IFPUG complexity weights
COMPLEXITY_WEIGHTS = {
    "simple": 5,
    "medium": 10,
    "complex": 20,
    "epic": 35,
}

# Value Adjustment Factor by complexity level
VAF_MAP = {
    "Low": 0.75,
    "Medium": 0.90,
    "High": 1.05,
    "Very High": 1.20,
}

# Phase breakdown ratios (industry standard)
PHASE_RATIOS = {
    "Discovery & Requirements": 0.10,
    "UI/UX Design": 0.12,
    "Backend Development": 0.30,
    "Frontend Development": 0.22,
    "QA & Testing": 0.18,
    "Deployment & DevOps": 0.08,
}


def estimate_function_points(
    feature_count: int = 10,
    complexity: str = "Medium",
    external_inputs: int = 5,
    external_outputs: int = 3,
    external_inquiries: int = 4,
    internal_logical_files: int = 4,
    external_interface_files: int = 2,
    tech_stack_count: int = 3,
) -> float:
    """
    Layer 1: Estimate IFPUG Function Points from project parameters.

    Args:
        feature_count: Number of identified features/requirements.
        complexity: Overall complexity level.
        external_inputs: Count of distinct user input forms.
        external_outputs: Count of distinct report/export types.
        external_inquiries: Count of read-only queries.
        internal_logical_files: Count of main data entities.
        external_interface_files: Count of third-party integrations.
        tech_stack_count: Number of technologies in the stack.

    Returns:
        Adjusted Function Points (size_fp).
    """
    # Assign complexity tiers to features
    if complexity in ("Low",):
        tier_dist = {"simple": 0.6, "medium": 0.3, "complex": 0.1, "epic": 0.0}
    elif complexity in ("Medium",):
        tier_dist = {"simple": 0.3, "medium": 0.4, "complex": 0.25, "epic": 0.05}
    elif complexity in ("High",):
        tier_dist = {"simple": 0.1, "medium": 0.3, "complex": 0.4, "epic": 0.2}
    else:  # Very High
        tier_dist = {"simple": 0.05, "medium": 0.2, "complex": 0.4, "epic": 0.35}

    # Calculate raw FP from features
    raw_fp = sum(
        int(feature_count * pct) * COMPLEXITY_WEIGHTS[tier]
        for tier, pct in tier_dist.items()
    )

    # Add standard IFPUG components
    raw_fp += external_inputs * 4
    raw_fp += external_outputs * 5
    raw_fp += external_inquiries * 4
    raw_fp += internal_logical_files * 7
    raw_fp += external_interface_files * 5

    # Extra complexity from tech stack diversity
    raw_fp += tech_stack_count * 3

    # Apply Value Adjustment Factor
    vaf = VAF_MAP.get(complexity, 0.90)
    size_fp = raw_fp * vaf

    # Clamp to dataset range (83-1849 in training data, but allow some flex)
    size_fp = max(50, min(size_fp, 3000))

    logger.info(
        "function_points_estimated",
        raw_fp=raw_fp,
        vaf=vaf,
        size_fp=round(size_fp, 1),
    )
    return round(size_fp, 1)


def calculate_cost(
    effort_hours_likely: float,
    effort_hours_min: float,
    effort_hours_max: float,
    hourly_rate_usd: float = 75.0,
) -> dict:
    """
    Layer 3: Convert effort hours to monetary cost.

    Returns:
        Dictionary with min, likely, max costs in USD.
    """
    return {
        "cost_min_usd": round(effort_hours_min * hourly_rate_usd, 2),
        "cost_likely_usd": round(effort_hours_likely * hourly_rate_usd, 2),
        "cost_max_usd": round(effort_hours_max * hourly_rate_usd, 2),
    }


def calculate_timeline(
    duration_months: float,
    team_size: int,
) -> dict:
    """
    Calculate project timeline in weeks.
    Applies Brooks's Law simplified scaling.

    Returns:
        Dictionary with min, likely, max timeline in weeks.
    """
    base_weeks = duration_months * 4.33

    # Brooks's Law: more people → faster but not linearly
    team_scaling_factor = 1.0 / (0.5 + (team_size / 10))
    timeline_likely = max(4, base_weeks * team_scaling_factor)
    timeline_min = timeline_likely * 0.80
    timeline_max = timeline_likely * 1.35

    return {
        "timeline_min_weeks": round(timeline_min, 1),
        "timeline_likely_weeks": round(timeline_likely, 1),
        "timeline_max_weeks": round(timeline_max, 1),
    }


def calculate_phase_breakdown(
    effort_hours_likely: float,
    cost_likely_usd: float,
    timeline_likely_weeks: float,
) -> list[dict]:
    """
    Break down effort and cost by project phase.

    Returns:
        List of phase breakdown dictionaries.
    """
    breakdown = []
    for phase, ratio in PHASE_RATIOS.items():
        breakdown.append({
            "phase": phase,
            "effort_hours": round(effort_hours_likely * ratio, 1),
            "cost_usd": round(cost_likely_usd * ratio, 2),
            "duration_weeks": round(timeline_likely_weeks * ratio, 1),
            "pct_of_total": round(ratio * 100, 0),
        })
    return breakdown


def build_feature_vector_params(
    project_type: str,
    team_size: int,
    duration_months: float,
    complexity: str,
    tech_stack: list[str],
    feature_count: int = 10,
) -> dict:
    """
    Build the full parameter dict needed for estimation.
    Combines IFPUG FP calculation with user inputs.
    """
    # Estimate function points
    size_fp = estimate_function_points(
        feature_count=feature_count,
        complexity=complexity,
        tech_stack_count=len(tech_stack),
    )

    return {
        "project_type": project_type,
        "team_size": team_size,
        "duration_months": duration_months,
        "complexity": complexity,
        "tech_stack": tech_stack,
        "size_fp": size_fp,
        "feature_count": feature_count,
    }
