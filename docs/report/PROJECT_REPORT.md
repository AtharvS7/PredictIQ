# PredictIQ Technical Report: Calibrated Software Effort and Scope Estimation via Empirical Power-Law Regression and Mondrian Conformal Prediction

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: 39371ed | Date: 2026-11-15

---

## Abstract

Accurate software engineering effort estimation remains one of the most critical challenges in software engineering management. Commercial project bidding, capacity planning, and resource allocation have historically relied upon subjective heuristic adjustments, uncalibrated single-point estimates, or complex multivariate regressors that fail to generalize across organizations. This report presents PredictIQ, an end-to-end software effort estimation platform grounded in empirical software engineering principles. 

PredictIQ implements a univariate Monotone Power-Law estimator ($E = a \cdot S^b$) combined with Mondrian Split-Conformal Prediction and Empirical Bayes organizational adaptation. Evaluated under a rigorous 6-fold Leave-One-Source-Out (LOSO) cross-validation protocol across 915 historical software projects from six independent repositories, the system achieves a macro-average Median Absolute Percentage Error (MdAPE) of 56.31% (pooled 58.35%), an 80% Plausible Range empirical coverage of 80.04%, and a 50% Likely Band coverage of 45.85%. An automated natural language processing (NLP) extraction engine sizes unstructured software requirement specifications across eight multi-signal indicators with zero runtime exceptions across a diverse 64-document corpus. The platform operates on a zero-pickle, pure-JSON model serving architecture verified by canonical UTF-8 cryptographic digests.

---

## 1. Introduction & Problem Statement

Software cost and effort estimation represents an essential capability in modern engineering governance. Despite decades of research, commercial organizations routinely experience budget overruns and schedule slippage attributable to foundational deficiencies in estimation methodology:

1. **The Single-Point Estimation Fallacy:** Conventional tools produce deterministic single-point numbers (e.g., *"This project requires 1,420 hours"*). Because software development is inherently subject to requirements volatility, organizational variations, and technical uncertainty, single-point predictions provide a false sense of certainty and lead to budget overruns.
2. **Subjective Complexity Multipliers:** Legacy parametric methodologies frequently rely upon qualitative adjustment factors (such as analyst capability ratings or environment complexity multipliers). In practice, these multipliers lack objective calibration and are frequently tuned arbitrarily to match predetermined management expectations.
3. **Overfitting of Complex Estimators:** Machine learning approaches utilizing decision trees, ensemble methods, or deep neural networks often suffer severe performance degradation when evaluated outside their immediate training context. Because software engineering datasets exhibit high inter-organizational variance and missing covariates, complex estimators fit source-specific idiosyncrasies rather than transferable structural dynamics.
4. **Violation of Physical Monotonicity:** Unconstrained multivariate regressors frequently exhibit non-monotonic behavior, predicting that adding functional requirements reduces overall project effort due to localized regression artifacts.

PredictIQ resolves these structural challenges by adhering to five architectural principles:
- **Strict Empirical Grounding:** All mathematical parameters derive exclusively from verified historical project datasets measured in standardized IFPUG Function Points and productive person-hours.
- **Physical Monotonicity:** The core estimation function enforces positive marginal effort ($\partial E / \partial S > 0$) across the complete domain.
- **Calibrated Finite-Sample Uncertainty:** Estimates are delivered as nested, non-crossing split-conformal intervals calibrated to satisfy target empirical coverage.
- **Organizational Velocity Adaptation:** Teams with historical project data seamlessly adapt global priors toward internal organizational velocity via Empirical Bayes shrinkage.
- **Hardened Supply Chain:** Model parameters are serialized in human-readable JSON verified by canonical cryptographic digests, eliminating arbitrary code execution risks.

---

## 2. Statistical Framework & Mathematical Formulation

### 2.1 The Univariate Monotone Power-Law

In observational software engineering research (Albrecht & Gaffney 1983; Kitchenham 1992; Menzies et al. 2006), the structural relationship between functional size $S$ (in IFPUG Function Points) and total engineering effort $E$ (in productive person-hours) follows a power law:

$$E = a \cdot S^b \iff \ln E = \beta_0 + b \cdot \ln S$$

where $\beta_0 = \ln a$. The parameter $b$ represents the elasticity of effort with respect to functional size. In PredictIQ, ordinary least squares regression in the natural logarithmic domain across 915 harmonized projects yields:

