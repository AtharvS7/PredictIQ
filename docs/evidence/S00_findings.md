# Checkpoint S00 Evidence: Orientation & Linux Truth Baseline

**Program:** `PREDICTIQ_RC3_PORTABILITY_VALIDITY_DOCS_PROGRAM`  
**Checkpoint:** `S00`  
**Status:** **PASS**  
**Role:** Orchestrator  
**Date:** 2026-11-08  
**Working Directory:** `E:\Codex\PredictIQ-dev3`  
**Working Branch:** `dev3`  
**Baseline HEAD SHA:** `cdca04128a3f8206d2d3a3f5a1a1f0a2e5e4fa44`  

---

## 1. Remote Branch Protection Attestation

```text
git ls-remote origin dev2 main
d7a66b4095b8ae84f818900c2199c243f9d46b5f	refs/heads/dev2
894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43	refs/heads/main
```

- `origin/dev2` remains strictly locked at `d7a66b4095b8ae84f818900c2199c243f9d46b5f` (**EXACT MATCH, UNTOUCHED**).
- `origin/main` remains strictly locked at `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43` (**EXACT MATCH, UNTOUCHED**).
- `git status`: `nothing to commit, working tree clean`.

---

## 2. Windows Baseline Test Suite Counts

Full suite executed and verified across all components:
- **Backend Test Suite (Pytest):** **661 passed, 6 skipped** in 167.0s
- **Scripts Test Suite (Pytest):** **50 passed, 4 skipped** in 7.3s
- **Python Linting (Ruff):** **0 errors** (`backend/app`, `backend/ml`)
- **Python Static Typing (Mypy):** **0 errors** across 48 source files
- **Frontend Typecheck (TSC):** **0 errors** (`tsc --noEmit && tsc -p tsconfig.test.json --noEmit`)
- **Frontend Unit/Component Tests (Vitest):** **132 passed** across 24 test files in 110.6s
- **Frontend Production Build (Vite):** `frontend/dist/` built cleanly in 48.8s
- **Hygiene & Security Audit:** **0 secrets, 0 forbidden files, 0 files > 50MB**

---

## 3. Real Endpoint Probes on Windows

Executed with TestClient against live FastAPI app (`RELEASE_MODE=prediction`):

### 3.1. GET `/api/v1/live` (HTTP 200)
```json
{"status":"alive"}
```

### 3.2. GET `/api/v1/health` (HTTP 200)
```json
{
  "status": "healthy",
  "release_mode": "prediction",
  "capabilities": {
    "manual_budget": true,
    "automatic_prediction": true
  },
  "version": "3.1.0",
  "uptime_seconds": 0,
  "services": {
    "database": "connected",
    "ml_model": "ready",
    "firebase": "initialized"
  },
  "model_loaded": true,
  "model_mode": "production_v2_monotone",
  "model_version": "2.0.0-rc.1",
  "best_model": "MultivariateMonotoneModel + MondrianConformalPredictor",
  "training_samples": 915,
  "n_features": 3,
  "r2_score": 0.314,
  "mdape": 0.539,
  "dataset_sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att_aptness"],
  "confidence_method": "mondrian_split_conformal_80pct",
  "interval_method": "inductive_conformal_p10_p50_p90",
  "nominal_interval_coverage": 0.8,
  "dataset_sha256": "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3",
  "manifest_sha256": "690da0cd5bc462cb021cbbec2f2199fc816cff39a02a55e3753cf72f432b69c3"
}
```

### 3.3. GET `/api/v1/ready` (HTTP 200)
```json
{
  "status": "healthy",
  "release_mode": "prediction",
  "capabilities": {
    "manual_budget": true,
    "automatic_prediction": true
  },
  "version": "3.1.0",
  "uptime_seconds": 0,
  "services": {
    "database": "connected",
    "ml_model": "ready",
    "firebase": "initialized"
  },
  "model_loaded": true,
  "model_mode": "production_v2_monotone",
  "model_version": "2.0.0-rc.1",
  "best_model": "MultivariateMonotoneModel + MondrianConformalPredictor",
  "training_samples": 915,
  "n_features": 3,
  "r2_score": 0.314,
  "mdape": 0.539,
  "dataset_sources": ["china", "desharnais", "kitchenham", "maxwell", "albrecht", "att_aptness"],
  "confidence_method": "mondrian_split_conformal_80pct",
  "interval_method": "inductive_conformal_p10_p50_p90",
  "nominal_interval_coverage": 0.8,
  "dataset_sha256": "b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3",
  "manifest_sha256": "690da0cd5bc462cb021cbbec2f2199fc816cff39a02a55e3753cf72f432b69c3"
}
```

---

## 4. Linux Model-Loading Bug Reproduction & Root Cause Analysis

### 4.1. Empirical Reproduction
We verified the SHA-256 of `backend/ml/artifacts/production_v2/model_params.json` across three representations:
- **Windows CRLF raw bytes (1,166 bytes):**
  `c8f746b8c006028faec9e1dfefab8f17b22b065e8ea45aa77cb971a098dda644`
- **Git repository tree object / Linux LF bytes (1,118 bytes):**
  `40ae4f6aec7437b7c3b7b4f4225111c791e5f20ba4b576ba9472b305abeee175`
- **Manifest expectation (`manifest.json`):**
  `c8f746b8c006028faec9e1dfefab8f17b22b065e8ea45aa77cb971a098dda644`

### 4.2. Exact Failure Trace on Linux
When checked out on Linux or in a container where line endings are LF:
```text
RuntimeError: SHA-256 checksum mismatch for 'model_params.json': expected c8f746b8c006028faec9e1dfefab8f17b22b065e8ea45aa77cb971a098dda644, got 40ae4f6aec7437b7c3b7b4f4225111c791e5f20ba4b576ba9472b305abeee175
```
Because `backend/ml/artifacts/loader.py` calls `_compute_sha256(artifact_path)` using raw binary file reading (`with path.open("rb")`), any difference in newline serialization (`\r\n` vs `\n`) produces completely different SHA-256 digests. There is currently no `.gitattributes` file enforcing consistent line endings across platforms.

### 4.3. Impact on Runtime
- On Windows: Bundle loads, `/health` and `/ready` return HTTP 200.
- On Linux: Model loading throws `RuntimeError`, `ml_service.is_ready()` is `False`, `/ready` returns HTTP 503, `/health` returns HTTP 503 degraded, and automatic prediction capabilities are disabled.

This proves the bug and establishes the baseline for Checkpoint S01.
