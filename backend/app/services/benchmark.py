"""
Predictify Benchmark Service
Compares current estimate against historical training dataset.
"""
import pandas as pd
import numpy as np
import structlog
from pathlib import Path

logger = structlog.get_logger()

_benchmark_df: pd.DataFrame | None = None


def load_benchmark_data():
    """Load the training dataset for benchmark comparisons."""
    global _benchmark_df
    csv_path = Path(__file__).parent.parent.parent / "ml" / "predictiq_merged_dataset.csv"

    if csv_path.exists():
        _benchmark_df = pd.read_csv(csv_path)
        logger.info("benchmark_data_loaded", rows=len(_benchmark_df))
    else:
        logger.warning("benchmark_data_not_found", path=str(csv_path))


def get_benchmark_comparison(
    size_fp: float,
    effort_hours_likely: float,
    cost_likely_usd: float,
    duration_months: float,
    hourly_rate: float = 75.0,
) -> str:
    """
    Compare current estimate against historical projects of similar size.

    Returns a plain-English benchmark comparison string.
    """
    if _benchmark_df is None or _benchmark_df.empty:
        return (
            "Benchmark data unavailable. Unable to compare against historical projects."
        )

    # Find similar projects (±30% of size_fp)
    fp_lower = size_fp * 0.7
    fp_upper = size_fp * 1.3
    similar = _benchmark_df[
        (_benchmark_df["size_fp"] >= fp_lower) & (_benchmark_df["size_fp"] <= fp_upper)
    ]

    if len(similar) < 3:
        # Broaden range if too few matches
        fp_lower = size_fp * 0.5
        fp_upper = size_fp * 1.5
        similar = _benchmark_df[
            (_benchmark_df["size_fp"] >= fp_lower)
            & (_benchmark_df["size_fp"] <= fp_upper)
        ]

    if len(similar) == 0:
        return (
            f"No similar projects found in the dataset for {size_fp:.0f} function points. "
            "This estimate is at the edge of our training data range."
        )

    # Calculate comparison metrics
    median_effort = similar["effort_hours"].median()
    mean_effort = similar["effort_hours"].mean()
    p25_effort = similar["effort_hours"].quantile(0.25)
    p75_effort = similar["effort_hours"].quantile(0.75)

    median_cost = median_effort * hourly_rate
    mean_cost = mean_effort * hourly_rate

    # Percentile of current estimate
    percentile = (similar["effort_hours"] <= effort_hours_likely).mean() * 100

    # Deviation from median
    deviation_pct = ((effort_hours_likely - median_effort) / median_effort) * 100

    direction = "above" if deviation_pct > 0 else "below"
    abs_dev = abs(deviation_pct)

    comparison = (
        f"Based on {len(similar)} similar projects ({fp_lower:.0f}–{fp_upper:.0f} FP), "
        f"typical effort ranges from {p25_effort:,.0f} to {p75_effort:,.0f} hours "
        f"(median: {median_effort:,.0f} hrs, ~${median_cost:,.0f}). "
        f"Your estimate of {effort_hours_likely:,.0f} hours (${cost_likely_usd:,.0f}) "
        f"is {abs_dev:.0f}% {direction} the median, "
        f"placing it at the {percentile:.0f}th percentile."
    )

    return comparison


def get_model_explanation(
    params: dict,
    effort_hours: float,
    feature_importance: dict | None = None,
) -> str:
    """
    Generate a plain-English explanation of what drove the prediction.

    Args:
        params: Input parameters.
        effort_hours: Predicted effort hours.
        feature_importance: Feature importance dict from model.

    Returns:
        Human-readable explanation string.
    """
    drivers = []

    size_fp = params.get("size_fp", 0)
    complexity = params.get("complexity", "Medium")
    duration = params.get("duration_months", 6)
    team_size = params.get("team_size", 5)
    tech_count = len(params.get("tech_stack", []))

    if size_fp > 300:
        drivers.append(f"large scope ({size_fp:.0f} function points)")
    elif size_fp < 100:
        drivers.append(f"compact scope ({size_fp:.0f} function points)")

    if complexity in ("High", "Very High"):
        drivers.append(f"{complexity.lower()} complexity")
    elif complexity == "Low":
        drivers.append("low complexity reducing effort")

    if duration > 12:
        drivers.append(f"extended {duration:.0f}-month timeline")
    elif duration < 3:
        drivers.append(f"compressed {duration:.0f}-month timeline")

    if team_size > 10:
        drivers.append(f"large team of {team_size}")

    if tech_count > 5:
        drivers.append(f"diverse technology stack ({tech_count} technologies)")

    if not drivers:
        drivers.append("moderate scope and complexity")

    driver_text = ", ".join(drivers[:-1])
    if len(drivers) > 1:
        driver_text += f", and {drivers[-1]}"
    else:
        driver_text = drivers[0]

    return (
        f"The estimated effort of {effort_hours:,.0f} hours is primarily driven by "
        f"{driver_text}. "
        f"The model considers {size_fp:.0f} function points with {complexity.lower()} "
        f"complexity as the key cost factors."
    )
