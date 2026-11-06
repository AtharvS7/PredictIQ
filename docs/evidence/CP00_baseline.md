# CP00: Baseline, Branch & Hygiene Verification

**Date:** 2026-11-06T11:28:00+05:30  
**Status:** PASS  
**Agents & Skills Used:** `planner`, `code-explorer`, `opensource-sanitizer`, `using-git-worktrees`

---

## 1. Git State & Remote Inspection

- **Remote URL:** `https://github.com/AtharvS7/PredictIQ.git` (owner AtharvS7)
- **Starting Branch:** `dev2`
- **Target Branch Created:** `dev3` (via `git switch -c dev3` from current HEAD)
- **Local HEAD SHA at start:** `d7a66b4095b8ae84f818900c2199c243f9d46b5f`
- **origin/dev2 SHA:** `d7a66b4095b8ae84f818900c2199c243f9d46b5f` (identical to HEAD)
- **origin/main SHA:** `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43`
- **origin/dev3 Status:** Confirmed empty via `git ls-remote --heads origin dev3` (branch does NOT exist on remote prior to M1).
- **Working Tree Import Commit:** `c58f5d3` (`CP00: import local working-tree state`)
- **Worktree Gitignore Commit:** `5e3e962` (`CP00: add .worktrees/ to .gitignore`)

---

## 2. Hygiene & Tracked Files Check

- **.gitignore additions:**
  - `.agent/`
  - `.agents-disabled-*/`
  - `.tools/`
  - `.worktrees/`
  - `backend/ml/data/research/` (excluding raw itemlet 438MB file and research archives)
  - `backend/ml/experiments/`
  - Test/audit outputs: `backend/*-report.json`, `backend/*-results.txt`, `frontend/*-results.txt`, etc.
- **Tracked Files Audit:** No files over 50 MB are tracked. No `.env`, `.pem`, serviceAccount JSON, or cache directories are tracked.

---

## 3. Environment & Python Selection

Per `environment_rules`, the backend environment was tested:
- `.venv` configured to use Python 3.12.2 at `C:\Users\Atharv sawane\AppData\Local\Programs\Python\Python312\python.exe`.
- **Python version:** 3.12.2 (tags/v3.12.2:6abddd9, Feb 6 2024)
- **Key dependencies verified:**
  - `fastapi`: `0.111.0`
  - `scikit-learn`: `1.4.2`
  - `pandas`: `2.2.2`
  - `numpy`: `1.26.4`
  - `pytest`: `8.2.0` (with `pytest-cov` 7.1.0, `pytest-asyncio` 0.23.6)
  - `ruff`: `0.17.4`
  - `mypy`: `2.4.1`

---

## 4. Test Suite Baseline Execution (Outside Sandbox)

### A. Backend Tests (`pytest backend/tests`)
- **Command:** `& .\.venv\Scripts\python.exe -m pytest backend/tests`
- **Result:** `593 passed, 7 skipped, 3 failed, 7 warnings in 32.59s`
- **Coverage:** `82%` (2302 statements, 424 missed)
- **Failures Identified:**
  1. `test_fresh_packaged_artifacts_are_unrevoked_and_live`: Artifact in `backend/ml/` revoked or has label discrepancy as pre-documented.
  2. `TestAuthGuard::test_protected_endpoint_without_auth`: Auth header assertion mismatch.
  3. `test_parser_error_privacy.py[docx]`: Exception string containment expectation.

### B. Scripts Tests (`pytest scripts/tests`)
- **Command:** `& .\.venv\Scripts\python.exe -m pytest scripts/tests`
- **Result:** `25 passed, 4 skipped in 5.73s`

### C. Frontend Typecheck
- **Command:** `npm --prefix frontend run typecheck` (`tsc --noEmit && tsc -p tsconfig.test.json --noEmit`)
- **Result:** Exit code 0 (clean).

### D. Frontend Vitest
- **Command:** `npx vitest run --pool=forks --no-file-parallelism`
- **Note on Windows Hang:** Worker threads hang on Windows in vitest v4.1.11; running with `--pool=forks` completely resolves the hang and runs cleanly.
- **Result:** `15 test files passed, 85 passed in 52.55s`

### E. Frontend Build
- **Command:** `npm --prefix frontend run build`
- **Result:** Built in 22.54s; client production bundle created in `frontend/dist/`.

---

## 5. Artifact Hash Truth & Resolution

- Current disk hashes:
  - `backend/ml/predictiq_best_model.pkl`: `0bea59fbe69a5b17acdf9953d61e659b26d3450052fd8934b2b1e0b716e0b257`
  - `backend/ml/predictiq_scaler.pkl`: `b2ac866974acf7ef9d7dbbf58dcab255fec4008f391c7f8448cfead7b0ab81ad`
- **Resolution:** The `68c07e99...` hash in dev2 log was an uncommitted intermediate candidate model. The committed production model is `0bea59fb...`. Recorded in `docs/evidence/before_metrics.json`.

---

## 6. Dead-Code Inventory (Report Only)

- **Ruff F401/F841:**
  - `backend/ml/verify_e2e_pipeline.py:17`: `os` imported but unused
  - `backend/ml/verify_e2e_pipeline.py:24`: `EXPECTED_FEATURES` imported but unused
  - `backend/ml/verify_e2e_pipeline.py:84`: `timeline` assigned but unused
- **Mypy (`backend/app`):** 9 type errors in `config.py`, `estimate_service.py`, and `estimates.py`.

---

## 7. Isolated Worktrees Setup

Created 8 local worktree environments under `.worktrees/` branching off `dev3`:
1. `.worktrees/ws_a_data` (`agent/ws_a_data`)
2. `.worktrees/ws_b_core` (`agent/ws_b_core`)
3. `.worktrees/ws_b1_simple` (`agent/ws_b1_simple`)
4. `.worktrees/ws_b2_flex` (`agent/ws_b2_flex`)
5. `.worktrees/ws_c_serving_nlp` (`agent/ws_c_serving_nlp`)
6. `.worktrees/ws_d_qa` (`agent/ws_d_qa`)
7. `.worktrees/ws_e_frontend` (`agent/ws_e_frontend`)
8. `.worktrees/ws_f_docs` (`agent/ws_f_docs`)

Stale background tasks killed. Active tasks: 0.

---

## Gate Evaluation
- [x] Branch `dev3` exists locally
- [x] dev2 and main remote SHAs recorded
- [x] Baseline test counts and timings real and verified
- [x] Hygiene entries in place
- [x] Worktrees ready

**Gate Status:** PASS
