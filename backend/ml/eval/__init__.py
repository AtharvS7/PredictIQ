"""PredictIQ Evaluation Harness (v2.0).

Adheres strictly to docs/contracts/evaluation_protocol.md and docs/contracts/ml_contract.md.
Provides:
- LeaveOneSourceOutSplitter and RepeatedGroupedKFoldSplitter
- Frozen metrics: R^2, RMSE, MAE, MdMRE, MdAPE, PRED(25), PRED(30), PRED(50), RMSLE, Log-bias, MMRE, SA
- Fixed baselines: MedianDummyPredictor, MedianProductivityPredictor, AlbrechtNominalPredictor, LogLinearBaseline, HuberPowerLawBaseline
"""

from backend.ml.eval.protocol import (
    FoldSplit,
    LeaveOneSourceOutSplitter,
    RepeatedGroupedKFoldSplitter,
    load_dataset,
)
from backend.ml.eval.metrics import (
    compute_metrics,
    log_bias,
    macro_average_metrics,
    mae,
    mdape,
    mdmre,
    mmre,
    pred_k,
    pred25,
    pred30,
    pred50,
    r2_score,
    rmse,
    rmsle,
    standardized_accuracy,
)
from backend.ml.eval.baselines import (
    AlbrechtNominalPredictor,
    BaseBaseline,
    COCOMONominalPredictor,
    HuberPowerLawBaseline,
    LogLinearBaseline,
    MedianDummyPredictor,
    MedianProductivityPredictor,
    PowerLawBaseline,
)

__all__ = [
    "FoldSplit",
    "LeaveOneSourceOutSplitter",
    "RepeatedGroupedKFoldSplitter",
    "load_dataset",
    "r2_score",
    "rmse",
    "mae",
    "mdmre",
    "mdape",
    "pred_k",
    "pred25",
    "pred30",
    "pred50",
    "rmsle",
    "log_bias",
    "mmre",
    "standardized_accuracy",
    "compute_metrics",
    "macro_average_metrics",
    "BaseBaseline",
    "MedianDummyPredictor",
    "MedianProductivityPredictor",
    "AlbrechtNominalPredictor",
    "COCOMONominalPredictor",
    "PowerLawBaseline",
    "LogLinearBaseline",
    "HuberPowerLawBaseline",
]
