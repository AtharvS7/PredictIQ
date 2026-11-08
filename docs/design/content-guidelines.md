# PredictIQ Content & Uncertainty Communication Guidelines

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Principles of Plain-Language Uncertainty Communication

Software project estimation is fundamentally an exercise in risk quantification under incomplete information. Traditional tools either present ungrounded point estimates that project false precision or overwhelm users with dense academic statistics.

PredictIQ adheres to four core editorial principles across documentation and user interfaces:

1. **Quantify Uncertainty Honestly:** Always pair central tendencies with calibrated intervals. Never present a single-point number as an inevitable outcome.
2. **Explain Mechanics in Plain Terms:** Translate mathematical concepts (such as conformal quantiles, log-normal distributions, and shrinkage) into concrete engineering implications.
3. **Respect Operational Realities:** Acknowledge that real-world software delivery involves organizational friction, changing requirements, and team learning curves.
4. **Reject Unsubstantiated Marketing Claims:** Ban marketing hyperbole and hype terminology in favor of auditable, empirically verified facts.

---

## 2. Communicating Confidence Intervals & Probabilities

PredictIQ outputs two distinct uncertainty intervals for every estimate. Content across the application must maintain clear distinctions between their operational purposes:

### 2.1. The Likely Band ($P_{25}$ to $P_{75}$, Inner 50% Band)
- **Terminology:** Always refer to this range as the **"Likely Band"** or **"Core Operational Range"**.
- **Explanation:** *"This interval represents the central 50% probability envelope under typical delivery conditions. Half of all historical projects of this scope were delivered within these bounds. Use this band for standard quarterly capacity planning and sprint milestone targets."*
- **Avoid:** Do not call this a "safe target" or an "average case".

### 2.2. The Plausible Range ($P_{10}$ to $P_{90}$, Outer 80% Range)
- **Terminology:** Always refer to this range as the **"Plausible Range"** or **"Contractual Risk Envelope"**.
- **Explanation:** *"This interval captures 80% of observed historical outcomes across verified benchmark projects. The lower bound ($P_{10}$) reflects an ideal delivery scenario with zero friction, while the upper bound ($P_{90}$) accounts for scope volatility, integration delays, or technical hurdles. Use this range for fixed-price contracts and contingency budgeting."*
- **Avoid:** Do not describe $P_{90}$ as a "worst-case scenario" (outliers can exceed $P_{90}$) or $P_{10}$ as a "minimum bid".

---

## 3. Explaining Out-of-Distribution (OOD) Diagnostics

When an estimate exceeds the size, team, or schedule boundaries of the benchmark cohort, the user interface displays an OOD notification. The content must clearly explain why intervals expand:

### 3.1. Plain-Language Messaging
- **Headline:** *"Anomalous Project Parameters Detected"*
- **Body Text:** *"One or more parameters for this project exceed empirical benchmark calibration envelopes (e.g., project size $>3,000$ Function Points or team size $>50$ engineers). Because fewer empirical data points exist at this scale, PredictIQ widens the prediction intervals to reflect heightened uncertainty rather than projecting artificial confidence. This widening is a deliberate statistical property that reflects epistemic risk."*

---

## 4. Prohibited Terminology & Replacement Vocabulary

To preserve scientific credibility, PredictIQ prohibits promotional buzzwords, speculative superlatives, and claims of absolute certainty across all user-facing documentation, tooltips, and marketing pages.

### 4.1. Banned Words Policy
The following terms are banned unless quoting an external citation directly:
- **"Guaranteed" / "Guarantee"** (Replaced by: *bounded*, *calibrated*, *enforced by invariant*, *statistically verified*)
- **"State-of-the-Art"** (Replaced by: *empirically grounded*, *modern statistical*, *formally evaluated*)
- **"Industry-Grade"** (Replaced by: *production-ready*, *enterprise-tested*, *cryptographically verified*)
- **"100% Accurate" / "Flawless" / "Perfect"** (Software estimation cannot achieve perfection; predictions are *calibrated approximations*)
- **"AI Magic" / "Intelligent Guessing"** (PredictIQ relies on *transparent power-law regression and conformal inference*, not black-box magic)

### 4.2. Replacement Lexicon Table

| Prohibited or Discouraged Term | Approved Replacement Term | Contextual Rationale |
|---|---|---|
| *"Guaranteed delivery within 6 months"* | *"Bounded $P_{90}$ timeline of 26 calendar weeks"* | Empirical models quantify probabilities, not guarantees. |
| *"State-of-the-art ML algorithm"* | *"Monotone power-law model with Mondrian conformal calibration"* | Concrete model architectures are verifiable; superlatives are not. |
| *"Industry-grade codebase"* | *"Enterprise-tested codebase with automated test suites"* | Replaces marketing buzzwords with factual verification evidence. |
| *"Average developer speed"* | *"Empirical baseline productivity ($a = 24.3$ hrs/FP)"* | Averages obscure skewed software engineering distributions. |
| *"Cost prediction"* | *"Cost estimation range"* | "Prediction" often implies a single exact number; "estimation range" reinforces uncertainty. |
| *"Gut check / Heuristic"* | *"Empirical benchmark comparison"* | Distinguishes data-grounded comparisons from subjective guesswork. |

---

## 5. Standardized Metric Formatting

All documentation, tables, charts, and exports must adhere to standardized formatting rules:

- **Functional Sizing:** Always abbreviate Function Points as `FP` with an explicit space after the number (e.g., `450 FP`, not `450fp` or `450 points`).
- **Person-Hours:** Always spell out `person-hours` in prose, or format as `hrs` in compact tables (e.g., `1,250 person-hours`, `1,250 hrs`).
- **Person-Months:** Standardized to 152 productive hours per person-month:
  $$\text{Person-Months (PM)} = \frac{\text{Effort in Person-Hours}}{152}$$
  Always format to one or two decimal places (e.g., `8.2 PM`).
- **Currency Figures:** Format with comma separators and currency symbols, rounded to nearest dollar or cent (e.g., `$93,750 USD` or `€84,500 EUR`). Never show fractional fractions of cents in summary views.
