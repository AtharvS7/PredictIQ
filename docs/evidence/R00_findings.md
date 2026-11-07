# R00 Findings: Truth Baseline & Audit Investigation

**Program:** `PREDICTIQ_V2_RC2_HARDENING_PROGRAM`  
**Checkpoint:** R00 (Orientation & Truth Baseline)  
**Date:** 2026-11-07  
**Branch:** `dev3`  
**Commit:** `a2068352a7de575f8bf65ec2fe4a3a7e7ba37ccb`  

---

## 1. Issue Confirmation Matrix

| Issue ID | Hypothesis in Prompt | Verified Finding | Status |
| :--- | :--- | :--- | :---: |
| **I-01** | Backend test count mismatch (238 reported vs 597+ expected) | **CONFIRMED.** The previous session ran an explicit 12-file slice (238 tests). Running the full 62 test files failed during collection due to an import error in `test_async_work.py` (`ModuleNotFoundError: No module named 'backend'`) caused by `_repo_root` missing from `sys.path` in `conftest.py`. With this fixed, **757 tests collect across 62 test files**. | **CONFIRMED & FIXED** |
| **I-02** | Legacy predictor coupled to runtime (`health.py`, `estimate_service.py`, `main.py`) | **CONFIRMED.** `app/api/v1/health.py` lines 10, 30, 61, 73, 79, 82 import `from ml.inference import predictor`. `app/services/estimate_service.py` imports `predictor` for `model_version` and `feature_importance`. `main.py` lines 64-71 still attempts to load legacy `predictor`. | **CONFIRMED** |
| **I-03** | Model input validity: `team_size` 0% coverage; `duration_months` positive elasticity (+0.53); silent 150 FP default | **CONFIRMED.** `projects_v2.csv` has 0 rows with non-null `team_size`. `duration_months` has a positive exponent ($0.53$), meaning compressing schedule lowers estimated effort (economically counter-intuitive). `ml_service.py` defaulted missing size to 150 FP with Tier A. | **CONFIRMED** |
| **I-04** | Pickle dependency in production serving bundle (`model.pkl`, `conformal.pkl`) | **CONFIRMED.** `loader.py` calls `pickle.load()` on custom dataclasses and NumPy arrays, triggering version warnings and potential portability failures. | **CONFIRMED** |
| **I-05** | Missing NLP SRS test fixtures (`backend/tests/fixtures/srs`) | **CONFIRMED.** Directory `backend/tests/fixtures/srs` is absent on disk. Sizing uses unvalidated heuristic constants (8 FP/story, 5 FP/integration). | **CONFIRMED** |
| **I-06** | README.md branch diff language and unsupported claims | **CONFIRMED.** `README.md` reads as a changelog comparing `dev2` vs `dev3` with claims like "outperforming gradient boosted trees" (despite $p=0.69$). `backend/ml/README.md` still describes models as revoked. | **CONFIRMED** |

---

## 2. Real System Baseline Numbers

### Backend & Core Services
- **Collected Pytest Tests:** **757 test cases** across 62 files in `backend/tests/`.
- **Collection Time:** 18.36s (unbuffered, no coverage overhead during discovery).
- **Service Liveness (`GET /api/v1/live`):** HTTP 200 `{"status": "alive"}`.
- **Service Readiness (`GET /api/v1/ready`):** HTTP 200 with active production v2 model bundle (`model_version: 2.0.0-rc.1`, 915 training samples, `MultivariateMonotoneModel + MondrianConformalPredictor`).

### Frontend
- **TypeScript Static Check:** 0 errors (`tsc --noEmit`).
- **Vitest Unit & Component Tests:** 131 tests passed across 24 test files.
- **Production Bundle:** Clean Vite build completed in 42.07s (0 errors).

---

## 3. Remote State & Safety Verification
- `origin/dev2`: `d7a66b4095b8ae84f818900c2199c243f9d46b5f` (strictly verified untouched).
- `origin/main`: `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43` (strictly verified untouched).
- `origin/dev3`: `a2068352a7de575f8bf65ec2fe4a3a7e7ba37ccb` (up to date with local HEAD).
