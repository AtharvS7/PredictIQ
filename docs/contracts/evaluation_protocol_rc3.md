Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# PredictIQ Pre-Registered Evaluation Protocol & Frozen Decision Rules (RC3)

**Status:** FROZEN & APPROVED  
**Applies to:** version 2.0.0-rc.3  
**Verified against commit:** cdca041  
**Date:** 2026-11-08  
**Author:** ML Architecture & Infrastructure Group  

---

## 1. Context & Scientific Objectives

PredictIQ evaluates software effort and cost prediction algorithms using rigorous, cross-organizational Leave-One-Source-Out (LOSO) cross-validation. This protocol pre-registers experimental procedures, metrics, and immutable decision thresholds for release candidate **v2.0.0-rc.3 (RC3)** to prevent data snooping, cherry-picking, and post-hoc rationalization.

The RC3 evaluation program investigates three core hypotheses:
1. **Empirical Bayes Organizational Shrinkage**: Whether Bayesian shrinkage to project actuals improves prediction accuracy on downstream organization estimates without overfitting small sample sizes ($k \in [1, 10]$).
2. **Zero-Pickle Numerical Equivalence**: Whether pure JSON parameter deserialization (`model_params.json`) achieves bitwise/floating-point parity ($| \hat{y}_{\text{JSON}} - \hat{y}_{\text{pickle}} | / \hat{y} < 10^{-6}$) with Python pickle deserialization while eliminating remote code execution vulnerabilities.
3. **Cross-Platform Numerical Invariance**: Whether inference outputs across Linux POSIX (Ubuntu 22.04/24.04 x86_64) and Windows x86_64 runtimes remain identical within IEEE 754 double-precision tolerances.

---

## 2. Experimental Dataset & Partitioning

Evaluations are performed against the verified gold dataset `backend/ml/data/projects_v2.csv` (SHA-256: `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`) comprising 915 completed software projects across six historical sources:

| Source | Record Count | Functional Size Range (FP) | Effort Range (Hours) | Primary Language/Environment |
|--------|--------------|----------------------------|----------------------|------------------------------|
| **China** | 499 | 4.0 – 4,100.0 | 26.0 – 54,620.0 | Diverse / 4GL / Modern Web |
| **Desharnais** | 81 | 62.0 – 1,116.0 | 546.0 – 23,940.0 | Traditional / Cobol / 4GL |
| **Kitchenham** | 145 | 11.0 – 1,600.0 | 59.0 – 21,346.0 | Commercial / Mixed |
| **Maxwell** | 62 | 48.0 – 3,641.0 | 583.0 – 63,694.0 | Defense / Banking / High-Reliability |
| **Albrecht** | 24 | 199.0 – 1,902.0 | 500.0 – 60,000.0 | Enterprise IBM / Mainframe |
| **AT&T Aptness** | 104 | 14.0 – 1,822.0 | 18.0 – 19,865.0 | Telecommunications / Systems |
| **Total** | **915** | **4.0 – 4,100.0** | **18.0 – 63,694.0** | **Multi-Source Cross-Section** |

### Leave-One-Source-Out (LOSO) 6-Fold Cross-Validation
In each of the six folds, an entire data source is completely excluded from training, scaling, and calibration. The model is trained exclusively on the remaining five sources and evaluated as an out-of-domain transfer test on the held-out source.

---

## 3. Pre-Registered Evaluation Metrics

For every model candidate across each LOSO fold, the following metrics are evaluated:

1. **Macro Median Absolute Percentage Error (Macro MdAPE)** *(Primary Metric)*:
   $$\text{MdAPE}_s = \text{median}_{i \in \text{Source}_s}\left(\frac{|\hat{y}_i - y_i|}{y_i}\right) \times 100\%$$
   $$\text{Macro MdAPE} = \frac{1}{|S|} \sum_{s \in S} \text{MdAPE}_s$$
2. **$\text{PRED25}$**: Percentage of estimates within 25% of actual recorded effort:
   $$\text{PRED25} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}\left[\frac{|\hat{y}_i - y_i|}{y_i} \le 0.25\right] \times 100\%$$
