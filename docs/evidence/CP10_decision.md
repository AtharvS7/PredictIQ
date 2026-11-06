# Checkpoint CP10: Challenger Decision & Primary Track Selection

**Status:** PASS  
**Date:** 2026-11-06  
**Branch:** `dev3`  
**Agents & Skills Used:** mle-reviewer, architect, spec-miner, loop-operator  

---

## 1. Frozen Decision Rule Evaluation

In Checkpoint CP01 (`docs/contracts/ml_contract.md`) and the project guidelines, a strict, objective, frozen statistical decision rule was codified to eliminate model selection bias:

> **Frozen Challenger Threshold:**
> To dislodge Track 1 and become the primary production estimator, a Track 2 challenger must:
> 1. Reduce Leave-One-Source-Out (LOSO) Macro MdAPE by $\ge 5\%$ relative compared to the LogLinear/Track 1 reference floor ($\le 53.2\%$ MdAPE).
> 2. Demonstrate statistically significant superiority over holdout error distributions via Wilcoxon signed-rank test ($p < 0.05$).
> 3. Cause no single historical source to degrade by $> 10\%$ absolute MdAPE.

---

## 2. Quantitative Comparison Matrix (6 LOSO Folds on `projects_v2.csv`)

| Track | Model Name | Macro MdAPE | Macro MAE | Macro RMSE | Macro $R^2$ | PRED(25) | SA (%) | Status vs Threshold |
|---|---|---|---|---|---|---|---|---|
| **CP07 Baseline** | `MedianDummyPredictor` | 72.5% | 7232.4 h | 13572.6 h | -0.275 | 13.6% | 0.0% | Reference Dummy |
| **CP07 Baseline** | `AlbrechtNominalPredictor` | 56.1% | 5904.5 h | 10449.8 h | 0.233 | 19.6% | 21.4% | Reference Baseline |
| **CP07 Baseline** | `LogLinearBaseline` | 56.0% | 5886.4 h | 10787.6 h | 0.202 | 20.5% | 22.5% | Reference Floor |
| **Track 1** | `MonotonePowerLaw` | 56.3% | 5875.2 h | 10449.2 h | 0.222 | 20.2% | 21.2% | Transparent Single-Feature |
| **Track 1 (Selected)** | **`MultivariateMonotoneModel`** | **53.9%** | **5712.7 h** | **10027.5 h** | **0.314** | **19.1%** | **25.3%** | **Top Out-of-Domain Generalizer** |
| **Track 2** | `MonotoneHistGradientBoosting` | 55.5% | 5953.0 h | 10834.6 h | 0.191 | 19.5% | 18.4% | Fails $\le 53.2\%$ Criterion |
| **Track 2** | `MultivariateHistGradientBoosting` | 55.4% | 5890.7 h | 10565.4 h | 0.239 | 19.0% | 20.5% | Fails $\le 53.2\%$ Criterion |

---

## 3. Statistical Hypothesis Testing & Per-Source Degradation

### 3.1 Wilcoxon Signed-Rank Test
Comparing the fold-level MdAPE across the 6 historical sources between Track 1 (`MultivariateMonotoneModel`) and Track 2 (`MultivariateHistGradientBoosting`):
- **Test Statistic $W$:** $8.0$
- **$p$-value:** $0.6875$ (two-sided)
- **Conclusion:** Track 2 is **not** statistically significantly better than Track 1 ($p \gg 0.05$).

### 3.2 Per-Source Breakdown
| Historical Source | Test N | Track 1 Multi MdAPE | Track 2 Multi MdAPE | Difference ($\Delta$) | Winner |
|---|---|---|---|---|---|
| `china` | 499 | **49.7%** | 58.7% | +9.0% | **Track 1** (by 9.0%) |
| `kitchenham` | 145 | 59.2% | **51.7%** | -7.6% | **Track 2** |
| `att_aptness` | 104 | 58.7% | **56.7%** | -2.0% | **Track 2** |
| `desharnais` | 81 | **52.4%** | 56.3% | +3.9% | **Track 1** |
| `maxwell` | 62 | **34.4%** | 40.6% | +6.1% | **Track 1** |
| `albrecht` | 24 | 69.2% | **68.4%** | -0.8% | **Track 2** |

On the largest empirical dataset (`china`, representing 54.5% of all historical projects), Track 1 decisively outperforms Track 2 by 9.0% lower MdAPE, with an $R^2$ of **0.490** vs 0.448.

---

## 4. Final Architecture Decision

1. **Primary Production Estimator:** **Track 1 (`MultivariateMonotoneModel` + `MonotonePowerLaw`)** is selected as the primary point estimator.
   - Global mathematical guarantee: $\partial E / \partial S > 0$ everywhere ($C^\infty$ smooth).
   - Zero synthetic imputation: handles missing target duration with base marginal power law.
   - Lowest Macro MdAPE (**53.9%**) and highest generalization $R^2$ (**0.314**).
2. **Role of Track 2:**
   - Retained in codebase (`backend/ml/track2/`) for benchmarking, ensemble comparisons, and research.
   - Track 2 quantile regressor (`QuantileGradientBoosting`) informs interval spread diagnostics.
3. **Serving & Artifact Freezing:**
   - CP11 will calibrate prediction intervals around Track 1 using conformal prediction.

