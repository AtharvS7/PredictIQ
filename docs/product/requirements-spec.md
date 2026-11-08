# PredictIQ Functional Requirements Specification

Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

---

## 1. Introduction & Traceability Framework

This specification defines the functional, algorithmic, and interface requirements for the PredictIQ platform. Every requirement is uniquely indexed with an alphanumeric identifier (`REQ-<SUBSYSTEM>-<ID>`), verification criteria, priority, and implementation mapping across backend endpoints and frontend components.

```text
Traceability Key:
  [REQ-AUTH]  Identity, Authentication, and Role-Based Access Control
  [REQ-DOC]   Document Ingestion, Format Validation, and Isolated Extraction
  [REQ-EST]   Effort, Cost, and Timeline Estimation Pipeline
  [REQ-UNC]   Uncertainty Calibration, Mondrian Buckets, and Quantile Bounds
  [REQ-ACT]   Actuals Flywheel and Empirical Bayes Shrinkage
  [REQ-BUD]   Deterministic Manual Task-Based Budgeting
  [REQ-FIN]   Multi-Currency Localization and Real-Time Conversions
  [REQ-EXP]   Export Governance, Share Links, and Artifact Integrity
  [REQ-OPS]   Operational Health, Preflight Diagnostics, and Telemetry
```

---

## 2. Authentication & Access Control (REQ-AUTH)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-AUTH-01` | Firebase Token Verification | The system must verify Firebase ID tokens via the Firebase Admin SDK on all protected API routes, checking cryptographic signatures, audience, issuer, and expiration. | Automated Integration Tests (`test_auth.py`) | P0 | `backend/app/core/security.py` |
| `REQ-AUTH-02` | Role-Based Access Control | The platform must enforce hierarchical access levels: `viewer` (read-only), `editor` (estimate generation and modification), and `admin` (system configuration and org settings). | Role Matrix Dependency Tests | P0 | `backend/app/core/security.py:require_role` |
| `REQ-AUTH-03` | User Profile Synchronization | The database must maintain a synchronized user profile for each authenticated user, persisting default currency, hourly rate, and timezone. | PostgreSQL Trigger & Profile Endpoint Tests | P1 | `backend/app/api/v1/profile.py`, `supabase/migrations/001_initial_schema.sql` |
| `REQ-AUTH-04` | Token Revocation Handling | The platform must reject revoked ID tokens and terminated sessions, returning HTTP 401 Unauthorized with descriptive challenge headers. | Negative Token Security Tests | P1 | `backend/app/core/security.py:get_current_user` |

---

## 3. Document Ingestion & Safe Parsing (REQ-DOC)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-DOC-01` | Multi-Format Ingestion | The platform must accept project requirements in PDF (`application/pdf`), Word (`.docx`), and plain text (`text/plain`) up to 10 MB per file. | File Ingestion Fixture Tests | P1 | `backend/app/api/v1/documents.py` |
| `REQ-DOC-02` | Archive & Signature Validation | The system must validate binary file magic bytes (`%PDF-`, standard PK zip headers) and enforce resource limits (max 2,000 zip entries, max 20 MB uncompressed) to prevent compression bombs. | Malicious Payload Tests | P0 | `backend/app/services/document_parser.py` |
| `REQ-DOC-03` | Isolated Subprocess Parsing | Text extraction for rich formats must execute within an isolated sandbox subprocess with memory and CPU timeouts to isolate memory safety issues. | Parser Timeout & Isolation Tests | P0 | `backend/app/services/isolated_parser.py` |
| `REQ-DOC-04` | NLP Scope Extraction | The parser service must scan extracted document text to identify candidate functional components, external interfaces, integrations, and proposed tech stacks. | SRS Extraction Benchmark Tests | P1 | `backend/app/services/nlp_extractor.py` |

---