3. **$\text{PRED50}$**: Percentage of estimates within 50% of actual recorded effort.
4. **Mean Absolute Error (MAE)**: Absolute effort discrepancy in person-hours.
5. **Root Mean Squared Logarithmic Error (RMSLE)**:
   $$\text{RMSLE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\ln(\hat{y}_i + 1) - \ln(y_i + 1))^2}$$
6. **Standardized Accuracy (SA)**:
   $$\text{SA} = \left(1 - \frac{\text{MAE}_{\text{model}}}{\text{MAE}_{\text{random\_guessing}}}\right) \times 100\%$$
7. **Empirical Conformal Interval Coverage**:
   - Nominal 80% Range ($P_{10}$–$P_{90}$): Observed percentage of projects where $y_i \in [\hat{y}_{p10}, \hat{y}_{p90}]$. Target: $80\% \pm 5\%$.
   - Nominal 50% Likely Band ($P_{25}$–$P_{75}$): Observed percentage where $y_i \in [\hat{y}_{p25}, \hat{y}_{p75}]$. Target: $50\% \pm 5\%$.

---

## 4. Frozen Decision Rules for RC3

### Decision Rule 1: Empirical Bayes Organizational Shrinkage Calibration

When organization actuals are submitted via the actuals flywheel (`/api/v1/estimates/{id}/actuals`), empirical Bayes shrinkage computes an organization multiplier $\gamma_{\text{org}}$:

$$w_k = \frac{k}{k + \tau_0^2}, \quad \tau_0^2 = 2.83$$
$$\ln \gamma_{\text{org}} = w_k \cdot \left(\frac{1}{k} \sum_{j=1}^k (\ln y_j - \ln \hat{y}_j)\right)$$
$$\gamma_{\text{org}} = \text{clip}\left(\exp(\ln \gamma_{\text{org}}), 0.33, 3.0\right)$$

**Pre-Registered Acceptance Criteria:**
- Shrinkage multiplier must be strictly non-negative and bounded within $[0.33, 3.0]$.
- At $k \ge 3$, shrinkage must demonstrate a relative Macro MdAPE improvement $\ge 8.0\%$ over uncalibrated baseline on held-out intra-organizational test sets.
- If $k = 0$ or no valid actuals exist, $\gamma_{\text{org}} \equiv 1.0$ (identity pass-through).

---

### Decision Rule 2: Challenger Model Displacement Criteria

A challenger model architecture shall displace the incumbent `MultivariateMonotoneModel` + `MondrianConformalPredictor` if and only if **all five** of the following conditions are met simultaneously:

1. **Accuracy Gain**: Macro MdAPE across the 6 LOSO folds improves by at least **3.0% relative**:
   $$\frac{\text{MdAPE}_{\text{incumbent}} - \text{MdAPE}_{\text{challenger}}}{\text{MdAPE}_{\text{incumbent}}} \ge 0.03$$
2. **Statistical Significance**: Paired two-sided Wilcoxon signed-rank test on absolute percentage errors achieves $p < 0.05$.
3. **Non-Inferiority on PRED25**: Overall $\text{PRED25}_{\text{challenger}} \ge \text{PRED25}_{\text{incumbent}} - 1.0\%$.
4. **Monotonicity Guarantee**: First-order partial derivative of predicted effort with respect to functional size is strictly non-negative everywhere:
   $$\frac{\partial \hat{y}}{\partial S} \ge 0, \quad \forall S \in [1, 10000]$$
5. **Zero Feature Fabrication**: The candidate must strictly require observable planning-time inputs (`size_fp`, `duration_months`, `team_size`) and ban proxy/synthetic features (e.g., T01-T15, fabricated entity counts).

If any of conditions 1–5 fails, the incumbent model remains frozen for production serving.

---

### Decision Rule 3: Zero-Pickle Serving Parity & Safety

To eliminate deserialization vulnerabilities:
1. Production serving must load exclusively from `model_params.json` using pure Python `json.load`.
2. Binary pickle files (`model.pkl`, `calibrator.pkl`) are strictly prohibited in the serving execution path.
3. Prediction outputs generated from `model_params.json` must match serialized reference outputs with maximum relative tolerance $\epsilon < 10^{-6}$.
4. Artifact loaders must fail closed immediately if `manifest.json` checksum, dataset checksum, or parameter checksum fails validation.
