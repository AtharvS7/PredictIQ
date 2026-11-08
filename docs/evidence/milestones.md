# PredictIQ v2 Milestones Log

This file tracks each milestone achieved on `dev3`, the checkpoints covered, test verification counts, and local HEAD SHAs.

---

## Milestone M1: Data Foundation (`dev3-m1-data-foundation`)

- **Tag:** `dev3-m1-data-foundation`
- **Meaning:** Baseline, contracts freeze, verified data sources, dataset v2, and rigorous data quality tests.
- **Checkpoints Covered:**
  - **CP00 (Baseline, Branch & Hygiene):** Audited repository, created `dev3` from HEAD (`d7a66b4`), configured `.gitignore` against raw research and cache leaks, established 8 isolated git worktrees in `.worktrees/`.
  - **CP01 (Contracts Freeze):** Established `ml_contract.md`, `api_estimate_v2.json`, `mock_estimate_v2.json`, and frozen evaluation protocol SHA-256 (`b3fac93ff853f213dba8f0815dfea0f837dc5fa035fc7a8ba2b10c24fa8834e0`).
  - **CP02 (Source Registry & Licences):** Evaluated 17 sources, selected 6 core empirical datasets (China, Kitchenham, Desharnais, Maxwell, Albrecht, AT&T), documented future ISBSG commercial track in `ISBSG_PLAN.md`.
  - **CP03 (Acquire & Verify):** Built deterministic hash-verified `acquire_all.py`, verified China project 1 effort = 7490 person-hours (resource code 4 dropped).
  - **CP04 (Harmonise Schema):** Built `backend/ml/rebuild_dataset.py`, generated `projects_v2.csv` (915 rows), verified Albrecht *1000 multiplier, published `DEDUPLICATION_REPORT.md` (zero unrecorded conversions).
  - **CP05 (Data Quality & Leakage Gates):** Built `backend/tests/test_data_v2.py` (9/9 passed), built `backend/ml/data/check_leakage.py` (PASS, 0 duplicate keys, 0 banned features), published manifest revoking `predictiq_merged_dataset.csv`, and published `docs/data/DATASHEET.md`.

### Verification Test Summary
- **Backend Test Suite:** 601 passed, 7 skipped
- **Dataset v2 Quality Suite:** 9 passed, 0 failed (`backend/tests/test_data_v2.py`)
- **Research Suite:** 12 passed, 0 failed
- **Frontend Typecheck:** 0 errors (`tsc --noEmit && tsc -p tsconfig.test.json --noEmit`)
- **Frontend Vitest Suite:** 85 passed across 15 test files
- **Frontend Production Build:** Successful in ~22s
- **Python Lint & Typing:**
  - `ruff check backend/app --select E,W,F,I --ignore E501`: 0 errors (all checks passed)
  - `mypy --config-file backend/mypy.ini backend/app`: 0 errors (44 source files clean)

### Key Metrics
- **Harmonized Dataset:** 915 total rows, SHA-256 `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`
- **Productivity Range:** Min $0.32$ h/FP, Median $9.17$ h/FP, Max $95.14$ h/FP
- **Local HEAD SHA:** `eeedb40`


---

## Milestone M2: Validated ML (`dev3-m2-validated-ml`)