## 4. Estimation Engine & Monotone Modeling (REQ-EST)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-EST-01` | Monotone Power-Law Inference | The effort engine must compute median development effort using a monotone power-law formulation ($E = a \cdot S^b$) where scaling exponent $b > 0$, ensuring $\frac{\partial E}{\partial S} > 0$ across all input ranges. | Mathematical Monotonicity Invariant Suite | P0 | `backend/ml/track1/models.py:MultivariateMonotoneModel` |
| `REQ-EST-02` | Bounded Duration Elasticity | When planned duration ($D$) is supplied, duration elasticity ($c$) must be bounded within $[0.2, 0.8]$ in log space, reflecting schedule constraints without violating Brooks' Law. | Duration Elasticity Unit Tests | P0 | `backend/ml/track1/models.py` |
| `REQ-EST-03` | Non-Imputed Missing Duration | When duration is omitted, the engine must evaluate the marginal power law on size alone rather than imputing artificial duration figures. | Null-Input Regression Tests | P1 | `backend/app/services/ml_service.py` |
| `REQ-EST-04` | Positive Effort Bounding | Estimated development effort must be bounded to $\ge 1.0$ person-hour for all non-empty inputs. | Boundary Value Assertion Tests | P0 | `backend/ml/track1/models.py:predict` |
| `REQ-EST-05` | Phase Breakdown Computation | The platform must allocate total effort and cost across five development lifecycle phases: Inception/Requirements, Architecture/Design, Implementation, Verification/Testing, and Deployment. | Phase Summation & Ratio Tests | P1 | `backend/app/services/cost_calculator.py` |
| `REQ-EST-06` | Risk & Volatility Analysis | The system must calculate an aggregate risk score (0–100) and discrete risk level (Low, Medium, High, Critical) based on team experience, volatility, and integration count. | Risk Matrix Evaluation Tests | P1 | `backend/app/services/risk_analyzer.py` |
| `REQ-EST-07` | Cost Synthesis | The system must convert effort hours to currency values using the user-specified or profile default hourly billing rate. | Financial Math Validation Tests | P0 | `backend/app/services/cost_calculator.py` |
| `REQ-EST-08` | Direct Sizing Input | The platform must allow direct numeric input of Functional Size (Function Points) as an alternative to document upload. | Wizard Form Flow Tests | P1 | `frontend/src/pages/NewEstimatePage.tsx` |

---

## 5. Calibrated Uncertainty & Interval Bounds (REQ-UNC)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-UNC-01` | Split-Conformal Calibration | The estimation service must produce empirical prediction intervals via split-conformal calibration with finite-sample exchangeability guarantees. | Coverage & Invariant Test Suite | P0 | `backend/ml/calibration/conformal.py` |
| `REQ-UNC-02` | Mondrian Size Conditioning | Calibration quantiles must be conditioned upon functional size buckets: Small ($< 150$ FP), Medium ($150$–$750$ FP), and Large ($> 750$ FP). | Stratified Coverage Tests | P0 | `backend/ml/calibration/conformal.py:MondrianConformalPredictor` |
| `REQ-UNC-03` | Non-Crossing Quantile Ordering | The system must enforce monotonic non-crossing ordering: $1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$ for all queries without exception. | Invariant Property-Based Testing | P0 | `backend/app/services/ml_service.py` |
| `REQ-UNC-04` | Dual Uncertainty Presentation | The user interface must present both the P25–P75 Likely Band (operational planning) and the P10–P90 Plausible Range (contractual risk limits). | UI Visual & DOM Assertions | P1 | `frontend/src/components/shared/ConfidenceInterval.tsx` |
| `REQ-UNC-05` | Out-of-Distribution Detection | The platform must evaluate input parameters against training boundaries and emit diagnostic alerts when size, duration, or team size exceed calibration envelopes. | OOD Trigger & Diagnostic Tests | P1 | `backend/app/services/ml_service.py:detect_ood` |

---

