"""R03: Duration Elasticity Ablation Study under Frozen Protocol.

Compares:
- Model A: MonotonePowerLaw (size-only, E = a * S^b)
- Model B: MultivariateMonotoneModel (size + duration, E = a * S^b * D^c)

Evaluates under Leave-One-Source-Out (LOSO) across the duration-bearing subset
(China N=499, Maxwell N=62; total N=561) and across all 6 folds.
Computes:
1. Paired two-sided Wilcoxon signed-rank test on absolute percentage errors (APEs)
2. Per-source MdAPE and Macro MdAPE
3. Bootstrap 95% confidence intervals for Macro MdAPE (B=2000)
4. Fitted duration elasticity c
5. Evaluation against the 3 pre-registered criteria in docs/contracts/evaluation_protocol_rc2.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

# Ensure repository root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from backend.ml.eval.metrics import mdape, pred25
from backend.ml.eval.protocol import LeaveOneSourceOutSplitter, load_dataset
from backend.ml.track1.models import MonotonePowerLaw, MultivariateMonotoneModel


def bootstrap_macro_mdape(
    source_apes: dict[str, np.ndarray],
    n_boot: int = 2000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Compute bootstrap 95% confidence interval for macro MdAPE."""
    rng = np.random.default_rng(seed)
    sources = list(source_apes.keys())
    boot_macro = np.empty(n_boot, dtype=np.float64)

    for b in range(n_boot):
        fold_mdapes = []
        for s in sources:
            apes = source_apes[s]
            boot_idx = rng.choice(len(apes), size=len(apes), replace=True)
            fold_mdapes.append(float(np.median(apes[boot_idx]) * 100.0))
        boot_macro[b] = float(np.mean(fold_mdapes))

    point = float(np.mean([np.median(source_apes[s]) * 100.0 for s in sources]))
    ci_lower = float(np.percentile(boot_macro, 2.5))
    ci_upper = float(np.percentile(boot_macro, 97.5))
    return point, ci_lower, ci_upper


