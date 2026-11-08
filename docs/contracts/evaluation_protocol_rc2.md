Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Evaluation Protocol & Frozen Decision Rules (RC2)

**Status:** FROZEN  
**Applies to:** version 2.0.0-rc.2  
**Date:** 2026-11-07  
**Author:** WS_ML / Orchestrator  

---

## 1. Context & Purpose
PredictIQ v2 evaluates effort estimation models using rigorous, cross-organizational Leave-One-Source-Out (LOSO) cross-validation to ensure models generalize to new, unseen software development environments without data leakage.

This document formally freezes the statistical decision rules for **Checkpoint R03** (Duration Elasticity Ablation) and **Checkpoint R07** (Model Track Selection) **prior** to running experimental evaluations.

---

## 2. Frozen Decision Rule: Checkpoint R03 (Duration Elasticity Ablation)

### Context & Economic Rationale
In `projects_v2.csv`, `duration_months` is populated for approximately 61% of projects (primarily from China and Maxwell repositories). In previous multivariate fits, the duration exponent was estimated at $c \approx +0.53$, implying:
$$\text{Effort} \propto \text{Size}^b \times \text{Duration}^c$$
Economically and operationally:
1. If $c > 0$, compressing a schedule (e.g. from 12 months to 6 months) reduces the estimated effort, which contradicts Brook's Law and the well-documented effort penalties of schedule compression ("the mythical man-month").
2. For projects lacking duration data (Kitchenham, Desharnais, Albrecht, AT&T), evaluating duration requires piecewise fallback or marginal power laws, introducing heterogeneity.

### Decision Criteria (Pre-Registered)
`duration_months` shall remain in the primary production effort point estimate **if and only if ALL** of the following three conditions are met on the duration-bearing subset under 6-fold Leave-One-Source-Out cross-validation:
1. **Statistical Significance:** Paired two-sided Wilcoxon signed-rank test on absolute percentage errors (APE) achieves $p < 0.05$ favoring the multivariate model (Size + Duration) over the univariate model (Size only).
2. **Material Accuracy Gain:** Macro MdAPE of the multivariate model improves by at least **5.0% relative** compared to the size-only baseline:
   $$\frac{\text{MdAPE}_{\text{size-only}} - \text{MdAPE}_{\text{multivariate}}}{\text{MdAPE}_{\text{size-only}}} \ge 0.05$$
3. **Defensible What-If Direction:** The elasticity coefficient must be defensible in production what-if scenarios (compressing schedule must not artificially underestimate effort without explicit risk penalties).

### Fallback Policy
If **any** of the criteria above fail:
- The production point estimate becomes **strictly size-only**: $\text{Effort} = a \cdot \text{Size}^b$.
- `duration_months` is removed from the ML effort equation and used solely for timeline, scheduling, staffing, and project delivery feasibility display.
- Contracts, serving schemas, and UI copy are updated to state clearly: "Planned duration is used for schedule and timeline planning; it does not alter raw effort estimates."

---

## 3. Frozen Decision Rule: Checkpoint R07 (Challenger Models)

### Candidates
- Model A: Primary Monotone Power Law (Track 1)
- Model B: Hierarchical/Mixed-Effects Log-Log Model with source random intercept
- Model C: Categorical context (platform, dev_type) where coverage supports it under LOSO
- Model D: Quantile Regression on log size

### Criteria
A challenger model shall displace the incumbent Track 1 model if:
1. Macro MdAPE improves by $\ge 3.0\%$ relative across unseen LOSO source folds.
2. PRED25 improves or remains strictly non-inferior (within $\pm 1.0\%$).
3. Strictly preserves monotonicity with respect to functional size ($\partial \hat{y} / \partial S \ge 0$).
4. Does not require unobservable, unverified, or synthetic feature inputs.