## 6. Actuals Flywheel & Empirical Bayes Shrinkage (REQ-ACT)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-ACT-01` | Project Actuals Ingestion | The platform must allow authenticated users to log completed project actuals: actual effort hours, final cost, elapsed duration, delivered team size, and functional size. | API Endpoint & Schema Tests | P1 | `backend/app/api/v1/actuals.py` |
| `REQ-ACT-02` | Empirical Bayes Calibration | The estimation service must adjust global priors toward organization actuals using shrinkage weight $w_k = \frac{k}{k + 2.83}$, clipping adjustments to $[0.33, 3.0]$. | Statistical Calibration Tests | P0 | `backend/app/services/ml_service.py` |
| `REQ-ACT-03` | Voluntary Training Consent | Submitting actuals must include an explicit opt-in boolean (`consent_for_training`), segregating consented records for future model updates. | Privacy & Schema Constraint Tests | P1 | `backend/app/models/actual.py` |
| `REQ-ACT-04` | Actuals Benchmark Export | The system must provide an export endpoint formatting logged actuals into compliant benchmark records for model evaluation. | Export Serialization Tests | P2 | `backend/app/api/v1/actuals.py:export` |

---

## 7. Deterministic Task-Based Budgeting (REQ-BUD)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-BUD-01` | Task Scenario Calculations | The platform must provide an independent manual planning track calculating low, likely, and high cost totals from user-supplied task hours and hourly rates. | Deterministic Math Tests | P0 | `backend/app/models/budget.py:calculate_budget` |
| `REQ-BUD-02` | Strict Ordering Validation | Every budget task must enforce low hours $\le$ likely hours $\le$ high hours, rejecting ill-formed task configurations. | Pydantic Model Validator Tests | P0 | `backend/app/models/budget.py:BudgetTask` |
| `REQ-BUD-03` | Contingency Allocation | The budget calculator must apply a uniform contingency percentage ($0$–$100\%$) across all tasks and round final currency values to cents. | Precision Rounding Tests | P1 | `backend/app/api/v1/budgets.py` |

---

## 8. Multi-Currency Localization (REQ-FIN)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-FIN-01` | Multi-Currency Support | The system must support cost conversions across USD, EUR, GBP, CAD, AUD, and INR. | Currency Enum & Conversion Tests | P1 | `backend/app/services/currency_service.py` |
| `REQ-FIN-02` | Cached Exchange Rates | The currency service must fetch and cache exchange rates with an automated daily refresh and failover to fallback parity tables. | Cache Expiry & Network Fallback Tests | P1 | `backend/app/services/currency_service.py` |
| `REQ-FIN-03` | Client-Side Currency Toggle | The frontend user interface must instantly convert all displayed costs, tables, and charts upon currency selection without reloading the page. | Zustand Store State Tests | P1 | `frontend/src/store/currencyStore.ts` |

---

## 9. Sharing, Export & Artifact Governance (REQ-EXP)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-EXP-01` | Secure Share Links | The platform must allow users to generate public, read-only estimate links with optional password protection and configurable expiration windows ($1$–$365$ days). | Link Expiry & Auth Token Tests | P1 | `backend/app/api/v1/estimates.py:share` |
| `REQ-EXP-02` | Multi-Format Export | The system must export complete estimate dossiers in JSON (machine-readable) and PDF/HTML (human-readable executive report). | Export Contract & Generation Tests | P1 | `backend/app/api/v1/export.py` |
| `REQ-EXP-03` | Model Transparency Record | Every estimate must record the exact model version, training dataset SHA-256, parameter manifest hash, and calibration quantiles used during generation. | Transparency Manifest Audits | P0 | `backend/app/services/estimate_service.py` |

---

## 10. Operational Health & Telemetry (REQ-OPS)

| ID | Title | Description | Verification Method | Priority | Implementation Path |
|---|---|---|---|---|---|
| `REQ-OPS-01` | Liveness & Readiness Probes | The API must expose `/api/v1/live` for process uptime and `/api/v1/ready` for database connectivity and artifact integrity status. | HTTP Probe Execution Tests | P0 | `backend/app/api/v1/health.py` |
| `REQ-OPS-02` | Cryptographic Preflight | Model serving must verify SHA-256 hashes of all model weights and calibration parameters against `manifest.json` at startup, failing closed on discrepancy. | Preflight Integrity Check Tests | P0 | `backend/ml/artifacts/loader.py` |
| `REQ-OPS-03` | Zero-Pickle Serving | Serving inference must load model architecture and calibration boundaries strictly from validated JSON manifests (`model_params.json`). | Deserialization Security Tests | P0 | `backend/ml/artifacts/loader.py` |