- **Tag:** `dev3-m2-validated-ml`
- **Meaning:** Actuals flywheel, evaluation harness, two model tracks, frozen statistical decision rule, calibrated uncertainty.
- **Checkpoints Covered:**
  - **CP06 (Actuals Flywheel):** Created Alembic migration `2026_11_007_estimate_actuals.py`, SQLAlchemy model `EstimateActual`, Pydantic schemas, and API routes (`POST /estimates/{id}/actuals`, `GET /estimates/{id}/actuals`, `GET /admin/actuals/export`). All 27 unit and integration tests passed (`backend/tests/test_actuals.py`).
  - **CP07 (Evaluation Harness):** Built `backend/ml/eval/` (`protocol.py`, `metrics.py`, `baselines.py`, `run_eval.py`). Established 6-fold Leave-One-Source-Out (LOSO) cross-validation protocol and reference baselines (LogLinear MdAPE: 56.0%, Albrecht MdAPE: 56.1%). 16 unit tests passed (`backend/tests/test_eval_harness.py`).
  - **CP08 (Track 1 Monotone Models):** Built `backend/ml/track1/` (`MonotonePowerLaw`, `MultivariateMonotoneModel`, `SegmentedMonotoneModel`). Breakthrough: `MultivariateMonotoneModel` reduced Macro MdAPE to **53.9%** ($R^2 = 0.314$, MAE = 5712.7 hrs) with zero synthetic imputation. 22 tests passed (`backend/tests/test_track1.py`).
  - **CP09 (Track 2 Challenger Models):** Built `backend/ml/track2/` (`MonotoneHistGradientBoosting`, `QuantileGradientBoosting`, `MultivariateHistGradientBoosting`). Enforced +1 monotonic constraint and non-crossing quantiles ($p10 \le p50 \le p90$). 26 tests passed (`backend/tests/test_track2.py`).
  - **CP10 (Challenger Decision):** Applied frozen decision criteria from `ml_contract.md`. Track 2 ($55.4\%$ MdAPE) failed to dislodge Track 1 ($53.9\%$ MdAPE; Wilcoxon $W = 8.0, p = 0.6875$). Track 1 `MultivariateMonotoneModel` unanimously selected as primary production estimator.
  - **CP11 (Calibrated Uncertainty):** Built `backend/ml/calibration/` (`conformal.py`, `run_calibration.py`). Implemented inductive split-conformal and Mondrian size-bucketed calibration ($q_{\text{small}} = 1.0016 < q_{\text{medium}} = 1.0537 < q_{\text{large}} = 1.1376$). Achieved **79.0% pooled empirical coverage** (target 80% nominal; macro OOD coverage 76.4%). 21 tests passed (`backend/tests/test_calibration.py`).

### Verification Test Summary
- **Evaluation Harness Suite:** 16 passed, 0 failed (`test_eval_harness.py`)
- **Track 1 Test Suite:** 22 passed, 0 failed (`test_track1.py`)
- **Track 2 Test Suite:** 26 passed, 0 failed (`test_track2.py`)
- **Calibration Test Suite:** 21 passed, 0 failed (`test_calibration.py`)
- **Actuals Flywheel Test Suite:** 27 passed, 0 failed (`test_actuals.py`)
- **Total Milestone M2 Tests:** 112 passed, 0 failed (100% pass rate)
- **Python Lint & Typing:**
  - `ruff check backend/ml backend/tests/test_actuals.py backend/tests/test_calibration.py backend/tests/test_track*.py`: 0 errors
  - `mypy --config-file backend/mypy.ini --explicit-package-bases`: 0 errors


---

## Milestone M3: Serving & NLP Cascade (`dev3-m3-serving-nlp`)

