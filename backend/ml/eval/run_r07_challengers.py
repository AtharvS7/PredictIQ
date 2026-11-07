"""R07 Challenger Models Re-evaluation under Frozen Evaluation Protocol RC2.

Evaluates incumbent Model A against candidate challengers under strict 6-fold
Leave-One-Source-Out (LOSO) cross-validation on projects_v2.csv (N=915).

Frozen criteria (docs/contracts/evaluation_protocol_rc2.md):
1. Macro MdAPE improves by >= 3.0% relative across unseen LOSO folds.
2. PRED25 improves or remains strictly non-inferior (within +/- 1.0%).
3. Strictly preserves monotonicity with respect to functional size (dy/dS >= 0).
4. Does not require unobservable, unverified, or synthetic feature inputs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import QuantileRegressor

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.ml.eval.metrics import mae, mdape, pred25
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset
from backend.ml.track1.models import MonotonePowerLaw
from backend.ml.track2.models import MonotoneHistGradientBoosting


class HierarchicalLogLogModel:
    """Model B: Hierarchical/Mixed-effects log-log model.

    Models source random intercepts. On unseen test folds under LOSO, the random
    effect expectation is zero, yielding the population marginal fixed effect.
    """
    def __init__(self):
        self.alpha_0: float = 0.0
        self.beta: float = 0.827
        self.tau2: float = 0.0
        self.sigma2: float = 0.0

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "HierarchicalLogLogModel":
        log_s = np.log(X["size_value"].to_numpy(dtype=float))
        log_e = np.log(y.astype(float))
        sources = X["source"].to_numpy()

        # OLS population fit
        reg = stats.linregress(log_s, log_e)
        self.beta = float(reg.slope)
        self.alpha_0 = float(reg.intercept)

        unique_srcs = np.unique(sources)
        intercepts = []
        within_res = []
        for s in unique_srcs:
            mask = sources == s
            res = log_e[mask] - (self.alpha_0 + self.beta * log_s[mask])
            intercepts.append(np.mean(res))
            within_res.extend(res - np.mean(res))

        self.tau2 = float(max(1e-4, np.var(intercepts, ddof=1)))
        self.sigma2 = float(max(1e-4, np.var(within_res, ddof=1)))
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        log_s = np.log(X["size_value"].to_numpy(dtype=float))
        # On unseen source, E[u_new] = 0, so prediction is population marginal
        pred_log = self.alpha_0 + self.beta * log_s
        return np.exp(pred_log)


class LogSizeQuantileRegression:
    """Model D: Median Quantile Regression on log size (L1 loss)."""
    def __init__(self):
        self.model = QuantileRegressor(quantile=0.5, alpha=0.0)

    def fit(self, X: pd.DataFrame, y: np.ndarray) -> "LogSizeQuantileRegression":
        log_s = np.log(X["size_value"].to_numpy(dtype=float)).reshape(-1, 1)
        log_e = np.log(y.astype(float))
        self.model.fit(log_s, log_e)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        log_s = np.log(X["size_value"].to_numpy(dtype=float)).reshape(-1, 1)
        pred_log = self.model.predict(log_s)
        return np.exp(pred_log)


def evaluate_all_challengers() -> dict[str, Any]:
    dataset = load_dataset()
    splitter = LeaveOneSourceOutSplitter()
    splits = list(splitter.split_df(dataset))

    models = {
        "Model A (MonotonePowerLaw - Incumbent)": lambda: MonotonePowerLaw(),
        "Model B (Hierarchical Mixed-Effects Log-Log)": lambda: HierarchicalLogLogModel(),
        "Model D (QuantileRegression L1 Median)": lambda: LogSizeQuantileRegression(),
        "Track 2 (MonotoneHistGradientBoosting)": lambda: MonotoneHistGradientBoosting(max_iter=50, max_leaf_nodes=7),
    }

    # Store fold metrics
    model_fold_mdape: dict[str, list[float]] = {m: [] for m in models}
    model_fold_pred25: dict[str, list[float]] = {m: [] for m in models}
    model_fold_mae: dict[str, list[float]] = {m: [] for m in models}
    model_all_apes: dict[str, list[float]] = {m: [] for m in models}

    for fold in splits:
        train_df = fold.train_df
        test_df = fold.test_df
        y_train = train_df["effort_hours"].to_numpy(dtype=float)
        y_test = test_df["effort_hours"].to_numpy(dtype=float)

        for name, ctor in models.items():
            model = ctor()
            # Prepare inputs
            if name.startswith("Track 2"):
                X_train = pd.DataFrame({"size_fp": train_df["size_value"]})
                X_test = pd.DataFrame({"size_fp": test_df["size_value"]})
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            else:
                model.fit(train_df, y_train)
                y_pred = model.predict(test_df)

            fold_mdape_val = float(mdape(y_test, y_pred))
            fold_pred25_val = float(pred25(y_test, y_pred))
            fold_mae_val = float(mae(y_test, y_pred))

            model_fold_mdape[name].append(fold_mdape_val)
            model_fold_pred25[name].append(fold_pred25_val)
            model_fold_mae[name].append(fold_mae_val)

            # APE per sample
            apes = np.abs(y_test - y_pred) / y_test
            model_all_apes[name].extend(apes.tolist())

    incumbent_name = "Model A (MonotonePowerLaw - Incumbent)"
    base_mdape = float(np.mean(model_fold_mdape[incumbent_name]))
    base_pred25 = float(np.mean(model_fold_pred25[incumbent_name]))
    base_apes = np.array(model_all_apes[incumbent_name])

    summary: dict[str, Any] = {
        "protocol": "6-fold Leave-One-Source-Out (LOSO)",
        "dataset_records": len(dataset),
        "incumbent_model": incumbent_name,
        "models": {},
        "decision": {
            "displaced": False,
            "selected_model": incumbent_name,
            "justification": "",
        },
    }

    winner = incumbent_name
    winner_gain = 0.0

    for name in models:
        m_mdape = float(np.mean(model_fold_mdape[name]))
        m_pred25 = float(np.mean(model_fold_pred25[name]))
        m_mae = float(np.mean(model_fold_mae[name]))

        rel_gain = (base_mdape - m_mdape) / base_mdape
        rel_gain_pct = rel_gain * 100.0

        # Paired Wilcoxon test against incumbent on all APEs
        cand_apes = np.array(model_all_apes[name])
        if name == incumbent_name:
            p_val = 1.0
        else:
            w_stat, p_val = stats.wilcoxon(base_apes, cand_apes, alternative="two-sided")
            p_val = float(p_val)

        # Monotonicity test
        test_sizes = np.linspace(10, 5000, 100)
        if name.startswith("Track 2"):
            test_preds = models[name]().fit(pd.DataFrame({"size_fp": dataset["size_value"]}), dataset["effort_hours"].to_numpy()).predict(pd.DataFrame({"size_fp": test_sizes}))
        else:
            test_preds = models[name]().fit(dataset, dataset["effort_hours"].to_numpy()).predict(pd.DataFrame({"size_value": test_sizes, "source": ["test"]*100}))
        is_monotone = bool(np.all(np.diff(test_preds) >= -1e-6))

        # Check pre-registered criteria
        c1_mdape = rel_gain >= 0.03
        c2_pred25 = m_pred25 >= (base_pred25 - 1.0)
        c3_monotone = is_monotone
        c4_features = True  # strictly size-based

        passes_all = c1_mdape and c2_pred25 and c3_monotone and c4_features

        summary["models"][name] = {
            "macro_mdape": round(m_mdape, 2),
            "macro_pred25": round(m_pred25, 2),
            "macro_mae_hours": round(m_mae, 1),
            "relative_mdape_gain_pct": round(rel_gain_pct, 2),
            "wilcoxon_p_value": p_val,
            "strictly_monotone": is_monotone,
            "criteria_check": {
                "c1_mdape_gain_ge_3pct": c1_mdape,
                "c2_pred25_non_inferior": c2_pred25,
                "c3_monotonicity_preserved": c3_monotone,
                "c4_clean_features_only": c4_features,
                "overall_pass": passes_all,
            },
        }

        if passes_all and rel_gain > winner_gain:
            winner = name
            winner_gain = rel_gain

    if winner != incumbent_name:
        summary["decision"]["displaced"] = True
        summary["decision"]["selected_model"] = winner
        summary["decision"]["justification"] = f"{winner} passed all 4 criteria with a relative MdAPE gain of {winner_gain*100:.2f}%."
    else:
        summary["decision"]["displaced"] = False
        summary["decision"]["selected_model"] = incumbent_name
        summary["decision"]["justification"] = (
            "None of the challenger models met all four frozen decision criteria (>=3% relative MdAPE gain with non-inferior PRED25 and monotonicity). "
            f"{incumbent_name} is unanimously confirmed as the production estimator."
        )

    return summary


if __name__ == "__main__":
    res = evaluate_all_challengers()
    print(json.dumps(res, indent=2))
    out_file = _REPO_ROOT / "docs" / "evidence" / "r07_challenger_results.json"
    with out_file.open("w") as f:
        json.dump(res, f, indent=2)
    print(f"Results written to {out_file}")
