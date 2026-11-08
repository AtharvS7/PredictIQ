"""Organizational Calibration Service (Checkpoint S06).

Implements Empirical Bayes shrinkage of the global Monotone Power-Law prediction model
toward an organization's historical completed project actuals.

Mathematical Formulation:
1. Global power law:
       E = a_global * S^(b_global)
       ln(E) = beta0_global + b_global * ln(S)
2. Organization productivity residual on k past projects:
       r_i = ln(Y_i) - (beta0_global + b_global * ln(S_i))
       Delta_log_a = mean(r_i)
3. Empirical Bayes shrinkage factor:
       w = k / (k + sigma2 / tau2)
   where sigma2 is within-org residual variance (~0.441) and tau2 is between-org
   intercept variance (~0.171), yielding sigma2 / tau2 ~= 2.57.
4. Calibrated parameters:
       beta0_cal = beta0_global + w * Delta_log_a
       a_cal = exp(beta0_cal)
       b_cal = b_global  (slope is strictly preserved to prevent overfitting on small k)
5. Quantile scaling:
       cal_ratio = a_cal / a_global = exp(w * Delta_log_a)
       P_q_cal = P_q_global * cal_ratio
   Guarantees 1.0 <= P10 <= P25 <= P50 <= P75 <= P90 strictly everywhere.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

SIGMA2_WITHIN: float = 0.441
TAU2_BETWEEN: float = 0.171
VARIANCE_RATIO: float = SIGMA2_WITHIN / TAU2_BETWEEN  # ~2.5789


@dataclass
class CalibrationPreviewResult:
    """Result of organization calibration computation."""

    k_projects: int
    shrinkage_weight: float
    global_a: float
    calibrated_a: float
    exponent_b: float
    scaling_ratio: float
    mdape_before: float
    mdape_after: float
    relative_gain_pct: float
    pred25_before: float
    pred25_after: float


class OrgCalibrationService:
    """Service providing Empirical Bayes calibration for organization actuals."""

    def __init__(
        self,
        beta0_global: float = 3.1880360932291065,
        b_global: float = 0.8270266757672359,
        variance_ratio: float = VARIANCE_RATIO,
    ) -> None:
        self.beta0_global = beta0_global
        self.b_global = b_global
        self.a_global = float(math.exp(beta0_global))
        self.variance_ratio = variance_ratio

    def compute_shrinkage_weight(self, k: int) -> float:
        """Compute Empirical Bayes shrinkage factor w in [0, 1)."""
        if k <= 0:
            return 0.0
        return float(k / (k + self.variance_ratio))

    def calibrate(
        self,
        actuals: Sequence[dict[str, Any]] | Sequence[tuple[float, float]],
    ) -> CalibrationPreviewResult:
        """Compute calibrated parameters and preview metrics on historical actuals.

        Parameters
        ----------
        actuals : sequence of dicts with 'size_fp' and 'actual_hours',
                  or tuples of (size_fp, actual_hours).
        """
        valid_sizes: list[float] = []
        valid_efforts: list[float] = []

        for item in actuals:
            if isinstance(item, dict):
                s = float(item.get("size_fp", item.get("size", 0.0)))
                e = float(item.get("actual_hours", item.get("effort_hours", item.get("effort", 0.0))))
            else:
                s = float(item[0])
                e = float(item[1])

            if s > 0.0 and e > 0.0 and math.isfinite(s) and math.isfinite(e):
                valid_sizes.append(s)
                valid_efforts.append(e)

        k = len(valid_sizes)
        if k == 0:
            return CalibrationPreviewResult(
                k_projects=0,
                shrinkage_weight=0.0,
                global_a=self.a_global,
                calibrated_a=self.a_global,
                exponent_b=self.b_global,
                scaling_ratio=1.0,
                mdape_before=0.0,
                mdape_after=0.0,
                relative_gain_pct=0.0,
                pred25_before=0.0,
                pred25_after=0.0,
            )

        sizes_arr = np.array(valid_sizes, dtype=np.float64)
        efforts_arr = np.array(valid_efforts, dtype=np.float64)

        # Baseline global predictions
        pred_before = np.maximum(self.a_global * (sizes_arr ** self.b_global), 1.0)
        ape_before = np.abs(pred_before - efforts_arr) / efforts_arr
        mdape_before = float(np.median(ape_before) * 100.0)
        pred25_before = float(np.mean(ape_before <= 0.25) * 100.0)

        # Empirical Bayes shrinkage
        log_s = np.log(sizes_arr)
        log_e = np.log(efforts_arr)
        residuals = log_e - (self.beta0_global + self.b_global * log_s)
        delta_log_a = float(np.mean(residuals))

        w = self.compute_shrinkage_weight(k)
        beta0_cal = self.beta0_global + w * delta_log_a
        a_cal = float(math.exp(beta0_cal))
        scaling_ratio = float(a_cal / self.a_global)

        # Calibrated predictions on actuals
        pred_after = np.maximum(a_cal * (sizes_arr ** self.b_global), 1.0)
        ape_after = np.abs(pred_after - efforts_arr) / efforts_arr
        mdape_after = float(np.median(ape_after) * 100.0)
        pred25_after = float(np.mean(ape_after <= 0.25) * 100.0)

        relative_gain = (
            float(((mdape_before - mdape_after) / mdape_before) * 100.0)
            if mdape_before > 0.0
            else 0.0
        )

        return CalibrationPreviewResult(
            k_projects=k,
            shrinkage_weight=float(round(w, 4)),
            global_a=float(round(self.a_global, 4)),
            calibrated_a=float(round(a_cal, 4)),
            exponent_b=float(round(self.b_global, 4)),
            scaling_ratio=float(round(scaling_ratio, 4)),
            mdape_before=float(round(mdape_before, 2)),
            mdape_after=float(round(mdape_after, 2)),
            relative_gain_pct=float(round(relative_gain, 2)),
            pred25_before=float(round(pred25_before, 2)),
            pred25_after=float(round(pred25_after, 2)),
        )

    def apply_calibration(
        self,
        base_quantiles: dict[str, np.ndarray | float],
        scaling_ratio: float,
    ) -> dict[str, Any]:
        """Scale predicted quantiles by calibrated organization productivity ratio."""
        if scaling_ratio <= 0.0:
            scaling_ratio = 1.0

        calibrated: dict[str, Any] = {}
        for k, v in base_quantiles.items():
            if isinstance(v, np.ndarray):
                calibrated[k] = np.maximum(v * scaling_ratio, 1.0)
            else:
                val = float(v) * scaling_ratio
                calibrated[k] = val if val > 1.0 else 1.0

        # Ensure monotonicity: p10 <= p25 <= p50 <= p75 <= p90
        if all(q in calibrated for q in ("p10", "p25", "p50", "p75", "p90")):
            if isinstance(calibrated["p10"], np.ndarray):
                calibrated["p10"] = np.maximum(calibrated["p10"], 1.0)
                calibrated["p25"] = np.maximum(calibrated["p25"], calibrated["p10"])
                calibrated["p50"] = np.maximum(calibrated["p50"], calibrated["p25"])
                calibrated["p75"] = np.maximum(calibrated["p75"], calibrated["p50"])
                calibrated["p90"] = np.maximum(calibrated["p90"], calibrated["p75"])
            else:
                p10_f = max(float(calibrated["p10"]), 1.0)
                p25_f = max(float(calibrated["p25"]), p10_f)
                p50_f = max(float(calibrated["p50"]), p25_f)
                p75_f = max(float(calibrated["p75"]), p50_f)
                p90_f = max(float(calibrated["p90"]), p75_f)
                calibrated["p10"], calibrated["p25"], calibrated["p50"], calibrated["p75"], calibrated["p90"] = (
                    p10_f,
                    p25_f,
                    p50_f,
                    p75_f,
                    p90_f,
                )

        return calibrated
