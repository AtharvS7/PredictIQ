"""Evaluation metrics for software effort estimation.

Implements all metrics specified in docs/contracts/evaluation_protocol.md:
- R^2, RMSE, MAE
- MdMRE and MdAPE (Primary Metric)
- PRED(25), PRED(30), PRED(50)
- RMSLE (Root Mean Squared Log Error)
- Log-space bias
- MMRE (Mean Magnitude of Relative Error)
- Standardized Accuracy (SA)
- Macro-averaging across evaluation folds
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np


def _check_arrays(
    y_true: Any,
    y_pred: Any,
) -> tuple[np.ndarray, np.ndarray]:
    """Validate and convert input arrays to 1D float numpy arrays."""
    y_t = np.asarray(y_true, dtype=np.float64).ravel()
    y_p = np.asarray(y_pred, dtype=np.float64).ravel()

    if len(y_t) == 0:
        raise ValueError("Input arrays must not be empty.")
    if len(y_t) != len(y_p):
        raise ValueError(f"Length mismatch: len(y_true)={len(y_t)} != len(y_pred)={len(y_p)}")
    if not (np.isfinite(y_t).all() and np.isfinite(y_p).all()):
        raise ValueError("Arrays contain NaN or infinite values.")

    return y_t, y_p


def r2_score(y_true: Any, y_pred: Any) -> float:
    """Coefficient of Determination R^2."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    ss_res = np.sum((y_t - y_p) ** 2)
    ss_tot = np.sum((y_t - np.mean(y_t)) ** 2)
    if ss_tot == 0.0:
        return 0.0 if ss_res == 0.0 else -float("inf")
    return float(1.0 - (ss_res / ss_tot))


def rmse(y_true: Any, y_pred: Any) -> float:
    """Root Mean Squared Error."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    return float(np.sqrt(np.mean((y_t - y_p) ** 2)))


def mae(y_true: Any, y_pred: Any) -> float:
    """Mean Absolute Error."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    return float(np.mean(np.abs(y_t - y_p)))


def mdmre(y_true: Any, y_pred: Any, as_percentage: bool = False) -> float:
    """Median Magnitude of Relative Error.

    MRE_i = |y_pred_i - y_true_i| / y_true_i
    """
    y_t, y_p = _check_arrays(y_true, y_pred)
    if (y_t <= 0).any():
        raise ValueError("y_true must contain strictly positive values for relative error metrics.")

    mre = np.abs(y_p - y_t) / y_t
    val = float(np.median(mre))
    return val * 100.0 if as_percentage else val


def mdape(y_true: Any, y_pred: Any) -> float:
    """Median Absolute Percentage Error (Primary Metric in evaluation protocol).

    MdAPE = median(|y_pred_i - y_true_i| / y_true_i) * 100%
    """
    return mdmre(y_true, y_pred, as_percentage=True)


def pred_k(y_true: Any, y_pred: Any, k: float = 0.25, as_percentage: bool = True) -> float:
    """PRED(k): Proportion of predictions within k * 100% of actual effort."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    if k <= 0:
        raise ValueError(f"Threshold k must be positive, got {k}")
    if (y_t <= 0).any():
        raise ValueError("y_true must contain strictly positive values for PRED(k).")

    mre = np.abs(y_p - y_t) / y_t
    within = np.mean(mre <= k)
    return float(within * 100.0 if as_percentage else within)


def pred25(y_true: Any, y_pred: Any) -> float:
    """PRED(25): Percentage of predictions within 25% of actual effort."""
    return pred_k(y_true, y_pred, k=0.25, as_percentage=True)


def pred30(y_true: Any, y_pred: Any) -> float:
    """PRED(30): Percentage of predictions within 30% of actual effort."""
    return pred_k(y_true, y_pred, k=0.30, as_percentage=True)


def pred50(y_true: Any, y_pred: Any) -> float:
    """PRED(50): Percentage of predictions within 50% of actual effort."""
    return pred_k(y_true, y_pred, k=0.50, as_percentage=True)


def rmsle(y_true: Any, y_pred: Any) -> float:
    """Root Mean Squared Logarithmic Error.

    RMSLE = sqrt(mean((ln(y_pred) - ln(y_true))^2))
    Clips zero/negative values to 1e-6 to avoid invalid logs.
    """
    y_t, y_p = _check_arrays(y_true, y_pred)
    y_t_safe = np.maximum(y_t, 1e-6)
    y_p_safe = np.maximum(y_p, 1e-6)
    log_diff = np.log(y_p_safe) - np.log(y_t_safe)
    return float(np.sqrt(np.mean(log_diff ** 2)))


def log_bias(y_true: Any, y_pred: Any) -> float:
    """Log-space bias: mean(ln(y_pred) - ln(y_true))."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    y_t_safe = np.maximum(y_t, 1e-6)
    y_p_safe = np.maximum(y_p, 1e-6)
    return float(np.mean(np.log(y_p_safe) - np.log(y_t_safe)))


