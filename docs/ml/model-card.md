# PredictIQ Model Card: Monotone Power-Law v2.0

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Model Details

- **Model Name:** Monotone Power-Law Software Effort Estimator
- **Model Version:** `2.0.0-rc.3`
- **Architecture:** Univariate Monotone Power-Law ($E = a \cdot S^b$) with Mondrian Split-Conformal Prediction and Empirical Bayes Shrinkage
- **Primary Input:** Functional size in IFPUG Function Points (`size_fp`)
- **Primary Output:** Total engineering effort in person-hours ($E$) with calibrated uncertainty quantiles ($P10, P25, P50, P75, P90$)
- **Fitted Global Parameters:**
  - $\beta_0 = 3.1880360932291065 \implies a = \exp(\beta_0) \approx 24.240774$
  - $b = 0.8270266757672359$ ($95\%$ bootstrap CI: $[0.778, 0.876]$)
- **Serving Serialization:** Pure JSON (`model_params.json`, `manifest.json`), zero pickle dependency
- **Cryptographic Digest:** Canonical UTF-8 SHA-256 `8066e9cf4c18f5fa45957bad9050cbab6effb68923a787f974640a463ede93d2`

---

## 2. Intended Use

- **In-Scope Use Cases:**
  - Early-stage software engineering project effort estimation.
  - Project risk assessment and contractual budget-cap setting via the 80% Plausible Range ($P10–P90$).
  - Sprint capacity planning and milestone target setting via the 50% Likely Band ($P25–P75$).
  - Organizational velocity adaptation via Empirical Bayes shrinkage ($k$ completed project actuals).
- **Out-of-Scope / Prohibited Uses:**
  - Individual developer performance evaluation, stack ranking, or surveillance.
  - Direct schedule forecasting from duration inputs (duration is an organizational capacity constraint governed by Brooks' Law, not an effort predictor).
  - High-consequence safety-critical bidding without domain expert review.

---

## 3. Training & Evaluation Data

- **Canonical Training Pool:** `backend/ml/data/projects_v2.csv` (915 records, SHA-256 `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`).
- **Harmonized Sources:** 6 empirical repositories (China $N=499$, Kitchenham $N=145$, AT&T Aptness $N=104$, Desharnais $N=81$, Maxwell $N=62$, Albrecht $N=24$).
- **Sizing Standard:** 100% IFPUG Function Points (AFP).
- **Effort Standard:** 100% verified productive person-hours.
- **Evaluation Protocol:** 6-Fold Leave-One-Source-Out (LOSO) cross-validation holding out each complete empirical source as an independent test set.

---

## 4. Empirical Performance Benchmarks

| Metric | Macro Average (LOSO) | Pooled Full-Dataset | Pre-Registered Floor |
|:-------|:--------------------:|:-------------------:|:--------------------:|
| **Median Relative Error (MdAPE)** | 56.31% | 58.35% | $\le 65.0\%$ |
| **Prediction Within 25% (PRED25)** | 20.21% | 21.09% | $\ge 17.0\%$ |
| **Mean Absolute Error (MAE)** | 5,875.2 hrs | 3,112.4 hrs | — |
| **80% Plausible Range Coverage** | 80.04% | 78.25% | $\ge 70.0\%$ |
| **50% Likely Band Coverage** | 45.85% | 48.85% | $\ge 45.0\%$ |

---

## 5. Organizational Calibration (Empirical Bayes)

For organizations logging historical project actuals, an Empirical Bayes conjugate normal shrinkage factor adapts the global intercept toward organizational velocity:
$$w = \frac{k}{k + 2.57}$$
- **$k=0$:** MdAPE = 52.59% (global baseline)
- **$k=5$:** MdAPE = 46.41% (+11.75% relative error reduction)
- **$k=10$:** MdAPE = 44.28% (+15.79% relative error reduction)
The scale elasticity exponent ($b = 0.8270$) is strictly locked to prevent small-sample overfitting.

---

## 6. Limitations & Known Weaknesses

1. **Empirical Variance:** Software development is inherently noisy. Typical prediction error on uncalibrated novel organizations is roughly $\pm 50\%$. Single-point estimates should never be used without uncertainty intervals.
2. **Dataset Age:** Historical repositories span projects developed between 1980 and 2010. While functional scaling laws remain stable, organizational calibration is strongly recommended to adapt to modern cloud-native architectures.
3. **Out-of-Distribution Domains:** Projects exceeding 4,100 Function Points lie outside the densest empirical training envelope and trigger advisory OOD warnings.
