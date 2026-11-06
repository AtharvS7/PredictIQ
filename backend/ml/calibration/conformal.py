"""Conformal Prediction Wrappers and Calibrated Uncertainty Estimation (CP11).

Implements split conformal prediction and Mondrian (bucket-conditional) conformal
prediction for Track 1 effort estimators (MultivariateMonotoneModel and MonotonePowerLaw).

Mathematical Guarantees:
1. Nominal Coverage Guarantee:
   Under exchangeability, split conformal prediction guarantees that:
       P(y in [p10, p90]) >= 1 - alpha = 0.80 (for alpha = 0.20)
2. Mondrian Group-Conditional Calibration:
   Calibration grouped by Functional Size:
       - Small: S < 150 FP
       - Medium: 150 <= S <= 750 FP
       - Large: S > 750 FP
   Ensures conditional coverage across diverse project sizes without over-conservatism
   on smaller projects.
3. Quantile Monotonicity:
   Guarantees 1.0 hr <= p10 <= p50 <= p90 for every prediction point x.
4. ML Contract Adherence (docs/contracts/ml_contract.md):
   Strictly rejects banned complexity factors (T01-T15, Transactions, Entities, etc.),
   never performs synthetic imputation, and ensures finite, positive predictions.
"""

from __future__ import annotations

from typing import Any, Literal, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import train_test_split

from backend.ml.track1.models import (
    BANNED_FEATURES,
    MultivariateMonotoneModel,
    validate_and_extract_inputs,
)

SIZE_BUCKET_THRESHOLDS: tuple[float, float] = (150.0, 750.0)
MONDRIAN_BUCKETS: tuple[str, str, str] = ("small", "medium", "large")