def mmre(y_true: Any, y_pred: Any, as_percentage: bool = True) -> float:
    """Mean Magnitude of Relative Error (explicitly labelled 'misleading alone' in protocol)."""
    y_t, y_p = _check_arrays(y_true, y_pred)
    if (y_t <= 0).any():
        raise ValueError("y_true must contain strictly positive values for MMRE.")

    mre = np.abs(y_p - y_t) / y_t
    val = float(np.mean(mre))
    return val * 100.0 if as_percentage else val


def standardized_accuracy(
    y_true: Any,
    y_pred: Any,
    y_train: Any = None,
    mae_random: float | None = None,
) -> float:
    """Standardized Accuracy (SA): (1 - MAE_model / MAE_random_guessing) * 100%.

    If mae_random is not explicitly provided:
    - If y_train is given, mae_random is computed as MAE of predicting median(y_train) on y_true.
    - Otherwise, mae_random is MAE of predicting median(y_true) on y_true.
    """
    y_t, y_p = _check_arrays(y_true, y_pred)
    mae_model = mae(y_t, y_p)

    if mae_random is None:
        if y_train is not None:
            y_tr = np.asarray(y_train, dtype=np.float64).ravel()
            baseline_pred = np.full_like(y_t, np.median(y_tr))
        else:
            baseline_pred = np.full_like(y_t, np.median(y_t))
        mae_random = mae(y_t, baseline_pred)

    if mae_random == 0.0:
        return 0.0 if mae_model == 0.0 else -float("inf")

    return float((1.0 - (mae_model / mae_random)) * 100.0)


def compute_metrics(
    y_true: Any,
    y_pred: Any,
    y_train: Any = None,
) -> dict[str, float]:
    """Compute complete suite of frozen evaluation metrics."""
    y_t, y_p = _check_arrays(y_true, y_pred)

    return {
        "r2": r2_score(y_t, y_p),
        "rmse": rmse(y_t, y_p),
        "mae": mae(y_t, y_p),
        "mdmre": mdmre(y_t, y_p, as_percentage=False),
        "mdape": mdape(y_t, y_p),
        "pred25": pred25(y_t, y_p),
        "pred30": pred30(y_t, y_p),
        "pred50": pred50(y_t, y_p),
        "rmsle": rmsle(y_t, y_p),
        "log_bias": log_bias(y_t, y_p),
        "mmre": mmre(y_t, y_p, as_percentage=True),
        "sa": standardized_accuracy(y_t, y_p, y_train=y_train),
    }


def macro_average_metrics(
    fold_metrics: Sequence[Mapping[str, float]],
) -> dict[str, float]:
    """Compute macro-average (unweighted arithmetic mean) across fold metrics."""
    if not fold_metrics:
        raise ValueError("fold_metrics sequence cannot be empty.")

    keys = list(fold_metrics[0].keys())
    result: dict[str, float] = {}

    for k in keys:
        values = [fm[k] for fm in fold_metrics if k in fm and np.isfinite(fm[k])]
        result[k] = float(np.mean(values)) if values else 0.0

    return result
