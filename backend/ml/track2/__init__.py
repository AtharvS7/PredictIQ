"""Track 2 (Challenger Models) for PredictIQ v2.

Non-linear, tree-based gradient boosted models with positive monotonic constraints
and asymmetric quantile uncertainty estimation.

Models:
- MonotoneHistGradientBoosting: HistGradientBoostingRegressor enforcing positive monotonic
  constraint (+1) on functional size.
- QuantileGradientBoosting: HistGradientBoostingRegressor(loss='quantile') at q in [0.1, 0.5, 0.9]
  producing calibrated asymmetric uncertainty intervals with guaranteed non-crossing (p10 <= p50 <= p90).
- MultivariateHistGradientBoosting: Non-linear interaction challenger model incorporating planned
  target duration and team size without synthetic imputation.

Strict ML Contract adherence (docs/contracts/ml_contract.md):
- Strictly bans fabricated complexity factors (T01-T15, Transactions, Entities, etc.).
- Guaranteed positive and finite predictions (clamped to >= 1.0 hour).
- Zero synthetic imputation.
"""

from __future__ import annotations

from backend.ml.track2.models import (
    BANNED_FEATURES,
    MonotoneHistGradientBoosting,
    MultivariateHistGradientBoosting,
    QuantileGradientBoosting,
    validate_and_extract_inputs,
)

__all__ = [
    "BANNED_FEATURES",
    "MonotoneHistGradientBoosting",
    "MultivariateHistGradientBoosting",
    "QuantileGradientBoosting",
    "validate_and_extract_inputs",
]
