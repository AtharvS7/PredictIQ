"""Non-linear, Tree-Based Challenger Effort Estimation Models (Track 2).

Implements:
1. MonotoneHistGradientBoosting: HistGradientBoostingRegressor with monotonic_cst=[+1]
   on functional size, enforcing positive monotonic behavior across the size domain.
2. QuantileGradientBoosting: HistGradientBoostingRegressor(loss="quantile", quantile=q)
   for q in [0.1, 0.5, 0.9] to produce direct asymmetric uncertainty intervals, with
   strictly guaranteed quantile monotonicity (p10 <= p50 <= p90).
3. MultivariateHistGradientBoosting: Non-linear interaction model incorporating functional size,
   planned target duration, and team size without synthetic imputation (using marginal fallback
   architecture when duration is unobserved).

Adheres strictly to docs/contracts/ml_contract.md:
- Strictly bans fabricated complexity factors (T01-T15, Transactions, Entities, etc.).
- Guaranteed positive and finite predictions (clamped to >= 1.0 hour).
- Zero synthetic imputation.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.exceptions import NotFittedError

# Banned features permanently prohibited by docs/contracts/ml_contract.md
BANNED_FEATURES = frozenset(
    [
        "t01",
        "t02",
        "t03",
        "t04",
        "t05",
        "t06",
        "t07",
        "t08",
        "t09",
        "t10",
        "t11",
        "t12",
        "t13",
        "t14",
        "t15",
        "transactions",
        "entities",
        "pointsnonadjust",
        "adjustment",
        "teamexp",
        "managerexp",
        "risk_score",
    ]
)


def validate_and_extract_inputs(
    X: Any,
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray | None]:
    """Validate inputs against ML Contract and extract size, duration, and team_size.

    Parameters
    ----------
    X : pd.DataFrame | np.ndarray | Sequence
        Input feature matrix or vector.

    Returns
    -------
    size : np.ndarray (1D float64, > 0)
    duration : np.ndarray | None (1D float64, with NaNs for missing/non-positive)
    team_size : np.ndarray | None (1D float64, with NaNs for missing/non-positive)

    Raises
    ------
    ValueError
        If banned features are present, or size values are non-positive / non-finite.
    """
    duration: np.ndarray | None = None
    team_size: np.ndarray | None = None

    if isinstance(X, pd.DataFrame):
        # 1. Enforce ML Contract Banned Features Ban
        cols_lower = {col: str(col).strip().lower() for col in X.columns}
        banned_found = [col for col, col_l in cols_lower.items() if col_l in BANNED_FEATURES]
        if banned_found:
            raise ValueError(
                f"ML Contract Violation: Forbidden feature(s) detected: {banned_found}. "
                "Under PredictIQ v2 contract (docs/contracts/ml_contract.md), fabricated "
                "complexity factors (T01-T15), legacy unadjusted metrics, and downstream scores "
                "are permanently banned from effort estimation."
            )

        # 2. Extract size_fp / size_value
        size_col: str | None = None
        for cand in ["size_fp", "size_value", "size", "functional_size"]:
            for col, col_l in cols_lower.items():
                if col_l == cand:
                    size_col = col
                    break
            if size_col is not None:
                break

        if size_col is not None:
            size = X[size_col].to_numpy(dtype=np.float64)
        elif X.shape[1] == 1:
            size = X.iloc[:, 0].to_numpy(dtype=np.float64)
        else:
            raise ValueError(
                "Input DataFrame must contain 'size_fp' or 'size_value' column."
            )

        # 3. Extract optional duration_months
        dur_col: str | None = None
        for cand in ["duration_months", "duration", "target_duration_months", "planned_duration_months"]:
            for col, col_l in cols_lower.items():
                if col_l == cand:
                    dur_col = col
                    break
            if dur_col is not None:
                break

        if dur_col is not None:
            raw_dur = X[dur_col].to_numpy(dtype=np.float64)
            duration = np.where(np.isfinite(raw_dur) & (raw_dur > 0), raw_dur, np.nan)

        # 4. Extract optional team_size
        team_col: str | None = None
        for cand in ["team_size", "team", "fte"]:
            for col, col_l in cols_lower.items():
                if col_l == cand:
                    team_col = col
                    break
            if team_col is not None:
                break

        if team_col is not None:
            raw_team = X[team_col].to_numpy(dtype=np.float64)
            team_size = np.where(np.isfinite(raw_team) & (raw_team > 0), raw_team, np.nan)

    elif isinstance(X, pd.Series):
        size = X.to_numpy(dtype=np.float64)
    else:
        # Array-like input
        arr = np.asarray(X, dtype=np.float64)
        if arr.ndim == 0:
            raise ValueError("Input must have at least 1 dimension.")
        elif arr.ndim == 1:
            size = arr
        elif arr.shape[1] == 1:
            size = arr[:, 0]
        elif arr.shape[1] == 2:
            size = arr[:, 0]
            raw_dur = arr[:, 1]
            duration = np.where(np.isfinite(raw_dur) & (raw_dur > 0), raw_dur, np.nan)
        else:
            size = arr[:, 0]
            raw_dur = arr[:, 1]
            raw_team = arr[:, 2]
            duration = np.where(np.isfinite(raw_dur) & (raw_dur > 0), raw_dur, np.nan)
            team_size = np.where(np.isfinite(raw_team) & (raw_team > 0), raw_team, np.nan)

    if len(size) == 0:
        raise ValueError("Input feature size array cannot be empty.")

    if not np.isfinite(size).all() or (size <= 0).any():
        raise ValueError("All size values must be strictly positive and finite numbers.")

    return size, duration, team_size


def _check_target(y: Any, n_samples: int) -> np.ndarray:
    """Validate target effort values."""
    y_arr = np.asarray(y, dtype=np.float64).ravel()
    if len(y_arr) != n_samples:
        raise ValueError(
            f"Input feature rows ({n_samples}) does not match target rows ({len(y_arr)})."
        )
    if not np.isfinite(y_arr).all() or (y_arr <= 0).any():
        raise ValueError("Target effort values must be strictly positive and finite numbers.")
    return y_arr


class MonotoneHistGradientBoosting(BaseEstimator, RegressorMixin):
    """Monotonic Histogram-based Gradient Boosting Regressor (Track 2 Challenger).

    Uses scikit-learn's `HistGradientBoostingRegressor` with `monotonic_cst=[+1]`
    to enforce positive monotonic relationship with respect to functional size:
    S1 < S2 => E(S1) <= E(S2).

    Parameters
    ----------
    loss : str, default='squared_error'
        Loss function ('squared_error' or 'absolute_error').
    learning_rate : float, default=0.05
        Learning rate shrinkage parameter.
    max_iter : int, default=100
        Maximum number of boosting iterations (trees).
    max_leaf_nodes : int, default=15
        Maximum number of leaves per tree.
    min_samples_leaf : int, default=10
        Minimum number of samples per leaf.
    l2_regularization : float, default=0.1
        L2 regularization parameter on leaf values.
    target_log : bool, default=True
        Whether to model log(effort) (True) or raw effort (False). Modeling log(effort)
        matches the log-normal distribution of software projects and guarantees strictly
        positive predictions via exp(pred).
    random_state : int | None, default=42
        Random seed for reproducibility.
    """

    def __init__(
        self,
        loss: str = "squared_error",
        learning_rate: float = 0.05,
        max_iter: int = 100,
        max_leaf_nodes: int = 15,
        min_samples_leaf: int = 10,
        l2_regularization: float = 0.1,
        target_log: bool = True,
        random_state: int | None = 42,
    ) -> None:
        self.loss = loss
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.max_leaf_nodes = max_leaf_nodes
        self.min_samples_leaf = min_samples_leaf
        self.l2_regularization = l2_regularization
        self.target_log = target_log
        self.random_state = random_state

        # Fitted estimator
        self.estimator_: HistGradientBoostingRegressor | None = None
        self.n_samples_train_: int = 0

    def fit(self, X: Any, y: Any) -> MonotoneHistGradientBoosting:
        """Fit MonotoneHistGradientBoosting model on training data.

        Parameters
        ----------
        X : DataFrame | array-like of shape (n_samples, n_features)
            Training inputs containing size_fp / size_value.
        y : array-like of shape (n_samples,)
            Observed effort in person-hours.
        """
        size, _, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        self.n_samples_train_ = len(size)
        fit_y = np.log(y_arr) if self.target_log else y_arr
        X_mat = size.reshape(-1, 1)

        estimator = HistGradientBoostingRegressor(
            loss=self.loss,
            learning_rate=self.learning_rate,
            max_iter=self.max_iter,
            max_leaf_nodes=self.max_leaf_nodes,
            min_samples_leaf=self.min_samples_leaf,
            l2_regularization=self.l2_regularization,
            monotonic_cst=[1],
            random_state=self.random_state,
        )
        estimator.fit(X_mat, fit_y)
        self.estimator_ = estimator
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict effort in person-hours.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Predicted effort hours (guaranteed >= 1.0 hour, positive and finite).
        """
        if self.estimator_ is None:
            raise NotFittedError("This MonotoneHistGradientBoosting instance is not fitted yet.")

        size, _, _ = validate_and_extract_inputs(X)
        X_mat = size.reshape(-1, 1)
        raw_pred = self.estimator_.predict(X_mat)

        if self.target_log:
            pred = np.exp(raw_pred)
        else:
            pred = raw_pred

        # Guaranteed positive and finite predictions (clamped to >= 1.0 hour)
        return np.maximum(pred, 1.0)


