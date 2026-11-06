"""Conformal Prediction and Calibrated Uncertainty for PredictIQ v2 (CP11).

Provides:
- ConformalIntervalPredictor: Unified split and Mondrian conformal wrapper for Track 1 estimators.
- MondrianConformalPredictor: Bucket-conditional conformal prediction grouped by functional size (<150, 150-750, >750).
- SplitConformalPredictor: Standard split conformal prediction wrapper with exchangeable coverage guarantees.
- Non-conformity scoring in log-residual and scaled relative error space.
- Guaranteed quantile monotonicity (p10 <= p50 <= p90) with p10 >= 1.0 hr.
"""

from __future__ import annotations

from backend.ml.calibration.conformal import (
    MONDRIAN_BUCKETS,
    SIZE_BUCKET_THRESHOLDS,
    ConformalIntervalPredictor,
    MondrianConformalPredictor,
    SplitConformalPredictor,
    assign_mondrian_bucket,
    compute_conformal_quantile,
    log_residual_score,
    scaled_relative_error_score,
)

__all__ = [
    "MONDRIAN_BUCKETS",
    "SIZE_BUCKET_THRESHOLDS",
    "ConformalIntervalPredictor",
    "MondrianConformalPredictor",
    "SplitConformalPredictor",
    "assign_mondrian_bucket",
    "compute_conformal_quantile",
    "log_residual_score",
    "scaled_relative_error_score",
]
