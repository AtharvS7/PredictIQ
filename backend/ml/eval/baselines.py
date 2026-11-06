"""Baseline effort estimation predictors.

Adheres strictly to docs/contracts/evaluation_protocol.md and docs/contracts/ml_contract.md.
Implements:
1. MedianDummyPredictor: Constant training fold median effort.
2. MedianProductivityPredictor: Median productivity multiplier P * Size.
3. AlbrechtNominalPredictor / COCOMONominalPredictor / PowerLawBaseline: E = a * S^b via log-log OLS.
4. LogLinearBaseline: OLS on log(size) and optional log(duration).
5. HuberPowerLawBaseline: Huber robust regression on log-log transform.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.linear_model import HuberRegressor, LinearRegression


def _extract_size_and_duration(
    X: Any,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Extract size_value and optional duration_months from DataFrame or ndarray."""
    if isinstance(X, pd.DataFrame):
        if "size_value" in X.columns:
            size = X["size_value"].to_numpy(dtype=np.float64)
        else:
            # Fall back to first column
            size = X.iloc[:, 0].to_numpy(dtype=np.float64)

        if "duration_months" in X.columns:
            duration = X["duration_months"].to_numpy(dtype=np.float64)
            # If all are NaN, treat as None
            if np.isnan(duration).all():
                duration = None
        elif X.shape[1] > 1:
            duration = X.iloc[:, 1].to_numpy(dtype=np.float64)
        else:
            duration = None
    else:
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 1:
            size = arr
            duration = None
        elif arr.shape[1] == 1:
            size = arr[:, 0]
            duration = None
        else:
            size = arr[:, 0]
            duration = arr[:, 1]

    if (size <= 0).any() or not np.isfinite(size).all():
        raise ValueError("size values must be positive and finite.")

    return size, duration


class BaseBaseline(BaseEstimator, RegressorMixin):
    """Base class for PredictIQ baseline models."""

    def __init__(self) -> None:
        pass

    def fit(self, X: Any, y: Any) -> "BaseBaseline":
        raise NotImplementedError

    def predict(self, X: Any) -> np.ndarray:
        raise NotImplementedError


class MedianDummyPredictor(BaseBaseline):
    """Baseline 1: Constant median of training fold target effort."""

    def __init__(self) -> None:
        super().__init__()
        self.median_effort_: float | None = None

    def fit(self, X: Any, y: Any) -> "MedianDummyPredictor":
        y_arr = np.asarray(y, dtype=np.float64).ravel()
        if len(y_arr) == 0:
            raise ValueError("Training target y cannot be empty.")
        self.median_effort_ = float(np.median(y_arr))
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self.median_effort_ is None:
            raise RuntimeError("MedianDummyPredictor must be fit before predict().")
        n_samples = len(X)
        return np.full(n_samples, self.median_effort_, dtype=np.float64)


class MedianProductivityPredictor(BaseBaseline):
    """Baseline 2: Median productivity multiplier P * Size."""

    def __init__(self) -> None:
        super().__init__()
        self.median_productivity_: float | None = None

    def fit(self, X: Any, y: Any) -> "MedianProductivityPredictor":
        size, _ = _extract_size_and_duration(X)
        y_arr = np.asarray(y, dtype=np.float64).ravel()
        if len(size) != len(y_arr):
            raise ValueError("X and y length mismatch.")

        prod = y_arr / size
        self.median_productivity_ = float(np.median(prod))
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self.median_productivity_ is None:
            raise RuntimeError("MedianProductivityPredictor must be fit before predict().")
        size, _ = _extract_size_and_duration(X)
        preds = self.median_productivity_ * size
        return np.maximum(preds, 1.0)


class AlbrechtNominalPredictor(BaseBaseline):
    """Baseline 3: Empirical power law E = a * S^b fitted via OLS in log space.

    ln(E) = ln(a) + b * ln(S) => E = exp(intercept + slope * ln(S))
    Also aliased as COCOMONominalPredictor and PowerLawBaseline.
    """

    def __init__(self) -> None:
        super().__init__()
        self.a_: float | None = None
        self.b_: float | None = None
        self.intercept_: float | None = None
        self.slope_: float | None = None

    def fit(self, X: Any, y: Any) -> "AlbrechtNominalPredictor":
        size, _ = _extract_size_and_duration(X)
        y_arr = np.asarray(y, dtype=np.float64).ravel()
        if len(size) != len(y_arr):
            raise ValueError("X and y length mismatch.")
        if (y_arr <= 0).any():
            raise ValueError("Effort y must be strictly positive for log-log regression.")

        log_s = np.log(size).reshape(-1, 1)
        log_y = np.log(y_arr)

        lr = LinearRegression()
        lr.fit(log_s, log_y)

        self.slope_ = float(lr.coef_[0])
        self.intercept_ = float(lr.intercept_)
        self.b_ = self.slope_
        self.a_ = float(np.exp(self.intercept_))
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self.intercept_ is None or self.slope_ is None:
            raise RuntimeError("Model must be fit before predict().")
        size, _ = _extract_size_and_duration(X)
        log_s = np.log(size)
        log_pred = self.intercept_ + self.slope_ * log_s
        preds = np.exp(log_pred)
        return np.maximum(preds, 1.0)


