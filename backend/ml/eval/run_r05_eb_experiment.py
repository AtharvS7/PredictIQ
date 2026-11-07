"""Empirical-Bayes Organization Calibration Experiment (Checkpoint R05).

Evaluates whether adapting the global production model to organization-specific
historical actuals using empirical-Bayes shrinkage improves Leave-One-Source-Out
(LOSO) generalization.

Pre-registered decision criterion:
If relative MdAPE gain >= 10% at k <= 10, implement in serving and UI;
otherwise document negative result in docs/evidence/R05.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.ml.eval.metrics import mdape, pred25
from backend.ml.eval.protocol import load_dataset


def run_experiment(
    data_path: Path | None = None,
    k_values: list[int] | None = None,
    n_trials: int = 50,
    random_state: int = 42,
) -> dict[str, Any]:
    if k_values is None:
        k_values = [0, 3, 5, 10, 20]

    df = load_dataset(data_path)
    # Filter valid size and effort
    df = df[df["size_value"] > 0].copy()
    df = df[df["effort_hours"] > 0].copy()
    df["log_size"] = np.log(df["size_value"].to_numpy(dtype=float))
    df["log_effort"] = np.log(df["effort_hours"].to_numpy(dtype=float))

    sources = sorted(df["source"].unique())
    rng = np.random.RandomState(random_state)

    # Store fold-level results for each k
    fold_mdape: dict[int, list[float]] = {k: [] for k in k_values}
    fold_pred25: dict[int, list[float]] = {k: [] for k in k_values}

    for fold_src in sources:
        train_df = df[df["source"] != fold_src]
        test_df = df[df["source"] == fold_src]
        n_test = len(test_df)

        # Fit global base model on training sources
        # Fit log-log linear model
        x_train = train_df["log_size"].to_numpy()
        y_train = train_df["log_effort"].to_numpy()
        reg = stats.linregress(x_train, y_train)
        beta = float(reg.slope)
        alpha_0 = float(reg.intercept)

        # Estimate between-source variance (tau^2) and within-source residual variance (sigma^2)
        train_sources = train_df["source"].unique()
        source_intercepts = []
        within_residuals = []
        for s in train_sources:
            s_df = train_df[train_df["source"] == s]
            s_res = s_df["log_effort"].to_numpy() - (alpha_0 + beta * s_df["log_size"].to_numpy())
            source_intercepts.append(np.mean(s_res))
            within_residuals.extend(s_res - np.mean(s_res))

        tau2 = float(max(1e-4, np.var(source_intercepts, ddof=1)))
        sigma2 = float(max(1e-4, np.var(within_residuals, ddof=1)))

        for k in k_values:
            if k == 0:
                # Prior prediction with no actuals
                y_pred_log = alpha_0 + beta * test_df["log_size"].to_numpy()
                y_pred = np.exp(y_pred_log)
                y_true = test_df["effort_hours"].to_numpy()
                fold_mdape[0].append(float(mdape(y_true, y_pred)))
                fold_pred25[0].append(float(pred25(y_true, y_pred)))
            else:
                if n_test <= k + 2:
                    # Skip if not enough test observations to evaluate out-of-sample
                    continue

                trial_mdape = []
                trial_pred25 = []

                for _ in range(n_trials):
                    # Randomly sample k adaptation actuals
                    adapt_idx = rng.choice(n_test, size=k, replace=False)
                    eval_mask = np.ones(n_test, dtype=bool)
                    eval_mask[adapt_idx] = False

                    adapt_df = test_df.iloc[adapt_idx]
                    eval_df = test_df.iloc[eval_mask]

                    # Residuals of adaptation points against global model
                    adapt_residuals = adapt_df["log_effort"].to_numpy() - (
                        alpha_0 + beta * adapt_df["log_size"].to_numpy()
                    )
                    mean_residual = float(np.mean(adapt_residuals))

                    # Empirical Bayes shrinkage factor
                    weight = tau2 / (tau2 + sigma2 / k)
                    alpha_adapted = alpha_0 + weight * mean_residual

                    # Evaluate on hold-out eval points
                    eval_pred_log = alpha_adapted + beta * eval_df["log_size"].to_numpy()
                    eval_pred = np.exp(eval_pred_log)
                    eval_true = eval_df["effort_hours"].to_numpy()

                    trial_mdape.append(mdape(eval_true, eval_pred))
                    trial_pred25.append(pred25(eval_true, eval_pred))

                fold_mdape[k].append(float(np.mean(trial_mdape)))
                fold_pred25[k].append(float(np.mean(trial_pred25)))

    # Compute macro-average metrics across folds
    base_mdape = float(np.mean(fold_mdape[0]))
    base_pred25 = float(np.mean(fold_pred25[0]))

    summary: dict[str, Any] = {
        "baseline_k0": {
            "macro_mdape": round(base_mdape, 4),
            "macro_pred25": round(base_pred25, 4),
        },
        "k_experiments": {},
        "decision": {
            "threshold_relative_gain": 0.10,
            "max_k": 10,
            "pass_gain_criterion": False,
            "recommendation": "",
        },
    }

    best_gain_at_k_le_10 = -1.0
    for k in k_values:
        if k == 0:
            continue
        k_mdape = float(np.mean(fold_mdape[k]))
        k_pred25 = float(np.mean(fold_pred25[k]))
        rel_gain = float((base_mdape - k_mdape) / base_mdape)

        summary["k_experiments"][f"k_{k}"] = {
            "k": k,
            "macro_mdape": round(k_mdape, 4),
            "macro_pred25": round(k_pred25, 4),
            "relative_gain_mdape": round(rel_gain, 4),
            "relative_gain_pct": round(rel_gain * 100, 2),
            "folds_evaluated": len(fold_mdape[k]),
        }

        if k <= 10 and rel_gain > best_gain_at_k_le_10:
            best_gain_at_k_le_10 = rel_gain

    pass_gate = best_gain_at_k_le_10 >= 0.10
    summary["decision"]["best_gain_at_k_le_10"] = round(best_gain_at_k_le_10, 4)
    summary["decision"]["best_gain_at_k_le_10_pct"] = round(best_gain_at_k_le_10 * 100, 2)
    summary["decision"]["pass_gain_criterion"] = pass_gate
    if pass_gate:
        summary["decision"]["recommendation"] = "Implement Empirical-Bayes actuals shrinkage in serving and UI."
    else:
        summary["decision"]["recommendation"] = (
            f"Gain ({best_gain_at_k_le_10 * 100:.2f}%) did not reach the pre-registered 10.0% threshold at k<=10. "
            "Document negative result; retain unshifted calibrated population model for enterprise consistency."
        )

    return summary


if __name__ == "__main__":
    res = run_experiment()
    print(json.dumps(res, indent=2))
    out_file = _REPO_ROOT / "docs" / "evidence" / "r05_eb_results.json"
    with out_file.open("w") as f:
        json.dump(res, f, indent=2)
    print(f"Saved results to {out_file}")