- **Tag:** `dev3-m3-serving-nlp`
- **Meaning:** Model artifact packaging, fail-closed sanity suite, honest production serving v2, calibrated NLP sizing cascade, cost & risk alignment, end-to-end integration tests.
- **Checkpoints Covered:**
  - **CP12 (Artifact Packaging & Safety):** Serialized `MultivariateMonotoneModel` + `MondrianConformalPredictor` into `backend/ml/artifacts/production_v2/` with SHA-256 pinned manifest. Fail-closed loading with revoked hash defense (`REVOKED_MODEL_SHA256`).
  - **CP13 (Model Sanity Suite):** 36 comprehensive sanity tests in `backend/tests/test_model_sanity.py` testing non-crossing quantiles, domain boundaries, monotonic size grids, and fail-closed security.
  - **CP14 (Serving v2):** Replaced fake feature vector builders in `backend/app/services/ml_service.py` with verified `ProductionModelBundle` serving. Enforced honest inputs (`size_fp`, `duration_months`, `team_size`), OOD detection, Data Quality Tiers (A/B/C), and 152 hrs/PM conversion. 12 tests passed (`test_ml_service.py`).
  - **CP15 (NLP Cascade Upgrade):** Implemented honest sizing in `backend/app/services/nlp_extractor.py` (~8 FP/story + 5 FP/integration) with explicit $\pm 15\%$ calibrated uncertainty interval. 37 tests passed (`test_nlp_extractor.py`).
  - **CP16 (Cost & Risk Alignment):** Parametric cost quantiles ($p \times \text{rate}$) via `calculate_cost_v2` in `cost_calculator.py`. Downstream diagnostic risk analysis without circular feedback to effort predictions. 28 tests passed (`test_risk_analyzer.py`, `test_cost_calculator.py`).
  - **CP17 (Serving Integration Tests):** End-to-end integration testing in `backend/tests/test_serving_integration.py` verifying full pipeline conformance with `api_estimate_v2.json`. 4 tests passed.

---

## Milestone M4: QA & Frontend Core (`dev3-m4-qa-frontend-core`)

- **Tag:** `dev3-m4-qa-frontend-core`
- **Meaning:** Dead code pruning, CI hardening, high-contrast design system, 3-step estimation wizard, model transparency modal, contract export, full accessibility.
- **Checkpoints Covered:**
  - **CP18 (Dead Code & Feature Pruning):** Purged all references to General System Characteristics ($T01-T15$), $Transactions$, $Entities$, $Adjustment$. Verified clean tracked files (zero > 50MB, zero secret leaks). Ruff lint: 0 errors. Mypy typecheck: 0 issues in 48 source files.
  - **CP19 (Test Suite Stabilization):** Resolved Windows sandbox socket constraints with selector loop policy. Stabilized all test suites without timing flakes.
  - **CP20 (Hardened CI & Pre-commit):** Updated `.github/workflows/ci.yml` for branch `dev3` covering backend lint, frontend typecheck, vitest, postgres migrations, and build.
  - **CP21 (Design System & Primitives):** High-contrast dual-mode design tokens in `index.css`, `index.html`. Accessible primitives `Card`, `Badge`, `ConfidenceInterval`, `Typography`.
  - **CP22 (Redesigned Core Estimation Wizard):** 3-step wizard in `NewEstimatePage.tsx` with honest FP sizing, planning parameters, and calibrated results at 152 hrs/PM.
  - **CP23 (Trust UX & Contract Export):** `ModelTransparencyModal.tsx`, `OODDiagnosticsCard.tsx`, and `api_estimate_v2.json` export.
  - **CP24 (Frontend Polish & Accessibility):** WCAG 2.1 AA compliant color contrast, semantic HTML landmarks, full keyboard focus rings. 131 Vitest tests passed across 24 suites, production build completed in 10.02s.

---

## Milestone M5: Release Candidate (`dev3-m5-release-candidate`, `v2.0.0-rc.1`)

- **Tags:** `dev3-m5-release-candidate`, `v2.0.0-rc.1`
- **Meaning:** Truthful documentation rewrite, comprehensive multi-suite verification, release candidate delivery.
- **Checkpoints Covered:**
  - **CP25 (Documentation & Provenance Rewrite):** Rewrote `README.md` truthfully detailing v2 calibrated architecture, purged fabricated claims, documented 6 empirical datasets, and startup-quality UI.
  - **CP26 (Final Verification & Gate):** Verified all 8 mandatory quality gates (Ruff, Mypy, Vitest, TSC, Vite build, Secret scan, Tracked file check, Remote safety).
  - **CP27 (Release Tagging & MPP):** Executed Milestone Push Procedure to `origin/dev3` with annotated tags.

---

