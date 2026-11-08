# Organizational Calibration & Empirical Bayes Shrinkage Specification

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Overview and Purpose

PredictIQ v2 models baseline software project engineering effort using a global Monotone Power-Law trained across 915 cross-organization historical software projects:
$$E = a \cdot S^b$$
Where $S$ denotes functional size in IFPUG Function Points and $E$ denotes total person-hours.

While the global model captures broad industry productivity curves, individual engineering organizations exhibit distinct productivity baselines driven by team maturity, technology stack familiarity, domain complexity, and organizational tooling. Organizational Calibration allows teams to supply historical completed projects to calibrate predictions to their specific velocity without the instability or overfitting risks of retraining models from scratch on small samples.

---

## 2. Mathematical Foundation: Empirical Bayes Shrinkage

PredictIQ implements Empirical Bayes shrinkage to adjust the intercept while locking the scale elasticity (slope exponent $b$).

### 2.1 Parameterization

1. **Global Base Model:**
   $$\ln(E) = \beta_0 + b \cdot \ln(S)$$
   $$\beta_{0, \text{global}} = 3.188036, \quad b_{\text{global}} = 0.827027$$
   $$a_{\text{global}} = \exp(\beta_{0, \text{global}}) \approx 24.2408$$

2. **Organization Residuals ($k$ Projects):**
   For an organization with $k$ historical projects with recorded size $S_i$ and actual effort $Y_i$:
   $$r_i = \ln(Y_i) - (\beta_{0, \text{global}} + b_{\text{global}} \cdot \ln(S_i))$$
   $$\Delta \log a_{\text{org}} = \frac{1}{k} \sum_{i=1}^k r_i$$

3. **Shrinkage Factor ($w$):**
   The Empirical Bayes shrinkage weight balances prior global knowledge against organization-specific evidence:
   $$w = \frac{k}{k + \frac{\sigma^2}{\tau^2}} = \frac{k}{k + 2.5789}$$
   Where:
   - $\sigma^2 \approx 0.441$ is the within-organization residual variance.
   - $\tau^2 \approx 0.171$ is the between-organization intercept variance.
   - Ratio $\sigma^2 / \tau^2 \approx 2.5789$.

### 2.2 Shrinkage Weight Schedule

| Past Projects ($k$) | Shrinkage Weight ($w$) | Influence of Org Actuals | Influence of Global Prior |
|:-------------------:|:----------------------:|:------------------------:|:-------------------------:|
| 0 | 0.000 | 0.0% | 100.0% |
| 1 | 0.280 | 28.0% | 72.0% |
| 3 | 0.538 | 53.8% | 46.2% |
| 5 | 0.660 | 66.0% | 34.0% |
| 10 | 0.795 | 79.5% | 20.5% |
| 20 | 0.886 | 88.6% | 11.4% |

### 2.3 Slope Preservation & Monotonicity
To ensure mathematical stability and prevent overfitting on small samples:
1. **Exponent Preserved:** $b_{\text{cal}} = b_{\text{global}} = 0.827027$.
2. **Intercept Shifted:** $\beta_{0, \text{cal}} = \beta_{0, \text{global}} + w \cdot \Delta \log a_{\text{org}}$.
3. **Quantile Scaling:** Conformal prediction intervals ($P10, P25, P50, P75, P90$) scale proportionally by the calibration multiplier:
   $$\text{ratio} = \exp(w \cdot \Delta \log a_{\text{org}})$$
   $$P_{q, \text{cal}} = P_{q, \text{global}} \cdot \text{ratio}$$
   This strictly ensures that $1.0 \le P10 \le P25 \le P50 \le P75 \le P90$ across all sizes.

---

## 3. Data Ingestion & Privacy Standards

### 3.1 Bulk Import Workflow
1. Organizations upload completed projects via `POST /api/v1/estimates/bulk-import` (CSV, TSV, or JSON).
2. The endpoint verifies:
   - Functional size ($S > 0$, IFPUG FP).
   - Actual effort ($E > 0$, person-hours).
   - Bounded values and finite numbers.
3. Users review a preview before confirming application to their workspace.

### 3.2 Tenant Isolation and Data Handling
- Historical project actuals are stored strictly within the organization's tenant workspace partition.
- Calibration parameters apply exclusively to estimates created within that workspace.
- Actuals are never pooled into global models without explicit consent flags.