def run_ablation() -> dict[str, Any]:
    dataset_path = _REPO_ROOT / "backend" / "ml" / "data" / "projects_v2.csv"
    df = load_dataset(dataset_path)

    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(df))

    # Storage for predictions and errors
    results: dict[str, Any] = {
        "dataset_total_projects": len(df),
        "duration_bearing_total": int(df["duration_months"].notna().sum()),
        "folds": {},
        "duration_subset": {},
        "all_folds_summary": {},
    }

    all_apes_a: list[float] = []
    all_apes_b: list[float] = []

    dur_apes_a: list[float] = []
    dur_apes_b: list[float] = []

    source_apes_a: dict[str, np.ndarray] = {}
    source_apes_b: dict[str, np.ndarray] = {}

    dur_source_apes_a: dict[str, np.ndarray] = {}
    dur_source_apes_b: dict[str, np.ndarray] = {}

    print("=" * 80)
    print("PREDICTIQ V2 - CHECKPOINT R03 DURATION ELASTICITY ABLATION")
    print("=" * 80)
    print(f"Total projects: {len(df)}")
    print(f"Duration populated: {results['duration_bearing_total']} (China, Maxwell)\n")

    for fold in folds:
        s_name = fold.fold_name
        train_df = fold.train_df
        test_df = fold.test_df
        y_train = train_df["effort_hours"].to_numpy()
        y_test = test_df["effort_hours"].to_numpy()

        # Model A: Size-only
        model_a = MonotonePowerLaw()
        model_a.fit(train_df, y_train)
        pred_a = model_a.predict(test_df)

        # Model B: Multivariate (Size + Duration)
        model_b = MultivariateMonotoneModel()
        model_b.fit(train_df, y_train)
        pred_b = model_b.predict(test_df)

        # Relative errors
        ape_a = np.abs(pred_a - y_test) / y_test
        ape_b = np.abs(pred_b - y_test) / y_test

        source_apes_a[s_name] = ape_a
        source_apes_b[s_name] = ape_b

        all_apes_a.extend(ape_a.tolist())
        all_apes_b.extend(ape_b.tolist())

        mdape_a = mdape(y_test, pred_a)
        mdape_b = mdape(y_test, pred_b)
        p25_a = pred25(y_test, pred_a)
        p25_b = pred25(y_test, pred_b)

        has_dur = bool(test_df["duration_months"].notna().any())
        results["folds"][s_name] = {
            "n_test": len(test_df),
            "has_duration": has_dur,
            "model_a_size_only": {
                "mdape": round(mdape_a, 2),
                "pred25": round(p25_a, 2),
                "a": round(float(model_a.a_), 4),
                "b": round(float(model_a.b_), 4),
            },
            "model_b_multivariate": {
                "mdape": round(mdape_b, 2),
                "pred25": round(p25_b, 2),
                "a": round(float(model_b.a_), 4) if model_b.a_ is not None else None,
                "b": round(float(model_b.b_), 4) if model_b.b_ is not None else None,
                "c": round(float(model_b.c_), 4) if model_b.c_ is not None else None,
            },
        }

        if has_dur:
            dur_mask = test_df["duration_months"].notna().to_numpy()
            sub_ape_a = ape_a[dur_mask]
            sub_ape_b = ape_b[dur_mask]
            dur_source_apes_a[s_name] = sub_ape_a
            dur_source_apes_b[s_name] = sub_ape_b
            dur_apes_a.extend(sub_ape_a.tolist())
            dur_apes_b.extend(sub_ape_b.tolist())

        print(
            f"Fold: {s_name:<12} (N={len(test_df):>3}, Dur={'Yes' if has_dur else 'No '}) | "
            f"Model A MdAPE: {mdape_a:>5.2f}% (P25: {p25_a:>5.2f}%) | "
            f"Model B MdAPE: {mdape_b:>5.2f}% (P25: {p25_b:>5.2f}%) | "
            f"Fitted c: {results['folds'][s_name]['model_b_multivariate']['c']}"
        )

    # Full dataset fit for parameter inspection
    full_a = MonotonePowerLaw().fit(df, df["effort_hours"].to_numpy())
    full_b = MultivariateMonotoneModel().fit(df, df["effort_hours"].to_numpy())

    fitted_c = float(full_b.c_)

    # 1. Statistical evaluation on Duration-bearing subset (China, Maxwell, N=561)
    dur_arr_a = np.array(dur_apes_a)
    dur_arr_b = np.array(dur_apes_b)

    # Wilcoxon signed-rank test (two-sided)
    wilcox_res = stats.wilcoxon(dur_arr_a, dur_arr_b, alternative="two-sided")
    wilcox_p = float(wilcox_res.pvalue)
    wilcox_stat = float(wilcox_res.statistic)

    # Bootstrap Macro MdAPE on duration sources (China, Maxwell)
    dur_macro_a, dur_ci_low_a, dur_ci_high_a = bootstrap_macro_mdape(dur_source_apes_a)
    dur_macro_b, dur_ci_low_b, dur_ci_high_b = bootstrap_macro_mdape(dur_source_apes_b)

    dur_rel_gain = (dur_macro_a - dur_macro_b) / dur_macro_a

    # Macro MdAPE across ALL 6 sources
    all_macro_a, all_ci_low_a, all_ci_high_a = bootstrap_macro_mdape(source_apes_a)
    all_macro_b, all_ci_low_b, all_ci_high_b = bootstrap_macro_mdape(source_apes_b)
    all_rel_gain = (all_macro_a - all_macro_b) / all_macro_a

    # Evaluate against the 3 Pre-Registered Decision Criteria
    cond1_wilcoxon = bool(wilcox_p < 0.05)
    cond2_rel_gain = bool(dur_rel_gain >= 0.05)
    # Criterion 3: defensible what-if direction.
    # If c > 0, schedule compression falsely reduces effort, which is indefensible.
    # What-if schedule compression requires c <= 0 or explicit penalty.
    cond3_direction = bool(fitted_c <= 0.0)

    decision_pass = cond1_wilcoxon and cond2_rel_gain and cond3_direction
    action = (
        "KEEP Duration in Primary Effort Estimate"
        if decision_pass
        else "REMOVE Duration from Effort Estimate -> Strictly Size-Only Production Point Estimate (E = a * S^b)"
    )

    results["duration_subset_evaluation"] = {
        "n_samples": len(dur_arr_a),
        "sources": list(dur_source_apes_a.keys()),
        "model_a_macro_mdape": round(dur_macro_a, 2),
        "model_a_95ci": [round(dur_ci_low_a, 2), round(dur_ci_high_a, 2)],
        "model_b_macro_mdape": round(dur_macro_b, 2),
        "model_b_95ci": [round(dur_ci_low_b, 2), round(dur_ci_high_b, 2)],
        "relative_gain_pct": round(dur_rel_gain * 100.0, 2),
        "wilcoxon_statistic": wilcox_stat,
        "wilcoxon_p_value": wilcox_p,
    }

    results["all_6_folds_evaluation"] = {
        "model_a_macro_mdape": round(all_macro_a, 2),
        "model_a_95ci": [round(all_ci_low_a, 2), round(all_ci_high_a, 2)],
        "model_b_macro_mdape": round(all_macro_b, 2),
        "model_b_95ci": [round(all_ci_low_b, 2), round(all_ci_high_b, 2)],
        "relative_gain_pct": round(all_rel_gain * 100.0, 2),
    }

    results["fitted_parameters_full_dataset"] = {
        "model_a": {"a": round(float(full_a.a_), 4), "b": round(float(full_a.b_), 4)},
        "model_b": {
            "a": round(float(full_b.a_), 4),
            "b": round(float(full_b.b_), 4),
            "c": round(fitted_c, 4),
        },
    }

    results["pre_registered_criteria_check"] = {
        "criterion_1_wilcoxon_p_lt_0_05": {
            "p_value": wilcox_p,
            "threshold": 0.05,
            "passed": cond1_wilcoxon,
        },
        "criterion_2_relative_gain_gte_5pct": {
            "relative_gain_pct": round(dur_rel_gain * 100.0, 2),
            "threshold_pct": 5.0,
            "passed": cond2_rel_gain,
        },
        "criterion_3_defensible_direction_c_lte_0": {
            "fitted_c": round(fitted_c, 4),
            "economic_interpretation": (
                "c > 0 implies reducing planned duration reduces required effort, "
                "violating Brooks' Law and project scheduling physics."
            ),
            "passed": cond3_direction,
        },
        "overall_decision_pass": decision_pass,
        "action_taken": action,
    }

    print("\n" + "=" * 80)
    print("ABLATION RESULTS SUMMARY")
    print("=" * 80)
    print(f"Duration Subset (China + Maxwell, N={len(dur_arr_a)}):")
    print(f"  Model A (Size-Only) Macro MdAPE: {dur_macro_a:.2f}% (95% CI: [{dur_ci_low_a:.2f}%, {dur_ci_high_a:.2f}%])")
    print(f"  Model B (Size+Dur)   Macro MdAPE: {dur_macro_b:.2f}% (95% CI: [{dur_ci_low_b:.2f}%, {dur_ci_high_b:.2f}%])")
    print(f"  Relative MdAPE Gain:             {dur_rel_gain * 100.0:.2f}%")
    print(f"  Wilcoxon signed-rank p-value:    {wilcox_p:.5e} (stat={wilcox_stat})")
    print(f"  Fitted Duration Elasticity c:    {fitted_c:.4f}")
    print("\nPre-Registered Decision Rules Assessment:")
    print(f"  [1] Wilcoxon p < 0.05:            {'PASS' if cond1_wilcoxon else 'FAIL'} (p={wilcox_p:.5e})")
    print(f"  [2] Relative Gain >= 5.0%:        {'PASS' if cond2_rel_gain else 'FAIL'} ({dur_rel_gain * 100.0:.2f}%)")
    print(f"  [3] Defensible Direction (c <= 0):{'PASS' if cond3_direction else 'FAIL'} (c={fitted_c:.4f} > 0)")
    print(f"\nFINAL VERDICT: {action}")
    print("=" * 80)

    # Save output to evidence
    out_file = _REPO_ROOT / "docs" / "evidence" / "r03_ablation_results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Results written to: {out_file}")

    return results


if __name__ == "__main__":
    run_ablation()
