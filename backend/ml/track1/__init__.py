"""Track 1 Models: Simple, Transparent, Monotonic Power-Law Models.

This package implements the Track 1 effort estimation models for PredictIQ v2:
1. MonotonePowerLaw: E = a * S^b with b > 0 strictly enforced.
2. MultivariateMonotoneModel: E = a * S^b * D^c with b > 0 and bounded duration elasticity c,
   handling missing duration gracefully without synthetic imputation.
3. SegmentedMonotoneModel: Size-bucketed power law (small < 150 FP, medium 150-750 FP, large > 750 FP)
   with boundary smoothing ensuring dE/dS > 0 everywhere.

All models strictly conform to docs/contracts/ml_contract.md:
- Inputs limited to size_fp/size_value, optional duration_months, optional team_size.
- Zero fabricated features, zero synthetic imputation.
- Predictions guaranteed positive and finite.
- Permanently rejects banned complexity factors and legacy metrics.
"""

from __future__ import annotations

from backend.ml.track1.models import (
    BANNED_FEATURES,
    MonotonePowerLaw,
    MultivariateMonotoneModel,
    SegmentedMonotoneModel,
    validate_and_extract_inputs,
)

__all__ = [
    "BANNED_FEATURES",
    "MonotonePowerLaw",
    "MultivariateMonotoneModel",
    "SegmentedMonotoneModel",
    "validate_and_extract_inputs",
]
