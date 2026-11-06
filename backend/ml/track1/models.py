"""Transparent, Interpretable, Monotonic Effort Estimation Models (Track 1).

Implements:
1. MonotonePowerLaw: E = a * S^b with b > 0 strictly enforced.
2. MultivariateMonotoneModel: E = a * S^b * D^c with b > 0 and bounded duration elasticity c,
   handling missing duration gracefully without synthetic imputation.
3. SegmentedMonotoneModel: Size-bucketed power law (<150 FP, 150-750 FP, >750 FP)
   with softplus boundary smoothing ensuring dE/dS > 0 everywhere.

Adheres strictly to docs/contracts/ml_contract.md:
- Strictly bans fabricated complexity factors (T01-T15, Transactions, Entities, etc.).
- Guaranteed positive and finite predictions (clamped to >= 1.0 hour).
- Zero synthetic imputation.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.base import BaseEstimator, RegressorMixin

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


def _softplus(z: np.ndarray, tau: float = 0.25) -> np.ndarray:
    """Numerically stable softplus function: tau * ln(1 + exp(z / tau))."""
    scaled = z / tau
    # For large positive scaled, softplus(scaled) ~ scaled
    # For large negative scaled, softplus(scaled) ~ exp(scaled)
    return tau * (np.log1p(np.exp(-np.abs(scaled))) + np.maximum(scaled, 0.0))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    """Numerically stable standard logistic sigmoid function."""
    return np.where(
        z >= 0,
        1.0 / (1.0 + np.exp(-z)),
        np.exp(z) / (1.0 + np.exp(z)),
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
            # Replace non-positive or non-finite values with NaN
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


class MonotonePowerLaw(BaseEstimator, RegressorMixin):
    """Transparent Monotone Power-Law Effort Estimation Model.

    Equation:
        E = a * S^b
    In log-space:
        ln(E) = beta_0 + b * ln(S)

    Enforces b >= b_min > 0 strictly via bounded Huber loss optimization in log-space,
    guaranteeing dE/dS = a * b * S^(b - 1) > 0 everywhere.
    """

    def __init__(
        self,
        b_min: float = 1e-4,
        delta: float = 1.35,
        max_iter: int = 500,
    ) -> None:
        """Initialize MonotonePowerLaw.

        Parameters
        ----------
        b_min : float
            Strict lower bound for size elasticity exponent b (> 0).
        delta : float
            Huber loss threshold parameter in log-space.
        max_iter : int
            Maximum iterations for L-BFGS-B optimizer.
        """
        self.b_min = b_min
        self.delta = delta
        self.max_iter = max_iter

        # Fitted parameters
        self.a_: float | None = None
        self.b_: float | None = None
        self.beta0_: float | None = None
        self.intercept_: float | None = None
        self.slope_: float | None = None
        self.loss_: float | None = None
        self.n_iter_: int = 0

    def fit(self, X: Any, y: Any) -> MonotonePowerLaw:
        """Fit MonotonePowerLaw on training data.

        Parameters
        ----------
        X : DataFrame | array-like of shape (n_samples, n_features)
            Training inputs containing size_fp / size_value.
        y : array-like of shape (n_samples,)
            Observed effort in person-hours.
        """
        size, _, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        log_s = np.log(size)
        log_y = np.log(y_arr)

        # Feature matrix in log-space: [1, ln(S)]
        Phi = np.column_stack([np.ones_like(log_s), log_s])

        def huber_objective_and_grad(w: np.ndarray) -> tuple[float, np.ndarray]:
            pred = Phi @ w
            r = log_y - pred
            abs_r = np.abs(r)
            loss = float(
                np.sum(
                    np.where(
                        abs_r <= self.delta,
                        0.5 * (r**2),
                        self.delta * (abs_r - 0.5 * self.delta),
                    )
                )
            )
            psi = np.where(abs_r <= self.delta, r, self.delta * np.sign(r))
            grad = -Phi.T @ psi
            return loss, grad

        init_w = np.array([float(np.mean(log_y) - np.mean(log_s)), 1.0])
        bounds = [(-np.inf, np.inf), (self.b_min, np.inf)]

        res = minimize(
            huber_objective_and_grad,
            init_w,
            jac=True,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": self.max_iter},
        )

        beta0, b = res.x
        self.beta0_ = float(beta0)
        self.b_ = float(b)
        self.a_ = float(np.exp(beta0))
        self.intercept_ = self.beta0_
        self.slope_ = self.b_
        self.loss_ = float(res.fun)
        self.n_iter_ = int(res.nit)

        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict effort in person-hours.

        Parameters
        ----------
        X : DataFrame | array-like of shape (n_samples, n_features)

        Returns
        -------
        np.ndarray of shape (n_samples,)
            Strictly positive predicted effort hours (>= 1.0).
        """
        if self.beta0_ is None or self.b_ is None:
            raise RuntimeError("MonotonePowerLaw must be fit before predict().")

        size, _, _ = validate_and_extract_inputs(X)
        log_pred = self.beta0_ + self.b_ * np.log(size)
        preds = np.exp(log_pred)
        return np.maximum(preds, 1.0)

    def derivative(self, X: Any) -> np.ndarray:
        """Compute analytical derivative dE/dS at input points.

        dE/dS = a * b * S^(b - 1) > 0 everywhere.
        """
        if self.a_ is None or self.b_ is None:
            raise RuntimeError("MonotonePowerLaw must be fit before derivative().")

        size, _, _ = validate_and_extract_inputs(X)
        deriv = self.a_ * self.b_ * (size ** (self.b_ - 1.0))
        return deriv