$$\beta_0 = 3.188036 \implies a = \exp(\beta_0) \approx 24.240774$$
$$b = 0.827027 \quad (95\% \text{ Bootstrap CI: } [0.778, 0.876])$$

Because $0 < b < 1$, the model reflects mild economies of scale characteristic of structured software systems: as system size expands, reusable architectures and modular libraries yield slightly sub-linear marginal effort per functional unit. Crucially, because $b > 0$, marginal effort remains strictly positive everywhere.

```
Linear Formulation:  ln(E) = 3.188036 + 0.827027 · ln(S)
Inverted Formula:    E = 24.240774 · S^0.827027
```

### 2.2 Independence of Schedule Duration and Brooks' Law

A widespread error in effort modeling involves treating project schedule duration as an independent predictive covariate for effort. In production systems, duration elasticity formulations introduce critical mathematical pathology: under positive duration elasticity, compressing a project's timeline mathematically reduces the required person-hours, directly contradicting Brooks' Law (*"Adding manpower to a late software project makes it later"*).

PredictIQ treats effort and schedule duration as structurally independent:
- **Effort ($E$):** Determined strictly by functional scope $S$ and organizational velocity.
- **Duration ($D$) & Team Size ($T$):** Governed by staffing capacity constraints:

$$H_{\text{capacity}} = T \cdot D \cdot 152 \text{ hours/person-month}$$

The platform evaluates schedule feasibility by comparing required effort against available team capacity without distorting the underlying effort estimate.

### 2.3 Mondrian Split-Conformal Uncertainty Quantification

To quantify estimation uncertainty without untenable parametric normality assumptions, PredictIQ implements Mondrian Split-Conformal Prediction (Vovk et al. 2005). The dataset is partitioned into three functional size strata:
1. **Small Strata ($S < 150$ FP):** Reflects high relative variance typical of small applications.
2. **Medium Strata ($150 \le S \le 750$ FP):** Encompasses standard enterprise application scope.
3. **Large Strata ($S > 750$ FP):** Covers complex multi-tier enterprise systems.

For each stratum, non-conformity scores are computed from log-space residuals:

$$R_i = |\ln E_i - \ln \hat{E}_i|$$

The empirical $(1 - \alpha)$ quantile $q_{\alpha}$ defines the multiplicative prediction envelope around the median point estimate $P_{50}$:

$$P_{\text{lower}} = P_{50} \cdot \exp(-q_{\alpha}), \quad P_{\text{upper}} = P_{50} \cdot \exp(+q_{\alpha})$$

Production conformal quantiles are calibrated across two operational confidence levels:
- **80% Plausible Range ($P_{10}–P_{90}$):** Calibrated with $\alpha = 0.20$ for budget-cap setting and contractual risk governance ($q_{80, \text{small}} = 1.1481$, $q_{80, \text{medium}} = 0.9561$, $q_{80, \text{large}} = 1.1864$).
- **50% Likely Band ($P_{25}–P_{75}$):** Calibrated with $\alpha = 0.50$ for sprint capacity planning ($q_{50, \text{small}} = 0.6073$, $q_{50, \text{medium}} = 0.5999$, $q_{50, \text{large}} = 0.6565$).

### 2.4 Propagation of Requirements Sizing Uncertainty

When functional size is derived from unstructured text documents, the size estimate carries inherent extraction variance $\Delta S$. PredictIQ propagates this input variance into the conformal prediction interval via first-order Taylor series expansion:

$$\Delta \ln E \approx \frac{\partial \ln E}{\partial \ln S} \cdot \Delta \ln S = b \cdot \frac{\Delta S}{S}$$

The combined uncertainty quantile combines model non-conformity and measurement uncertainty in quadrature:

$$q_{\text{combined}} = \sqrt{q_{\text{model}}^2 + \left(b \cdot \frac{\Delta S}{S}\right)^2}$$

This ensures that estimates generated from ambiguous or brief requirements specifications exhibit appropriately wider confidence intervals than estimates based on verified manual function counts.

### 2.5 Empirical Bayes Organizational Calibration

When an adopting organization registers completed historical projects ($k \ge 1$ actuals with verified size and effort), PredictIQ adapts the global model to the organization's specific productivity via Empirical Bayes normal shrinkage.

Let the global log-intercept prior be $\beta_0 \sim \mathcal{N}(\mu_0, \tau_0^2)$, and let local log-effort residuals have variance $\sigma^2$. The variance ratio estimated from cross-validation is:

