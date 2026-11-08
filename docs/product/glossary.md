# PredictIQ Canonical Product & Statistical Glossary

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Core Software Engineering & Sizing Metrics

### Function Point (FP)
A standardized, technology-independent unit of measurement representing the functional size of software as perceived by the end-user. Function points quantify logical business requirements by evaluating data storage (internal files, external interfaces) and transactional functionality (inputs, outputs, inquiries), independent of programming languages, frameworks, or developer implementation choices.

### IFPUG (International Function Point Users Group)
The global governing body that maintains the International Standard ISO/IEC 20926 for Function Point Analysis (FPA). IFPUG counting practices provide consistent, audited functional measurements across commercial and governmental software systems.

### Person-Month (PM)
A standard unit of software engineering labor equivalent to the productive working hours of one full-time software engineer over a calendar month. PredictIQ standardizes 1 Person-Month to exactly 152 productive person-hours, reflecting 19 eight-hour working days after accounting for non-project overhead.

### Brooks' Law
An established software engineering observation formulated by Fred Brooks in *The Mythical Man-Month*: *"Adding manpower to a late software project makes it later."* In estimation modeling, this principle dictates that effort and calendar duration cannot be traded off linearly because communication, coordination, and integration overhead scale non-linearly with team size ($O(n^2)$ communication channels).

---

## 2. Statistical & Machine Learning Terminology

### Leave-One-Source-Out (LOSO) Cross-Validation
A rigorous cross-validation protocol for multi-repository software datasets. In standard k-fold cross-validation, random shuffling across organizations leaks repository-specific practices into test folds. LOSO evaluates model generalization by holding out an entire external dataset source (e.g., all projects from China, Kitchenham, or Maxwell) during training and testing strictly on unseen external organizations.

### Median Absolute Percentage Error (MdAPE)
A robust measure of prediction accuracy defined as:
$$\text{MdAPE} = \text{median}\left(\frac{|y_i - \hat{y}_i|}{y_i}\right)$$
Unlike Mean Absolute Percentage Error (MAPE), which is vulnerable to catastrophic skew from extreme outlier projects, MdAPE evaluates the typical relative error across skewed software project distributions.

### Mondrian Conformal Prediction
A framework for group-conditional uncertainty calibration. While standard split-conformal prediction provides valid marginal coverage across an entire dataset, error spreads often vary systematically across project scales. Mondrian conformal prediction partitions the calibration space into discrete taxons (e.g., Small $<150$ FP, Medium $150$–$750$ FP, Large $>750$ FP), computing stratum-specific non-conformity quantiles to ensure balanced coverage across both small utilities and large enterprise systems.

### Exchangeability
The fundamental statistical assumption underlying conformal prediction. A sequence of random variables $Z_1, Z_2, \dots, Z_{n+1}$ is exchangeable if their joint probability distribution is invariant under permutations of indices. Conformal prediction provides finite-sample valid coverage properties whenever the calibration set and future test queries are exchangeable.

### Empirical Bayes Shrinkage
A statistical procedure that calibrates global population estimates toward specific organizational observations. When an organization records $k$ completed projects with observed actuals, PredictIQ calculates an adjustment weight $w_k = \frac{k}{k + \tau}$ (where $\tau = 2.83$ represents the prior variance ratio). For teams with few actuals ($k \le 2$), the model relies primarily on the global empirical baseline; as $k$ grows, predictions shift progressively toward internal team productivity.

### Monotone Power Law
An empirical regression model of the form:
$$E = a \cdot S^b$$
where $E$ represents effort in person-hours, $S$ represents functional size in Function Points, $a$ is the productivity coefficient, and $b > 0$ is the scaling elasticity exponent. The model enforces that effort increases strictly monotonically with functional scope ($\frac{\partial E}{\partial S} > 0$).

---

## 3. Quantile Intervals & Uncertainty Framework

### P10 / P50 / P90 Quantiles
Calibrated percentiles of the predicted effort distribution:
- **P50 (Median):** The central point estimate where observed effort has an equal probability of being higher or lower.
- **P10 (Optimistic Bound):** The 10th percentile representing a streamlined delivery scenario with minimal impediments.
- **P90 (Pessimistic Bound):** The 90th percentile representing a high-friction scenario with technical hurdles or scope churn.

### Likely Band (P25–P75)
The central 50% conformal prediction interval. This range captures the core probable envelope of effort under standard operational conditions, serving as the recommended baseline for sprint allocation and team staffing.

### Plausible Range (P10–P90)
The 80% conformal prediction interval. This range bounds 80% of observed project outcomes, providing an empirical safety envelope for fixed-bid contracts, executive commitments, and client statements of work.

### Out-of-Distribution (OOD) Diagnostics
Systematic checks verifying whether a user's input parameters fall within the empirical support of the training dataset. When projects exceed benchmark limits (e.g., $>3,000$ FP or $>100$ engineers), PredictIQ flags the estimate as OOD, signaling that prediction intervals widen appropriately to reflect heightened uncertainty rather than projecting artificial confidence.

---

## 4. Architectural & System Terminology

### Zero-Pickle Serving
A security pattern where model parameters, coefficients, and conformal quantiles are serialized to human-readable, schema-validated JSON manifests (`model_params.json`). During production serving, the runtime instantiates clean model objects directly from numeric parameters without executing Python `pickle.load()`, eliminating arbitrary code execution vectors.

### Fail-Closed Verification
A system resilience pattern where any integrity anomaly—such as a mismatched SHA-256 hash, missing manifest entry, or tampered parameter—immediately halts execution and raises a deterministic error rather than falling back to unvalidated defaults or degraded states.

### Actuals Flywheel
The closed-loop architectural subsystem that ingests completed project actuals (hours, cost, schedule), matches them against earlier estimates, and incorporates them into empirical Bayes shrinkage calculations for subsequent organizational forecasts.