class MultivariateMonotoneModel(BaseEstimator, RegressorMixin):
    """Multivariate Monotone Effort Estimation Model with Duration Elasticity.

    Equation:
        When duration D is present:
            E = a * S^b * D^c
        When duration D is missing (NaN / null):
            E = a_base * S^b_base

    Constraints:
        - b > 0 and b_base > 0 strictly enforced.
        - c is bounded to physically realistic elasticity [c_min, c_max] (default [0.0, 1.2]).
        - Zero synthetic imputation: Projects without duration are evaluated using the
          marginal power law without fabricating synthetic duration values.
    """

    def __init__(
        self,
        b_min: float = 1e-4,
        c_bounds: tuple[float, float] = (0.0, 1.2),
        delta: float = 1.35,
        min_duration_samples: int = 5,
        max_iter: int = 500,
    ) -> None:
        """Initialize MultivariateMonotoneModel.

        Parameters
        ----------
        b_min : float
            Strict lower bound for size elasticity exponent b (> 0).
        c_bounds : tuple[float, float]
            Physically realistic bounds (c_min, c_max) for duration elasticity.
        delta : float
            Huber loss threshold parameter in log-space.
        min_duration_samples : int
            Minimum number of training samples with valid duration required to activate
            multivariate duration elasticity.
        max_iter : int
            Maximum iterations for L-BFGS-B optimizer.
        """
        self.b_min = b_min
        self.c_bounds = c_bounds
        self.delta = delta
        self.min_duration_samples = min_duration_samples
        self.max_iter = max_iter

        # Fitted parameters
        self.a_base_: float | None = None
        self.b_base_: float | None = None
        self.beta0_base_: float | None = None

        self.has_duration_: bool = False
        self.a_: float | None = None
        self.b_: float | None = None
        self.c_: float | None = None
        self.beta0_: float | None = None
        self.n_valid_duration_train_: int = 0

    def fit(self, X: Any, y: Any) -> MultivariateMonotoneModel:
        """Fit model on training data.

        Fits base marginal model on all training observations, and multivariate model
        on the subset of observations containing valid duration values.
        """
        size, duration, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        log_s = np.log(size)
        log_y = np.log(y_arr)

        # 1. Fit Base Marginal Model on all training rows
        Phi_base = np.column_stack([np.ones_like(log_s), log_s])

        def huber_base(w: np.ndarray) -> tuple[float, np.ndarray]:
            pred = Phi_base @ w
            r = log_y - pred
            abs_r = np.abs(r)
            loss = float(
                np.sum(
                    np.where(
                        abs_r <= self.delta,
                        0.5 * (r**2),
                        self.delta * (abs_r - 0.5 * self.delta),
                    )
                )
            )
            psi = np.where(abs_r <= self.delta, r, self.delta * np.sign(r))
            grad = -Phi_base.T @ psi
            return loss, grad

        init_w_base = np.array([float(np.mean(log_y) - np.mean(log_s)), 1.0])
        res_base = minimize(
            huber_base,
            init_w_base,
            jac=True,
            method="L-BFGS-B",
            bounds=[(-np.inf, np.inf), (self.b_min, np.inf)],
            options={"maxiter": self.max_iter},
        )

        beta0_b, b_b = res_base.x
        self.beta0_base_ = float(beta0_b)
        self.b_base_ = float(b_b)
        self.a_base_ = float(np.exp(beta0_b))

        # 2. Check for training samples with valid duration
        if duration is not None:
            valid_dur_mask = np.isfinite(duration) & (duration > 0)
            n_valid = int(np.sum(valid_dur_mask))
            self.n_valid_duration_train_ = n_valid
        else:
            valid_dur_mask = np.zeros(len(size), dtype=bool)
            self.n_valid_duration_train_ = 0

        if self.n_valid_duration_train_ >= self.min_duration_samples:
            self.has_duration_ = True
            log_s_val = log_s[valid_dur_mask]
            log_d_val = np.log(duration[valid_dur_mask])  # type: ignore[index]
            log_y_val = log_y[valid_dur_mask]

            Phi_multi = np.column_stack([np.ones_like(log_s_val), log_s_val, log_d_val])

            def huber_multi(w: np.ndarray) -> tuple[float, np.ndarray]:
                pred = Phi_multi @ w
                r = log_y_val - pred
                abs_r = np.abs(r)
                loss = float(
                    np.sum(
                        np.where(
                            abs_r <= self.delta,
                            0.5 * (r**2),
                            self.delta * (abs_r - 0.5 * self.delta),
                        )
                    )
                )
                psi = np.where(abs_r <= self.delta, r, self.delta * np.sign(r))
                grad = -Phi_multi.T @ psi
                return loss, grad

            init_w_m = np.array([self.beta0_base_, self.b_base_, 0.5])
            bounds_m = [
                (-np.inf, np.inf),
                (self.b_min, np.inf),
                (self.c_bounds[0], self.c_bounds[1]),
            ]

            res_multi = minimize(
                huber_multi,
                init_w_m,
                jac=True,
                method="L-BFGS-B",
                bounds=bounds_m,
                options={"maxiter": self.max_iter},
            )

            beta0_m, b_m, c_m = res_multi.x
            self.beta0_ = float(beta0_m)
            self.b_ = float(b_m)
            self.c_ = float(c_m)
            self.a_ = float(np.exp(beta0_m))
        else:
            self.has_duration_ = False
            self.beta0_ = self.beta0_base_
            self.b_ = self.b_base_
            self.c_ = 0.0
            self.a_ = self.a_base_

        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict effort in person-hours.

        Evaluates multivariate power-law when duration is valid; evaluates base
        marginal power-law when duration is missing, without imputation.
        """
        if self.a_base_ is None or self.b_base_ is None:
            raise RuntimeError("MultivariateMonotoneModel must be fit before predict().")

        size, duration, _ = validate_and_extract_inputs(X)
        preds = np.empty(len(size), dtype=np.float64)

        if self.has_duration_ and duration is not None:
            valid_dur_mask = np.isfinite(duration) & (duration > 0)
            # Evaluate base model for samples without valid duration
            if (~valid_dur_mask).any():
                s_missing = size[~valid_dur_mask]
                preds[~valid_dur_mask] = self.a_base_ * (s_missing**self.b_base_)

            # Evaluate multivariate model for samples with valid duration
            if valid_dur_mask.any():
                s_valid = size[valid_dur_mask]
                d_valid = duration[valid_dur_mask]
                preds[valid_dur_mask] = (
                    self.a_ * (s_valid**self.b_) * (d_valid**self.c_)  # type: ignore[operator]
                )
        else:
            preds[:] = self.a_base_ * (size**self.b_base_)

        return np.maximum(preds, 1.0)


class SegmentedMonotoneModel(BaseEstimator, RegressorMixin):
    """Size-Bucketed Monotone Model with Boundary Smoothing.

    Partitions functional size domain into three empirical buckets:
    - Small: S < 150 FP
    - Medium: 150 <= S <= 750 FP
    - Large: S > 750 FP

    Uses numerically stable softplus smoothing in log-space:
        ln(E(S)) = beta_0 + b_1 * phi_1(x) + b_2 * phi_2(x) + b_3 * phi_3(x)
    where:
        x = ln(S), k_1 = ln(150), k_2 = ln(750)
        phi_1(x) = x - h(x - k_1; tau)
        phi_2(x) = h(x - k_1; tau) - h(x - k_2; tau)
        phi_3(x) = h(x - k_2; tau)
        h(z; tau) = tau * ln(1 + exp(z / tau))

    Mathematical Invariant:
        The derivative d/dx ln(E) is a convex combination:
            f'(x) = b_1 * (1 - sigma_1) + b_2 * (sigma_1 - sigma_2) + b_3 * sigma_2
        Since k_1 < k_2, for all x:
            (1 - sigma_1) > 0, (sigma_1 - sigma_2) >= 0, sigma_2 > 0
            and their sum equals 1.
        Because b_1, b_2, b_3 >= b_min > 0:
            dE/dS = (E(S) / S) * f'(ln(S)) >= (E(S) / S) * b_min > 0 everywhere!
        Guarantees strict monotonicity and C^inf smoothness across all size domains.
    """

    def __init__(
        self,
        bucket_cuts: tuple[float, float] = (150.0, 750.0),
        tau: float = 0.25,
        b_min: float = 1e-4,
        delta: float = 1.35,
        max_iter: int = 500,
    ) -> None:
        """Initialize SegmentedMonotoneModel.

        Parameters
        ----------
        bucket_cuts : tuple[float, float]
            Size cut points (K1, K2) in Function Points separating small, medium, and large buckets.
        tau : float
            Boundary smoothing scale parameter (controls transition width in log-space).
        b_min : float
            Strict lower bound for bucket elasticity slopes (b1, b2, b3 >= b_min > 0).
        delta : float
            Huber loss threshold parameter in log-space.
        max_iter : int
            Maximum iterations for L-BFGS-B optimizer.
        """
        self.bucket_cuts = bucket_cuts
        self.tau = tau
        self.b_min = b_min
        self.delta = delta
        self.max_iter = max_iter

        # Precompute log cut points
        self.k1_ = float(np.log(bucket_cuts[0]))
        self.k2_ = float(np.log(bucket_cuts[1]))

        # Fitted parameters
        self.beta0_: float | None = None
        self.b1_: float | None = None
        self.b2_: float | None = None
        self.b3_: float | None = None
        self.loss_: float | None = None
        self.n_iter_: int = 0

    def _compute_basis(self, log_s: np.ndarray) -> np.ndarray:
        """Compute the 4 smooth basis functions in log-space."""
        h1 = _softplus(log_s - self.k1_, self.tau)
        h2 = _softplus(log_s - self.k2_, self.tau)

        phi0 = np.ones_like(log_s)
        phi1 = log_s - h1
        phi2 = h1 - h2
        phi3 = h2

        return np.column_stack([phi0, phi1, phi2, phi3])

    def fit(self, X: Any, y: Any) -> SegmentedMonotoneModel:
        """Fit SegmentedMonotoneModel on training data.

        Globally convex optimization via L-BFGS-B with exact analytical gradients.
        """
        size, _, _ = validate_and_extract_inputs(X)
        y_arr = _check_target(y, len(size))

        log_s = np.log(size)
        log_y = np.log(y_arr)

        Phi = self._compute_basis(log_s)

        def huber_objective_and_grad(w: np.ndarray) -> tuple[float, np.ndarray]:
            pred = Phi @ w
            r = log_y - pred
            abs_r = np.abs(r)
            loss = float(
                np.sum(
                    np.where(
                        abs_r <= self.delta,
                        0.5 * (r**2),
                        self.delta * (abs_r - 0.5 * self.delta),
                    )
                )
            )
            psi = np.where(abs_r <= self.delta, r, self.delta * np.sign(r))
            grad = -Phi.T @ psi
            return loss, grad

        init_w = np.array([float(np.mean(log_y) - np.mean(log_s)), 0.8, 0.8, 0.8])
        bounds = [
            (-np.inf, np.inf),
            (self.b_min, np.inf),
            (self.b_min, np.inf),
            (self.b_min, np.inf),
        ]

        res = minimize(
            huber_objective_and_grad,
            init_w,
            jac=True,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": self.max_iter},
        )

        beta0, b1, b2, b3 = res.x
        self.beta0_ = float(beta0)
        self.b1_ = float(b1)
        self.b2_ = float(b2)
        self.b3_ = float(b3)
        self.loss_ = float(res.fun)
        self.n_iter_ = int(res.nit)

        return self

    def predict(self, X: Any) -> np.ndarray:
        """Predict effort in person-hours.

        Strictly monotonic, guaranteed positive and finite (>= 1.0).
        """
        if (
            self.beta0_ is None
            or self.b1_ is None
            or self.b2_ is None
            or self.b3_ is None
        ):
            raise RuntimeError("SegmentedMonotoneModel must be fit before predict().")

        size, _, _ = validate_and_extract_inputs(X)
        log_s = np.log(size)
        Phi = self._compute_basis(log_s)
        w = np.array([self.beta0_, self.b1_, self.b2_, self.b3_])
        log_pred = Phi @ w
        preds = np.exp(log_pred)
        return np.maximum(preds, 1.0)

    def derivative(self, X: Any) -> np.ndarray:
        """Compute analytical derivative dE/dS at input points.

        Returns
        -------
        np.ndarray
            dE/dS values, strictly positive (> 0) everywhere.
        """
        if (
            self.beta0_ is None
            or self.b1_ is None
            or self.b2_ is None
            or self.b3_ is None
        ):
            raise RuntimeError("SegmentedMonotoneModel must be fit before derivative().")

        size, _, _ = validate_and_extract_inputs(X)
        log_s = np.log(size)
        sigma1 = _sigmoid((log_s - self.k1_) / self.tau)
        sigma2 = _sigmoid((log_s - self.k2_) / self.tau)

        # Convex combination of slopes
        f_prime = (
            self.b1_ * (1.0 - sigma1)
            + self.b2_ * (sigma1 - sigma2)
            + self.b3_ * sigma2
        )

        preds = self.predict(X)
        deriv = (preds / size) * f_prime
        return deriv