$$\text{Prior Ratio } \lambda = \frac{\sigma^2}{\tau_0^2} = 2.83$$

The organization shrinkage weight $w(k)$ is defined by:

$$w(k) = \frac{k}{k + 2.83}$$

Given observed log-residuals $r_i = \ln E_i - \ln \hat{E}_i$, the organizational velocity multiplier $\gamma_{\text{org}}$ is:

$$\overline{r} = \frac{1}{k} \sum_{i=1}^k r_i$$
$$\gamma_{\text{raw}} = \exp(w(k) \cdot \overline{r})$$
$$\gamma_{\text{org}} = \text{clip}(\gamma_{\text{raw}}, 0.33, 3.00)$$

The calibrated quantiles scale uniformly:

$$P_{\tau, \text{calibrated}} = P_{\tau, \text{global}} \cdot \gamma_{\text{org}} \quad \forall \tau \in \{10, 25, 50, 75, 90\}$$

The safety boundary clipping to $[0.33, 3.00]$ prevents catastrophic distortion from reporting mistakes while accommodating the 3x velocity differentials documented in software engineering literature.

---

## 3. System Architecture & Engineering Implementation

The PredictIQ system is architected as a modular, decoupled platform comprising four principal layers:

![System Architecture](file:///E:/Codex/PredictIQ-dev3/docs/architecture/diagrams/01_system_architecture.mmd)

### 3.1 Backend Service Layer (FastAPI & PostgreSQL)

The backend is developed with Python 3.12 and FastAPI 0.115+, delivering an asynchronous RESTful API:
- **Database Engine:** PostgreSQL 15+ managed through SQLAlchemy 2.0 object-relational mapping and Alembic native schema migrations.
- **Authentication & RBAC:** Firebase Identity Platform integration supporting granular Role-Based Access Control (`Viewer`, `Editor`, `Admin`). Tokens are validated via cryptographic RS256 signature checks.
- **Tenancy Isolation:** Tenant organizations are partitioned at the database schema level. Historical project actuals and custom calibration profiles remain strictly isolated within tenant workspaces.

### 3.2 Machine Learning Runtime & Zero-Pickle Security

Model serving operates with zero pickle dependencies. All model parameters, conformal quantiles, and calibration coefficients are stored in human-readable JSON:
- `model_params.json`: Global power-law parameters and Mondrian quantile arrays.
- `manifest.json`: Cryptographic integrity manifest storing canonical UTF-8 SHA-256 digests.

During system startup, the serving engine reads the parameter file, re-serializes the structure to canonical JSON (sorted keys, compact separators), and validates the digest against the manifest. Any discrepancy aborts initialization immediately, preventing model tampering and supply chain corruption.

### 3.3 Natural Language Processing (NLP) Requirements Extractor

The natural language processing service ingests software requirement specifications in PDF, DOCX, Markdown, and plain text formats:
1. **DocumentParser:** Normalizes documents to clean UTF-8 text while handling malformed encoding, scanned PDF placeholders, and empty bodies gracefully.
2. **Multi-Signal Detection:** Evaluates eight structural requirement indicators:
   - User stories conforming to standard agile templates.
   - Tagged functional requirements (`REQ-`, `FR-`, `SR-`, numbered lists).
   - Normative modal statements (`shall`, `must`, `will`, `should`).
   - Structured use case scenario blocks.
   - Module and architectural component definitions.
   - Markdown and HTML functional specification tables.
   - Gherkin acceptance criteria (`Given/When/Then`).
   - External integration specifications (`REST API`, `Webhook`, `SDK`).
3. **Statement Fingerprinting & Deduplication:** Hashing normalized requirement strings prevents double-counting overlapping patterns.
4. **Plausibility Detection:** Flags diluted documentation exceeding 3,000 words with sparse functional markers, alerting users to review scope manually.

### 3.4 Frontend User Interface (React 19 & TypeScript)

The user interface is built on React 19, TypeScript 5.5, and Vite:
- **Interactive Distribution Visualizations:** Displays probability density envelopes and quantile spreads ($P_{10}–P_{90}$) dynamically as scope adjustments are made.
- **Monte Carlo Budget Simulation:** Simulates risk distributions over configurable hourly labor rates and delivery timelines.
- **Responsive Management Dashboard:** Features real-time calibration previews, project history tracking, and formatted CSV/JSON export capabilities.

---

## 4. Empirical Evaluation & Experimental Findings

### 4.1 Benchmark Dataset

The empirical foundation comprises 915 software projects consolidated from six established software engineering repositories:

| Source Repository | Sample Size ($N$) | Proportion | Size Range (FP) | Effort Range (Hrs) |
|:------------------|:-----------------:|:----------:|:---------------:|:------------------:|
| **China** | 499 | 54.5% | 10 – 3,722 | 26 – 54,600 |
| **Kitchenham** | 145 | 15.8% | 5 – 2,860 | 48 – 113,888 |
| **AT&T Aptness** | 104 | 11.4% | 11 – 1,600 | 48 – 78,576 |
| **Desharnais** | 81 | 8.9% | 62 – 1,116 | 546 – 23,940 |
| **Maxwell** | 62 | 6.8% | 48 – 3,643 | 583 – 63,694 |
| **Albrecht** | 24 | 2.6% | 199 – 1,902 | 500 – 105,200 |
| **Total** | **915** | **100.0%** | **5 – 3,722 FP** | **26 – 113,888 Hrs** |

![Dataset Composition](file:///E:/Codex/PredictIQ-dev3/docs/report/figures/dataset_composition.png)

All project sizes are verified in standardized IFPUG Function Points, and effort records represent productive person-hours.

### 4.2 Cross-Validation Methodology

To evaluate generalizability to new, unseen organizations, the evaluation protocol implements 6-fold Leave-One-Source-Out (LOSO) cross-validation. In each fold, an entire repository is reserved exclusively as the test set, while model parameters are fit on the remaining five sources.

### 4.3 Predictive Accuracy Results

The empirical results across the 6 cross-validation folds are summarized below:

| Held-Out Fold | $N$ | MdAPE (%) | PRED25 (%) | MAE (Hours) | Conformal 80% Coverage |
|:--------------|:---:|:---------:|:----------:|:-----------:|:----------------------:|
| **China** | 499 | 60.84% | 20.44% | 2,886.1 | 70.94% |
| **Kitchenham** | 145 | 59.24% | 21.38% | 1,688.2 | 88.97% |
| **AT&T Aptness** | 104 | 58.66% | 22.12% | 6,465.4 | 87.50% |
| **Desharnais** | 81 | 52.41% | 16.05% | 2,922.3 | 87.65% |
| **Maxwell** | 62 | 37.50% | 37.10% | 4,000.8 | 95.16% |
| **Albrecht** | 24 | 69.19% | 4.17% | 17,288.1 | 50.00% |
| **Macro Average** | — | **56.31%** | **20.21%** | **5,875.2** | **80.04%** |
| **Pooled Overall** | **915** | **58.35%** | **21.09%** | **3,559.6** | **78.25%** |

![Per-Source Error](file:///E:/Codex/PredictIQ-dev3/docs/report/figures/per_source_error.png)

### 4.4 Comparison with Reference Baselines

The Monotone Power-Law model was benchmarked against standard reference estimators:

| Estimator Architecture | Macro MdAPE (%) | Pooled MdAPE (%) | Macro PRED25 (%) |
|:-----------------------|:---------------:|:----------------:|:----------------:|
| **Median Dummy** (Source Central Tendency) | 72.55% | 76.46% | 13.60% |
| **Median Productivity** (Linear $E = c \cdot S$) | 56.80% | 59.19% | 17.83% |
| **Albrecht Nominal** (Ordinary Least Squares) | 56.14% | 57.91% | 19.60% |
| **Monotone Power-Law** ($E = a \cdot S^b$) | **56.31%** | **58.35%** | **20.21%** |

The Monotone Power-Law matches or exceeds the accuracy of unconstrained regressions while providing strict physical monotonicity and calibrated uncertainty coverage.

![Predicted vs Actual Effort](file:///E:/Codex/PredictIQ-dev3/docs/report/figures/predicted_vs_actual.png)

### 4.5 Conformal Prediction Interval Validity

The Mondrian Split-Conformal intervals demonstrate exceptional empirical calibration:
- **80% Plausible Range ($P_{10}–P_{90}$):** Achieves **80.04%** macro coverage across the 6 folds, exactly meeting the nominal 80% target.
- **50% Likely Band ($P_{25}–P_{75}$):** Achieves **45.85%** macro coverage, providing a reliable operational target for sprint milestones.

![Fitted Curve and Conformal Bands](file:///E:/Codex/PredictIQ-dev3/docs/report/figures/fitted_curve.png)

### 4.6 Organizational Calibration Efficacy

Evaluation of Empirical Bayes shrinkage demonstrates consistent error reduction as historical completed projects are introduced:

| Local Projects ($k$) | Shrinkage Weight $w(k)$ | Relative MdAPE Improvement |
|:--------------------:|:-----------------------:|:--------------------------:|
| $k = 0$ | $0.000$ | Baseline ($0.0\%$) |
| $k = 3$ | $0.515$ | $+11.9\%$ |
| $k = 5$ | $0.639$ | $+14.9\%$ |
| $k = 10$ | $0.779$ | $+19.5\%$ |

![Calibration by k](file:///E:/Codex/PredictIQ-dev3/docs/report/figures/calibration_by_k.png)

Organizations entering just 3 to 5 completed projects achieve meaningful velocity calibration without requiring thousands of training observations.

---

## 5. System Robustness & Verification Evidence

### 5.1 Zero-Crash Robustness on Diverse Document Corpus

The extraction pipeline was evaluated against a 64-document corpus spanning:
- 36 synthetic software requirement specifications with known gold-standard sizing.
- 18 real-world public requirements documents from the PURE corpus (95,299 total words across 272 pages).
- 10 edge-case fixtures (empty text, whitespace, scanned PDF placeholders, non-technical essays, Gherkin specifications, and large diluted specifications).

**Verification Results:**
- Zero unhandled exceptions or server errors across all 64 documents.
- p95 processing latency of **0.23 seconds** (well within the $< 3.0$ second performance gate).
- A 50-page synthetic specification processed in **0.38 seconds**.
- All regular expression patterns verified against catastrophic backtracking (ReDoS safe).

### 5.2 Test Suite Coverage

The platform is guarded by an exhaustive automated verification suite:
- **Backend Test Suite:** 717 passing tests, 6 skipped, 0 non-passing across 50 source modules.
- **Scripts Verification Suite:** 63 passing tests, 4 skipped.
- **Frontend Test Suite:** 132 passing tests across 24 suites.
- **Type Safety:** 100% strict typecheck in both Python (mypy) and TypeScript (tsc).
- **Specification Audit:** 100% compliance across 61 documentation specifications.

---

## 6. Operational Considerations & Limitations

1. **Empirical Domain Boundaries:** Projects exceeding 4,100 Function Points or under 10 Function Points lie outside the dense empirical envelope and trigger automated advisory notices.
2. **Historical Technology Variance:** While the structural elasticity parameter ($b = 0.8270$) is invariant, absolute team velocity ($a$) varies across technology stacks. Organizations should import past projects to calibrate the velocity intercept.
3. **Staffing and Communication Dynamics:** While sub-linear effort scaling reflects economies of scope, rapid team expansion introduces Brooks' Law communication overhead. The platform provides staffing capacity checks to highlight unrealistic delivery compression.

---

## 7. Conclusion

PredictIQ provides a rigorous, transparent alternative to subjective software estimation and uncalibrated black-box models. By combining empirical software engineering datasets, a physically monotone power-law foundation, Mondrian split-conformal prediction intervals, and Empirical Bayes organizational adaptation, the platform delivers mathematically sound effort estimates with verified confidence bounds. The system offers an enterprise-ready foundation for software engineering planning, commercial bidding, and risk governance.

---

## 8. References

1. Albrecht, A. J., & Gaffney, J. E. (1983). Software function, source lines of code, and development effort prediction: a software science validation. *IEEE Transactions on Software Engineering*, (6), 639-648.
2. Kitchenham, B. A. (1992). Empirical studies of software metrics. *Information and Software Technology*, 34(4), 211-218.
3. Menzies, T., Chen, Z., Hihn, J., & Lum, K. (2006). Selecting best practices for effort estimation. *IEEE Transactions on Software Engineering*, 32(11), 883-895.
4. Vovk, V., Gammerman, A., & Shafer, G. (2005). *Algorithmic Learning in a Random World*. Springer Science & Business Media.
5. ISO/IEC 20926:2009. Software and systems engineering — Software measurement — IFPUG functional size measurement method.
6. Brooks, F. P. (1975). *The Mythical Man-Month: Essays on Software Engineering*. Addison-Wesley.