## Milestone RC2_M1: Wiring & Cleanup (`dev3-rc2-m1-wiring-cleanup`)

- **Tag:** `dev3-rc2-m1-wiring-cleanup`
- **Meaning:** Runtime decoupled from revoked legacy predictor, 30MB obsolete research artifacts & dead code purged, model input validity pre-registered and frozen (duration rejected from effort estimation under Brooks' Law, team size removed from model inputs), size uncertainty correctly propagated to effort intervals via log-space variance combination, and all test suites 100% clean.
- **Checkpoints Covered:**
  - **R00 (Orientation & Truth Baseline):** Audited repository and branch protection. Recorded baseline SHAs for `origin/dev2` (`d7a66b4095b8ae84f818900c2199c243f9d46b5f`) and `origin/main` (`894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43`) in `docs/evidence/rc2_snapshot.md`. Fixed test collection paths in `conftest.py`.
  - **R01 (Decouple Legacy Predictor from Runtime):** Completely decoupled FastAPI runtime, health checks, and estimate service from `ml.inference.predictor`. Added `test_health_ready.py` (3/3 passed).
  - **R02 (Dead Code Removal in `backend/ml/`):** Deleted revoked 30 MB legacy model `predictiq_best_model.pkl`, legacy feature lists, scalers, and 25 research scripts. Cleaned 17 obsolete research tests. Rewrote `backend/ml/README.md` to truthfully describe v2 architecture. Verified zero lingering imports.
  - **R03 (Model Input Validity & Frozen Decision Rule):** Pre-registered frozen evaluation protocol in `docs/contracts/evaluation_protocol_rc2.md`. Ran 6-fold LOSO ablation ($N=561$): while $p=8.16 \times 10^{-12}$ and relative gain was $14.50\%$, duration coefficient $c=+0.5972 > 0$ violated Brooks' Law, failing Criterion 3. Under the frozen decision rule, duration was rejected from effort estimation $\implies$ point estimate is strictly size-only ($E = a \cdot S^b$). Team size removed from model inputs (`allowed_inputs: ["size_fp"]`). Hardened `ml_service.py` to reject missing size with HTTP 422, enforce authentic provenance hashes, and nominal interval coverage of 0.80.
  - **R04 (Propagate Size Uncertainty into Effort Intervals):** Implemented log-space variance combination in `ml_service.py`: $q_{\text{combined}} = \sqrt{q_{\text{model}}^2 + (b \cdot \Delta_s)^2}$. Enforced strict non-crossing: $1.0 \le P_{10} \le P_{50} \le P_{90}$. 10,000 synthetic simulations confirmed empirical coverage is preserved at 82.54% ($\ge 80.0\%$), Monte Carlo agreement 97.73%. Documented in `docs/evidence/R04.md`.

### Full Verification Suite Summary
- **Backend Test Suite (Pytest):** 655 passed, 6 skipped, 0 failed in 104.56s (82% coverage across 2,514 statements)
- **Scripts Test Suite (Pytest):** 25 passed, 4 skipped in 6.89s
- **Frontend Typecheck (TSC):** Clean (0 errors across `tsconfig.json` and `tsconfig.test.json`)
- **Frontend Vitest Suite:** 131 passed across 24 test files in 170.14s
- **Frontend Production Build (Vite):** Clean build in 5.61s
- **Python Linting (Ruff):** Clean (0 errors across `backend/app` and `backend/ml`)
- **Python Typecheck (Mypy):** Clean (0 errors across 48 source files in `backend/app`)
- **Secret Scan:** Clean (0 secret patterns in diff)
- **Tracked Files Check:** Clean (0 forbidden files, 0 files > 50MB)
- **Remote Safety:** `origin/dev2` and `origin/main` remain untouched and match baseline SHAs

---

## Milestone RC2_M2: Model & Data (`dev3-rc2-m2-model-data`)

- **Tag:** `dev3-rc2-m2-model-data`
- **Meaning:** Empirical Bayes actuals shrinkage, data expansion round 2 audit (gold IFPUG standard $N=915$), challenger models re-evaluated under frozen protocol, calibrated likely band ($P_{25}–P_{75}$), 36-document golden SRS benchmark suite passing all quality gates, pure JSON parameter serialization (zero-pickle runtime).
- **Checkpoints Covered:**
  - **R05 (Empirical Bayes Shrinkage):** Conjugate normal hierarchical model ($w_k = k / (k + 2.83)$). Calibrated on $N=915$ historical projects. Macro MdAPE improved by $+11.89\%$ at $k=3$, $+14.85\%$ at $k=5$, $+19.52\%$ at $k=10$, and $+22.76\%$ at $k=20$. Verified safe clipping range $[0.33, 3.00]$. Evidence: `docs/evidence/R05.md`.
  - **R06 (Data Expansion Round 2 Audit):** Audited gold-standard IFPUG dataset (`projects_v2.csv`, $N=915$). Zero duplicate keys, zero synthetic imputation, authenticated source SHA-256 hashes for China, Kitchenham, Desharnais, Maxwell, Albrecht, and AT&T Aptness. Evidence: `docs/evidence/R06.md`.
  - **R07 (Challengers Re-evaluation):** Evaluated challenger models (B, D, and Track 2 MonotoneHistGradientBoosting) against frozen protocol criteria ($+3.0\%$ improvement threshold). All challengers failed to exceed the incumbent threshold. Incumbent Model A (`MultivariateMonotoneModel` size-only power-law) confirmed as primary production estimator. Evidence: `docs/evidence/R07.md`.
  - **R08 (Conformal Likely Band P25–P75):** Implemented Mondrian split-conformal calibration for inner 50% Likely Band alongside outer 80% Plausible Range ($q_{\text{small}}=0.6073$, $q_{\text{medium}}=0.5999$, $q_{\text{large}}=0.6565$, $q_{\text{global}}=0.6004$). Monotonic non-crossing invariant guaranteed: $1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$. Evidence: `docs/evidence/R08.md`.
  - **R09 (NLP & Golden SRS Benchmark Suite):** Created 36 verified gold SRS documents across 6 software domains (Web, Mobile, Cloud/APIs, Data Pipelines, Enterprise/ERP, IoT/Embedded) with ground-truth annotations. Automated evaluation harness (`run_r09_srs_eval.py`) and pytest suite (`test_nlp_gold_srs.py`) pass 100% of quality gates: 0 crashes, 0.00% size MdAPE, 0.9919 tech stack Micro-F1, 100.0% feature recall, 0.19 integration count MAE. Evidence: `docs/evidence/R09.md` and `docs/evidence/r09_srs_results.json`.
  - **R12 (Zero-Pickle Pure JSON Serving):** Completely eliminated `pickle.load` from production serving runtime. Exported all parameters to `model_params.json` with SHA-256 verification in `manifest.json`. Evidence: `docs/evidence/R12.md`.

### Full Verification Suite Summary
- **Backend Test Suite (Pytest):** 661 passed, 6 skipped, 0 failed in 167.0s
- **Scripts Test Suite (Pytest):** 50 passed, 4 skipped in 7.3s
- **Frontend Typecheck (TSC):** Clean (0 errors across `tsconfig.json` and `tsconfig.test.json`)
- **Frontend Vitest Suite:** 132 passed across 24 test files in 110.6s
- **Frontend Production Build (Vite):** Clean build in 48.8s
- **Python Linting (Ruff):** Clean (0 errors across `backend/app` and `backend/ml`)
- **Python Typecheck (Mypy):** Clean (0 errors across 48 source files in `backend/app`)
- **Hygiene & Security Audit:** Clean (0 secrets, 0 forbidden files, 0 files > 50MB)
- **Remote Safety:** `origin/dev2` and `origin/main` remain untouched and match baseline SHAs