# Aliases for baseline 3
COCOMONominalPredictor = AlbrechtNominalPredictor
PowerLawBaseline = AlbrechtNominalPredictor


class LogLinearBaseline(BaseBaseline):
    """Baseline 4: Ordinary Least Squares on log(S) and optional log(duration).

    If duration is present in training data, fits:
        ln(E) = beta_0 + beta_1 * ln(S) + beta_2 * ln(duration)
    Imputes missing duration values with training median log-duration.
    """

    def __init__(self) -> None:
        super().__init__()
        self.model_: LinearRegression | None = None
        self.has_duration_: bool = False
        self.median_log_duration_: float | None = None

    def fit(self, X: Any, y: Any) -> "LogLinearBaseline":
        size, duration = _extract_size_and_duration(X)
        y_arr = np.asarray(y, dtype=np.float64).ravel()
        if len(size) != len(y_arr):
            raise ValueError("X and y length mismatch.")

        log_s = np.log(size)
        log_y = np.log(y_arr)

        if duration is not None:
            valid_dur_mask = np.isfinite(duration) & (duration > 0)
            if valid_dur_mask.sum() >= 5:
                self.has_duration_ = True
                valid_log_dur = np.log(duration[valid_dur_mask])
                self.median_log_duration_ = float(np.median(valid_log_dur))

                # Impute missing/non-positive duration with median log duration
                log_d = np.where(valid_dur_mask, np.log(np.maximum(duration, 1e-3)), self.median_log_duration_)
                feat_matrix = np.column_stack([log_s, log_d])
            else:
                self.has_duration_ = False
                feat_matrix = log_s.reshape(-1, 1)
        else:
            self.has_duration_ = False
            feat_matrix = log_s.reshape(-1, 1)

        self.model_ = LinearRegression()
        self.model_.fit(feat_matrix, log_y)
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self.model_ is None:
            raise RuntimeError("LogLinearBaseline must be fit before predict().")

        size, duration = _extract_size_and_duration(X)
        log_s = np.log(size)

        if self.has_duration_:
            if duration is not None:
                valid_dur_mask = np.isfinite(duration) & (duration > 0)
                fallback = self.median_log_duration_ if self.median_log_duration_ is not None else 0.0
                log_d = np.where(valid_dur_mask, np.log(np.maximum(duration, 1e-3)), fallback)
            else:
                fallback = self.median_log_duration_ if self.median_log_duration_ is not None else 0.0
                log_d = np.full(len(size), fallback)
            feat_matrix = np.column_stack([log_s, log_d])
        else:
            feat_matrix = log_s.reshape(-1, 1)

        log_pred = self.model_.predict(feat_matrix)
        preds = np.exp(log_pred)
        return np.maximum(preds, 1.0)


class HuberPowerLawBaseline(BaseBaseline):
    """Baseline 5: Huber robust regression on log-log transform."""

    def __init__(self, epsilon: float = 1.35, alpha: float = 0.0001) -> None:
        super().__init__()
        self.epsilon = epsilon
        self.alpha = alpha
        self.model_: HuberRegressor | None = None

    def fit(self, X: Any, y: Any) -> "HuberPowerLawBaseline":
        size, _ = _extract_size_and_duration(X)
        y_arr = np.asarray(y, dtype=np.float64).ravel()
        if len(size) != len(y_arr):
            raise ValueError("X and y length mismatch.")

        log_s = np.log(size).reshape(-1, 1)
        log_y = np.log(y_arr)

        self.model_ = HuberRegressor(epsilon=self.epsilon, alpha=self.alpha)
        self.model_.fit(log_s, log_y)
        return self

    def predict(self, X: Any) -> np.ndarray:
        if self.model_ is None:
            raise RuntimeError("HuberPowerLawBaseline must be fit before predict().")
        size, _ = _extract_size_and_duration(X)
        log_s = np.log(size).reshape(-1, 1)
        log_pred = self.model_.predict(log_s)
        preds = np.exp(log_pred)
        return np.maximum(preds, 1.0)