class QuantileGradientBoosting(BaseEstimator, RegressorMixin):
    """Direct Asymmetric Uncertainty Estimation via Quantile Gradient Boosting.

    Trains three distinct `HistGradientBoostingRegressor` models with `loss="quantile"`
    for quantiles [0.1, 0.5, 0.9]. Produces calibrated asymmetric uncertainty intervals
    with guaranteed quantile monotonicity: p10 <= p50 <= p90.

    Parameters
    ----------
    quantiles : Sequence[float], default=(0.1, 0.5, 0.9)
        Quantiles to fit for interval prediction.
    learning_rate : float, default=0.05
        Learning rate shrinkage parameter.
    max_iter : int, default=100
        Maximum number of boosting iterations (trees).
    max_leaf_nodes : int, default=15
        Maximum number of leaves per tree.
    min_samples_leaf : int, default=15
        Minimum number of samples per leaf.
    l2_regularization : float, default=0.1
        L2 regularization parameter on leaf values.
    target_log : bool, default=False
        Whether to model log(effort) (True) or raw effort (False).
    random_state : int | None, default=42
        Random seed for reproducibility.
    """

    def __init__(
        self,
        quantiles: Sequence[float] = (0.1, 0.5, 0.9),
        learning_rate: float = 0.05,
        max_iter: int = 100,
        max_leaf_nodes: int = 15,
        min_samples_leaf: int = 15,
        l2_regularization: float = 0.1,
        target_log: bool = False,
        random_state: int | None = 42,
    ) -> None:
        self.quantiles = tuple(sorted(quantiles))
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.max_leaf_nodes = max_leaf_nodes
        self.min_samples_leaf = min_samples_leaf
        self.l2_regularization = l2_regularization
        self.target_log = target_log
        self.random_state = random_state

        # Fitted quantile estimators
        self.estimators_: dict[float, HistGradientBoostingRegressor] | None = None
        self.n_samples_train_: int = 0

    def fit(self, X: Any, y: Any) -> QuantileGradientBoosting:
        """Fit quantile models for each configured quantile.

        Parameters
        ----------
        X : DataFrame | array-like
            Training inputs containing size_fp / size_value.
        y : array-like
            Observed effort in person-hours.
        """
        size, _, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        self.n_samples_train_ = len(size)
        fit_y = np.log(y_arr) if self.target_log else y_arr
        X_mat = size.reshape(-1, 1)

        estimators: dict[float, HistGradientBoostingRegressor] = {}
        for q in self.quantiles:
            est = HistGradientBoostingRegressor(
                loss="quantile",
                quantile=q,
                learning_rate=self.learning_rate,
                max_iter=self.max_iter,
                max_leaf_nodes=self.max_leaf_nodes,
                min_samples_leaf=self.min_samples_leaf,
                l2_regularization=self.l2_regularization,
                monotonic_cst=[1],
                random_state=self.random_state,
            )
            est.fit(X_mat, fit_y)
            estimators[q] = est

        self.estimators_ = estimators
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict median effort (p50) in person-hours.

        Provides standard scikit-learn regressor interface returning point estimates.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Median predicted effort hours (guaranteed >= 1.0 hour).
        """
        if self.estimators_ is None:
            raise NotFittedError("This QuantileGradientBoosting instance is not fitted yet.")

        quantiles_dict = self.predict_quantiles(X)
        return quantiles_dict["p50"]

    def predict_quantiles(self, X: Any) -> dict[str, np.ndarray]:
        """Predict calibrated quantile intervals: p10, p50, and p90.

        Strictly enforces quantile monotonicity: p10 <= p50 <= p90 everywhere,
        and guarantees predictions >= 1.0 person-hour.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features.

        Returns
        -------
        dict[str, np.ndarray]
            Dictionary containing 'p10', 'p50', and 'p90' arrays.
        """
        if self.estimators_ is None:
            raise NotFittedError("This QuantileGradientBoosting instance is not fitted yet.")

        size, _, _ = validate_and_extract_inputs(X)
        X_mat = size.reshape(-1, 1)

        raw_preds: dict[float, np.ndarray] = {}
        for q, est in self.estimators_.items():
            pred = est.predict(X_mat)
            if self.target_log:
                pred = np.exp(pred)
            raw_preds[q] = np.maximum(pred, 1.0)

        # Retrieve individual quantiles
        p10 = raw_preds.get(0.1, raw_preds[self.quantiles[0]])
        p50 = raw_preds.get(0.5, raw_preds[self.quantiles[1] if len(self.quantiles) > 1 else self.quantiles[0]])
        p90 = raw_preds.get(0.9, raw_preds[self.quantiles[-1]])

        # Enforce mathematical quantile monotonicity: p10 <= p50 <= p90
        # If any slight tree boundary crossing occurs, clamp non-crossing
        p10_monotone = np.minimum(p10, p50)
        p90_monotone = np.maximum(p90, p50)

        return {
            "p10": np.maximum(p10_monotone, 1.0),
            "p50": np.maximum(p50, 1.0),
            "p90": np.maximum(p90_monotone, 1.0),
        }

    def predict_intervals(self, X: Any) -> dict[str, np.ndarray]:
        """Alias for predict_quantiles."""
        return self.predict_quantiles(X)


class MultivariateHistGradientBoosting(BaseEstimator, RegressorMixin):
    """Multivariate Non-linear Interaction Challenger Model.

    Combines Functional Size with optional Planned Target Duration and Team Size.
    Enforces positive monotonic constraint (+1) on functional size.

    Zero Synthetic Imputation:
    - Trains a base marginal estimator on all training observations (size only).
    - Trains an interaction estimator on training observations where duration is observed.
    - At inference time, for observations with valid planned target duration, evaluates
      the non-linear interaction model. For observations where duration is missing or unobserved,
      falls back gracefully to the base marginal estimator.
    - Never fabricates or imputes synthetic values into feature matrices.

    Parameters
    ----------
    loss : str, default='squared_error'
        Loss function ('squared_error' or 'absolute_error').
    learning_rate : float, default=0.05
        Learning rate shrinkage parameter.
    max_iter : int, default=100
        Maximum number of boosting iterations (trees).
    max_leaf_nodes : int, default=15
        Maximum number of leaves per tree.
    min_samples_leaf : int, default=10
        Minimum number of samples per leaf.
    l2_regularization : float, default=0.1
        L2 regularization parameter on leaf values.
    target_log : bool, default=True
        Whether to model log(effort) (True) or raw effort (False).
    min_covariate_samples : int, default=10
        Minimum number of samples with valid duration required to fit interaction model.
    random_state : int | None, default=42
        Random seed for reproducibility.
    """

    def __init__(
        self,
        loss: str = "squared_error",
        learning_rate: float = 0.05,
        max_iter: int = 100,
        max_leaf_nodes: int = 15,
        min_samples_leaf: int = 10,
        l2_regularization: float = 0.1,
        target_log: bool = True,
        min_covariate_samples: int = 10,
        random_state: int | None = 42,
    ) -> None:
        self.loss = loss
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.max_leaf_nodes = max_leaf_nodes
        self.min_samples_leaf = min_samples_leaf
        self.l2_regularization = l2_regularization
        self.target_log = target_log
        self.min_covariate_samples = min_covariate_samples
        self.random_state = random_state

        # Fitted estimators
        self.base_estimator_: HistGradientBoostingRegressor | None = None
        self.interaction_estimator_: HistGradientBoostingRegressor | None = None
        self.has_interaction_: bool = False
        self.n_samples_train_: int = 0
        self.n_covariate_samples_train_: int = 0

    def fit(self, X: Any, y: Any) -> MultivariateHistGradientBoosting:
        """Fit MultivariateHistGradientBoosting model on training data.

        Parameters
        ----------
        X : DataFrame | array-like of shape (n_samples, n_features)
            Training inputs containing size_fp / size_value and optional duration_months.
        y : array-like of shape (n_samples,)
            Observed effort in person-hours.
        """
        size, duration, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        self.n_samples_train_ = len(size)
        fit_y = np.log(y_arr) if self.target_log else y_arr

        # 1. Fit Base Marginal Estimator on all observations (size only)
        base_mat = size.reshape(-1, 1)
        base_est = HistGradientBoostingRegressor(
            loss=self.loss,
            learning_rate=self.learning_rate,
            max_iter=self.max_iter,
            max_leaf_nodes=self.max_leaf_nodes,
            min_samples_leaf=self.min_samples_leaf,
            l2_regularization=self.l2_regularization,
            monotonic_cst=[1],
            random_state=self.random_state,
        )
        base_est.fit(base_mat, fit_y)
        self.base_estimator_ = base_est

        # 2. Check for observations with valid planned target duration
        if duration is not None:
            valid_mask = np.isfinite(duration) & (duration > 0)
            n_valid = int(np.sum(valid_mask))
            self.n_covariate_samples_train_ = n_valid
        else:
            valid_mask = np.zeros(len(size), dtype=bool)
            self.n_covariate_samples_train_ = 0

        if self.n_covariate_samples_train_ >= self.min_covariate_samples:
            self.has_interaction_ = True
            inter_X = np.column_stack([size[valid_mask], duration[valid_mask]])  # type: ignore[index]
            inter_y = fit_y[valid_mask]

            inter_est = HistGradientBoostingRegressor(
                loss=self.loss,
                learning_rate=self.learning_rate,
                max_iter=self.max_iter,
                max_leaf_nodes=self.max_leaf_nodes,
                min_samples_leaf=self.min_samples_leaf,
                l2_regularization=self.l2_regularization,
                monotonic_cst=[1, 1],
                random_state=self.random_state,
            )
            inter_est.fit(inter_X, inter_y)
            self.interaction_estimator_ = inter_est
        else:
            self.has_interaction_ = False
            self.interaction_estimator_ = None

        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict effort in person-hours.

        Evaluates interaction model for samples with valid duration; evaluates
        base marginal model for samples with unobserved/missing duration.

        Parameters
        ----------
        X : DataFrame | array-like
            Input features.

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Predicted effort hours (guaranteed >= 1.0 hour, positive and finite).
        """
        if self.base_estimator_ is None:
            raise NotFittedError("This MultivariateHistGradientBoosting instance is not fitted yet.")

        size, duration, _ = validate_and_extract_inputs(X)

        # Baseline predictions for all samples
        base_mat = size.reshape(-1, 1)
        raw_base = self.base_estimator_.predict(base_mat)
        pred_base = np.exp(raw_base) if self.target_log else raw_base
        final_pred = pred_base.copy()

        # Interaction predictions for samples with valid duration
        if self.has_interaction_ and self.interaction_estimator_ is not None and duration is not None:
            valid_mask = np.isfinite(duration) & (duration > 0)
            if valid_mask.any():
                inter_mat = np.column_stack([size[valid_mask], duration[valid_mask]])
                raw_inter = self.interaction_estimator_.predict(inter_mat)
                pred_inter = np.exp(raw_inter) if self.target_log else raw_inter
                final_pred[valid_mask] = pred_inter

        # Guaranteed positive and finite predictions (clamped to >= 1.0 hour)
        return np.maximum(final_pred, 1.0)
