# PredictIQ v2.0.0 Release Notes

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Executive Release Summary

PredictIQ version `2.0.0` marks the general availability release of the software effort, cost, and scope estimation platform. Grounded in empirical software engineering research and modern conformal prediction, PredictIQ provides engineering leaders with mathematically sound, reproducible estimates accompanied by verified finite-sample uncertainty bounds.

---

## 2. Key Capabilities & Architectural Highlights

### 2.1 Monotone Power-Law Estimation Engine
- **Mathematical Formulation:** Implements univariate power-law regression ($E = a \cdot S^b$) with global parameters $a = 24.2408$ and $b = 0.8270$ fit over 915 verified software engineering projects.
- **Physical Monotonicity:** Guarantees strictly positive marginal effort ($\partial E / \partial S > 0$) across the complete domain. Adding functional scope never reduces estimated effort.
- **Brooks' Law Structural Alignment:** Duration is treated as an independent capacity constraint ($H = 152 \cdot T \cdot D$) rather than an effort multiplier, preventing schedule compression artifacts.

### 2.2 Mondrian Split-Conformal Uncertainty Quantification
- **Calibrated Prediction Envelopes:** Generates two nested, non-crossing estimation intervals ($1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$):
  - **80% Plausible Range ($P_{10}–P_{90}$):** Achieved **80.04%** macro-average coverage in out-of-company cross-validation (designed for budget caps and risk governance).
  - **50% Likely Band ($P_{25}–P_{75}$):** Achieved **45.85%** macro-average coverage (designed for sprint planning and milestone targets).
- **Size-Stratified Bucketing:** Non-conformity scores are computed across functional size strata (Small $<150$ FP, Medium $150–750$ FP, Large $>750$ FP) to account for project variance characteristics.
- **Uncertainty Propagation:** First-order Taylor series expansion propagates document parsing sizing variance ($\Delta S$) directly into conformal quantile widths.

### 2.3 Organizational Velocity Adaptation (Empirical Bayes)
- **Bayesian Normal Shrinkage:** Organizations registering historical project actuals ($k \ge 1$) adapt the global prior toward local velocity:
  $$w(k) = \frac{k}{k + 2.83}, \quad \gamma_{\text{org}} = \text{clip}\left(\exp(w(k) \cdot \overline{r}), 0.33, 3.00\right)$$
- **Measured Accuracy Gains:**
  - $k = 3$ projects: $+11.9\%$ error reduction
  - $k = 5$ projects: $+14.9\%$ error reduction
  - $k = 10$ projects: $+19.5\%$ error reduction

### 2.4 Robust Multi-Signal NLP Requirements Sizing
- **Multi-Format Parsing:** Parses PDF, DOCX, Markdown, and plain text specifications with standardized UTF-8 normalization.
- **Eight-Signal Suite:** Detects user stories, tagged requirements (`REQ-`, `FR-`, `SR-`), normative verbs (`shall`, `must`), use cases, architectural modules, functional tables, acceptance criteria, and external integration points.
- **Plausibility Detection:** Flags diluted narrative documentation exceeding 3,000 words with sparse technical requirements.
- **Zero Exception Invariant:** Verified across 64 documents (including 18 real-world PURE specifications totaling 95,299 words) with zero server crashes and p95 latency of 0.23 seconds.

### 2.5 Enterprise Supply-Chain Security
- **Zero-Pickle Runtime:** Pure JSON serialization for model parameters and conformal quantiles (`model_params.json`). No untrusted Python object deserialization.
- **Canonical UTF-8 Cryptographic Integrity:** SHA-256 digests verified over canonical JSON representations (sorted keys, compact separators), providing fail-closed tamper resistance.

### 2.6 Full-Stack Modern Web Platform
- **Backend Service:** FastAPI 0.115+ running on Python 3.12 with PostgreSQL 15+ persistence, native Alembic schema migrations, and Firebase RS256 token authentication with Role-Based Access Control (`Viewer`, `Editor`, `Admin`).
- **Frontend Application:** React 19, TypeScript 5.5, Vite, Tailwind CSS, featuring interactive quantile distribution curves, Monte Carlo budget simulations, bulk project import (CSV/TSV/JSON), and PDF/CSV export.
- **One-Command Orchestration:** `python run.py` automatically validates system preflight and boots backend and frontend services.

---

## 3. Empirical Verification Summary

| Validation Suite | Scope | Result | Status |
|:-----------------|:------|:------:|:------:|
| **Backend Test Suite** | 50 source modules (`backend/tests`) | 717 passed, 6 skipped | Verified |
| **Scripts Test Suite** | Automation & pipelines (`scripts/tests`) | 63 passed, 4 skipped | Verified |
| **Frontend Test Suite** | React components & state (`frontend/src`) | 132 passed (24 suites) | Verified |
| **Static Type Safety** | Python (`mypy`) & TypeScript (`tsc`) | 0 type diagnostics | Verified |
| **Code Formatting** | Linting (`ruff check`) | 0 style diagnostics | Verified |
| **Specification Audit** | Documentation specifications (`docs/`) | 100% compliant (63 files) | Verified |
| **Remote Branch Protection** | Baseline tracking (`main`, `dev2`) | Strictly locked to baseline SHAs | Verified |

---

## 4. Documentation Specifications

- **Academic Technical Report:** [`report/PROJECT_REPORT.md`](report/PROJECT_REPORT.md)
- **Model Card:** [`ml/model-card.md`](ml/model-card.md)
- **Evaluation Results:** [`ml/EVALUATION_RESULTS.md`](ml/EVALUATION_RESULTS.md)
- **Organizational Calibration:** [`ml/org-calibration.md`](ml/org-calibration.md)
- **Architectural Diagrams:** [`architecture/diagrams/`](architecture/diagrams/) (11 Mermaid specifications)
- **API Contract:** [`contracts/api_estimate_v2.json`](contracts/api_estimate_v2.json)
- **Quickstart Guide:** [`../QUICK_START.md`](../QUICK_START.md)