__all__ = [
    "BANNED_FEATURES",
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


def assign_mondrian_bucket(size: np.ndarray | float | Sequence[float]) -> np.ndarray:
    """Assign functional size values to Mondrian calibration buckets.

    Buckets:
    - 'small':  S < 150.0 FP
    - 'medium': 150.0 <= S <= 750.0 FP
    - 'large':  S > 750.0 FP

    Parameters
    ----------
    size : array-like or float
        Functional size values (size_fp / size_value).

    Returns
    -------
    np.ndarray of dtype '<U6'
        Array of bucket labels ('small', 'medium', 'large').
    """
    s_arr = np.asarray(size, dtype=np.float64)
    buckets = np.where(
        s_arr < SIZE_BUCKET_THRESHOLDS[0],
        "small",
        np.where(s_arr <= SIZE_BUCKET_THRESHOLDS[1], "medium", "large"),
    )
    return buckets


def log_residual_score(y_true: Any, y_pred: Any) -> np.ndarray:
    """Compute non-conformity score in log-residual space.

    Formula:
        R_i = |ln(y_i) - ln(y_hat_i)| = |ln(y_i / y_hat_i)|

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Observed effort hours (> 0).
    y_pred : array-like of shape (n_samples,)
        Predicted effort hours (> 0).

    Returns
    -------
    np.ndarray of shape (n_samples,)
        Absolute log-residuals.
    """
    y_t = np.asarray(y_true, dtype=np.float64).ravel()
    y_p = np.asarray(y_pred, dtype=np.float64).ravel()

    if len(y_t) != len(y_p):
        raise ValueError(
            f"Length mismatch: len(y_true)={len(y_t)} != len(y_pred)={len(y_p)}"
        )
    if (y_t <= 0).any() or not np.isfinite(y_t).all():
        raise ValueError("All y_true values must be strictly positive and finite.")
    if (y_p <= 0).any() or not np.isfinite(y_p).all():
        raise ValueError("All y_pred values must be strictly positive and finite.")

    return np.abs(np.log(y_t) - np.log(y_p))


def scaled_relative_error_score(y_true: Any, y_pred: Any) -> np.ndarray:
    """Compute non-conformity score as scaled relative error.

    Formula:
        R_i = |y_i - y_hat_i| / y_hat_i

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        Observed effort hours (> 0).
    y_pred : array-like of shape (n_samples,)
        Predicted effort hours (> 0).

    Returns
    -------
    np.ndarray of shape (n_samples,)
        Scaled relative errors.
    """
    y_t = np.asarray(y_true, dtype=np.float64).ravel()
    y_p = np.asarray(y_pred, dtype=np.float64).ravel()

    if len(y_t) != len(y_p):
        raise ValueError(
            f"Length mismatch: len(y_true)={len(y_t)} != len(y_pred)={len(y_p)}"
        )
    if (y_t <= 0).any() or not np.isfinite(y_t).all():
        raise ValueError("All y_true values must be strictly positive and finite.")
    if (y_p <= 0).any() or not np.isfinite(y_p).all():
        raise ValueError("All y_pred values must be strictly positive and finite.")

    return np.abs(y_t - y_p) / y_p


def compute_conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """Compute finite-sample corrected conformal prediction quantile.

    Formula:
        q_level = ceil((n + 1) * (1 - alpha)) / n
        q = Quantile(scores, q_level, method='higher')

    Parameters
    ----------
    scores : np.ndarray
        1D non-conformity scores.
    alpha : float
        Significance level in (0, 1), e.g. 0.20 for an 80% prediction interval.

    Returns
    -------
    float
        Conformal critical quantile threshold.
    """
    if len(scores) == 0:
        raise ValueError("Cannot compute conformal quantile on empty scores array.")
    if not (0.0 < alpha < 1.0):
        raise ValueError(f"Significance level alpha must be in (0, 1), got {alpha}")

    n = len(scores)
    # Finite-sample conformal correction index
    target_idx = int(np.ceil((n + 1) * (1.0 - alpha)))

    if target_idx > n:
        # If target order statistic exceeds sample count, use maximum observed score
        return float(np.max(scores))

    q_level = float(target_idx / n)
    q_level = float(np.clip(q_level, 0.0, 1.0))
    return float(np.quantile(scores, q_level, method="higher"))


class ConformalIntervalPredictor(BaseEstimator, RegressorMixin):
    """Conformal Prediction Wrapper for software effort estimation models.

    Provides finite-sample split conformal and Mondrian (bucket-conditional)
    calibration around any point estimator, with special optimization for Track 1
    monotone power-law models.

    Parameters
    ----------
    estimator : Any | None
        Base point estimator. Defaults to MultivariateMonotoneModel().
    alpha : float
        Target significance level (default 0.20 for an 80% coverage interval [p10, p90]).
    mondrian : bool
        If True (default), performs Mondrian bucket-conditional calibration across
        functional size categories (<150, 150-750, >750).
    score_type : Literal["log_residual", "scaled_relative"]
        Non-conformity score metric. Defaults to "log_residual".
    cal_size : float
        Fraction of training observations reserved for calibration when fit() is called
        without explicit calibration data (default 0.20).
    min_bucket_samples : int
        Minimum calibration observations required in a Mondrian bucket before falling
        back to the global quantile threshold (default 5).
    random_state : int | None
        Random seed for reproducible train/calibration splitting (default 42).
    """

    def __init__(
        self,
        estimator: Any = None,
        alpha: float = 0.20,
        mondrian: bool = True,
        score_type: Literal["log_residual", "scaled_relative"] = "log_residual",
        cal_size: float = 0.20,
        min_bucket_samples: int = 5,
        random_state: int | None = 42,
    ) -> None:
        self.estimator = estimator
        self.alpha = alpha
        self.mondrian = mondrian
        self.score_type = score_type
        self.cal_size = cal_size
        self.min_bucket_samples = min_bucket_samples
        self.random_state = random_state

        # Fitted & calibrated state
        self.estimator_: Any = None
        self.global_quantile_: float | None = None
        self.bucket_quantiles_: dict[str, float] = {}
        self.cal_scores_: np.ndarray | None = None
        self.is_calibrated_: bool = False

    def fit(
        self,
        X: Any,
        y: Any,
        X_cal: Any = None,
        y_cal: Any = None,
    ) -> ConformalIntervalPredictor:
        """Fit base model and calibrate conformal prediction intervals.

        Parameters
        ----------
        X : DataFrame | array-like of shape (n_samples, n_features)
            Training feature matrix. If X_cal is None and cal_size > 0, X will be
            split into proper train and calibration splits.
        y : array-like of shape (n_samples,)
            Observed effort hours.
        X_cal : DataFrame | array-like, optional
            Explicit calibration feature matrix.
        y_cal : array-like, optional
            Explicit calibration target values.

        Returns
        -------
        ConformalIntervalPredictor
            Fitted and calibrated estimator.
        """
        # Validate inputs against ML contract
        validate_and_extract_inputs(X)
        if X_cal is not None:
            validate_and_extract_inputs(X_cal)

        # Initialize base estimator if none provided
        if self.estimator is None:
            self.estimator_ = MultivariateMonotoneModel()
        elif hasattr(self.estimator, "fit"):
            # Clone or instantiate fresh estimator
            if hasattr(self.estimator, "__class__"):
                self.estimator_ = self.estimator.__class__()
            else:
                self.estimator_ = self.estimator
        else:
            self.estimator_ = self.estimator

        # Case 1: Explicit calibration set provided
        if X_cal is not None and y_cal is not None:
            self.estimator_.fit(X, y)
            self.calibrate(X_cal, y_cal)
            return self

        # Case 2: Split calibration from X, y
        if self.cal_size > 0.0 and len(y) > 10:
            if isinstance(X, pd.DataFrame):
                X_tr, X_c, y_tr, y_c = train_test_split(
                    X,
                    y,
                    test_size=self.cal_size,
                    random_state=self.random_state,
                )
            else:
                X_arr = np.asarray(X)
                y_arr = np.asarray(y)
                X_tr, X_c, y_tr, y_c = train_test_split(
                    X_arr,
                    y_arr,
                    test_size=self.cal_size,
                    random_state=self.random_state,
                )
            self.estimator_.fit(X_tr, y_tr)
            self.calibrate(X_c, y_c)
            return self

        # Case 3: In-sample calibration (cal_size == 0.0 or tiny dataset)
        self.estimator_.fit(X, y)
        self.calibrate(X, y)
        return self

    def calibrate(
        self,
        X_cal: Any,
        y_cal: Any,
    ) -> ConformalIntervalPredictor:
        """Calibrate prediction intervals on a dedicated calibration dataset.

        Parameters
        ----------
        X_cal : DataFrame | array-like of shape (n_cal_samples, n_features)
            Calibration feature matrix.
        y_cal : array-like of shape (n_cal_samples,)
            Calibration target values.

        Returns
        -------
        ConformalIntervalPredictor
            Calibrated instance.
        """
        if self.estimator_ is None:
            if self.estimator is not None:
                self.estimator_ = self.estimator
            else:
                raise NotFittedError(
                    "Base estimator must be fitted before calling calibrate(). "
                    "Either call fit() or assign a fitted estimator_."
                )

        size_cal, _, _ = validate_and_extract_inputs(X_cal)
        y_cal_arr = np.asarray(y_cal, dtype=np.float64).ravel()

        if len(size_cal) != len(y_cal_arr):
            raise ValueError(
                f"Row mismatch in calibration data: X_cal ({len(size_cal)}) vs y_cal ({len(y_cal_arr)})."
            )

        # Get point predictions from base estimator
        y_pred_cal = np.maximum(self.estimator_.predict(X_cal), 1.0)

        # Compute non-conformity scores
        if self.score_type == "log_residual":
            scores = log_residual_score(y_cal_arr, y_pred_cal)
        elif self.score_type == "scaled_relative":
            scores = scaled_relative_error_score(y_cal_arr, y_pred_cal)
        else:
            raise ValueError(
                f"Unsupported score_type: '{self.score_type}'. "
                "Supported: 'log_residual', 'scaled_relative'."
            )

        self.cal_scores_ = scores
        self.global_quantile_ = compute_conformal_quantile(scores, self.alpha)

        # Compute Mondrian bucket-conditional quantiles if requested
        self.bucket_quantiles_ = {}
        if self.mondrian:
            cal_buckets = assign_mondrian_bucket(size_cal)
            for b in MONDRIAN_BUCKETS:
                mask = cal_buckets == b
                if np.sum(mask) >= self.min_bucket_samples:
                    sub_scores = scores[mask]
                    self.bucket_quantiles_[b] = compute_conformal_quantile(
                        sub_scores, self.alpha
                    )
                else:
                    # Fallback to global quantile when bucket has insufficient data
                    self.bucket_quantiles_[b] = self.global_quantile_
        else:
            for b in MONDRIAN_BUCKETS:
                self.bucket_quantiles_[b] = self.global_quantile_

        self.is_calibrated_ = True
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict median effort (p50) in person-hours.

        Standard scikit-learn regressor interface returning point estimates.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Point predictions clamped to >= 1.0 person-hour.
        """
        if not self.is_calibrated_ or self.estimator_ is None:
            raise NotFittedError(
                "This ConformalIntervalPredictor instance is not fitted/calibrated yet. "
                "Call 'fit' or 'calibrate' before predicting."
            )

        validate_and_extract_inputs(X)
        preds = self.estimator_.predict(X)
        return np.maximum(np.asarray(preds, dtype=np.float64), 1.0)

    def predict_quantiles(self, X: Any) -> dict[str, np.ndarray]:
        """Predict calibrated quantile intervals: p10, p50, and p90.

        Strictly enforces:
        1. Quantile monotonicity: p10 <= p50 <= p90 everywhere.
        2. Positive predictions: p10 >= 1.0 person-hour.
        3. Contract compliance: rejects banned features.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features containing size_fp / size_value and optional duration.

        Returns
        -------
        dict[str, np.ndarray]
            Dictionary containing:
            - 'p10': 10th percentile lower bound (>= 1.0 hr).
            - 'p50': 50th percentile median estimate (>= p10).
            - 'p90': 90th percentile upper bound (>= p50).
        """
        if not self.is_calibrated_ or self.estimator_ is None or self.global_quantile_ is None:
            raise NotFittedError(
                "This ConformalIntervalPredictor instance is not fitted/calibrated yet. "
                "Call 'fit' or 'calibrate' before predicting."
            )

        size, _, _ = validate_and_extract_inputs(X)
        n_samples = len(size)

        # Point estimate from base estimator
        base_preds = np.maximum(self.estimator_.predict(X), 1.0)

        # Look up conformal critical thresholds per sample
        if self.mondrian:
            buckets = assign_mondrian_bucket(size)
            thresholds = np.array(
                [self.bucket_quantiles_.get(b, self.global_quantile_) for b in buckets],
                dtype=np.float64,
            )
        else:
            thresholds = np.full(n_samples, self.global_quantile_, dtype=np.float64)

        if self.score_type == "log_residual":
            # [p10, p90] = [y_hat * exp(-q), y_hat * exp(q)]
            raw_p10 = base_preds * np.exp(-thresholds)
            raw_p90 = base_preds * np.exp(thresholds)
        else:
            # Scaled relative error: [y_hat * (1 - q), y_hat * (1 + q)]
            raw_p10 = base_preds * np.maximum(1.0 - thresholds, 0.0)
            raw_p90 = base_preds * (1.0 + thresholds)

        # Strictly enforce monotonicity and positive floor
        # 1.0 <= p10 <= p50 <= p90
        p10 = np.maximum(raw_p10, 1.0)
        p50 = np.maximum(p10, base_preds)
        p90 = np.maximum(p50, raw_p90)

        return {
            "p10": p10,
            "p50": p50,
            "p90": p90,
        }

    def predict_interval(
        self,
        X: Any,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Convenience method returning (p10, p50, p90) tuple of arrays."""
        quantiles = self.predict_quantiles(X)
        return quantiles["p10"], quantiles["p50"], quantiles["p90"]


class MondrianConformalPredictor(ConformalIntervalPredictor):
    """Mondrian (Size-Bucketed) Conformal Prediction Wrapper.

    Calibrates separate prediction intervals conditioned on functional size:
    - Small (<150 FP)
    - Medium (150-750 FP)
    - Large (>750 FP)
    """

    def __init__(
        self,
        estimator: Any = None,
        alpha: float = 0.20,
        score_type: Literal["log_residual", "scaled_relative"] = "log_residual",
        cal_size: float = 0.20,
        min_bucket_samples: int = 5,
        random_state: int | None = 42,
    ) -> None:
        super().__init__(
            estimator=estimator,
            alpha=alpha,
            mondrian=True,
            score_type=score_type,
            cal_size=cal_size,
            min_bucket_samples=min_bucket_samples,
            random_state=random_state,
        )


class SplitConformalPredictor(ConformalIntervalPredictor):
    """Standard Split Conformal Prediction Wrapper (marginal calibration).

    Computes a single global non-conformity threshold across all calibration samples.
    """

    def __init__(
        self,
        estimator: Any = None,
        alpha: float = 0.20,
        score_type: Literal["log_residual", "scaled_relative"] = "log_residual",
        cal_size: float = 0.20,
        random_state: int | None = 42,
    ) -> None:
        super().__init__(
            estimator=estimator,
            alpha=alpha,
            mondrian=False,
            score_type=score_type,
            cal_size=cal_size,
            random_state=random_state,
        )
