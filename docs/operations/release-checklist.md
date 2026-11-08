Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Production Release Verification Checklist

This checklist specifies the mandatory, step-by-step procedures required to promote a PredictIQ release candidate from the development branch (`dev3`) to staging and production.

---

## Phase 1: Pre-Release Automated Quality Gate

Must be completed on the local release engineer workstation prior to tagging or triggering deployment:

- [ ] **1.1. Working Tree Hygiene**: Confirm working tree is completely clean (`git status` reports nothing to commit).
- [ ] **1.2. Protected Branch Verification**: Confirm `origin/main` and `origin/dev2` hashes match protected baselines:
  ```bash
  git ls-remote origin main dev2
  # origin/main must be: 894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43
  # origin/dev2 must be: d7a66b4095b8ae84f818900c2199c243f9d46b5f
  ```
- [ ] **1.3. Unified Release Gate**: Execute the full canonical release gate script:
  ```bash
  python scripts/release_gate.py
  ```
  Verify that all 9 steps pass:
  - [x] Step 1: Python Linting (Ruff: 0 errors)
  - [x] Step 2: Python Type Safety (Mypy: 0 errors)
  - [x] Step 3: Backend Test Suite (Pytest: 660+ tests passed)
  - [x] Step 4: Scripts Test Suite (Pytest: 50+ tests passed)
  - [x] Step 5: Frontend Typecheck (TSC: 0 errors)
  - [x] Step 6: Frontend Unit Tests (Vitest: 132 tests passed)
  - [x] Step 7: Frontend Production Build (Vite: dist/ created)
  - [x] Step 8: Security & Hygiene Audit (0 secrets, 0 files > 50MB)
  - [x] Step 9: Remote Branch Protection (Clean)
- [ ] **1.4. Zero-Pickle Verification**: Confirm `backend/ml/artifacts/production_v2/model_params.json` is present and loads cleanly without invoking `pickle.load`.

---

## Phase 2: Staging Deployment & Operational Smoke Testing

- [ ] **2.1. Staging Promotion**: Merge reviewed PR into `dev3` or trigger `.github/workflows/cd-staging.yml`.
- [ ] **2.2. Liveness & Readiness Verification**:
  ```bash
  curl -fsS https://staging-api.predictiq.io/api/v1/live
  curl -fsS https://staging-api.predictiq.io/api/v1/ready
  ```
  Verify HTTP 200 response with `"status": "healthy"`, `"database": "connected"`, and `"ml_model": "ready"`.
- [ ] **2.3. Automated Operations Probe**: Run concurrency and latency probes:
  ```bash
  python scripts/check_operations.py --base-url https://staging-api.predictiq.io --requests 50 --concurrency 5
  ```
  Confirm 0 errors and P95 latency $< 500\text{ms}$.
- [ ] **2.4. End-to-End User Journey Smoke Test**:
  - Authenticate using staging test account.
  - Create a manual estimate (Web App, 185 FP, 5 team members) &rarr; verify $P_{10} \le P_{50} \le P_{90}$ quantiles rendered.
  - Upload sample SRS document &rarr; verify entity and feature extraction.
  - Export PDF and JSON reports &rarr; verify schema conformance with `api_estimate_v2.json`.
  - Submit project actuals with training consent.

---

## Phase 3: Production Database Preparation & Migration

- [ ] **3.1. Database Snapshot**: Take a Point-in-Time snapshot or Neon recovery branch before applying any production change:
  ```bash
  neon branches create --project-id <PROJECT_ID> --name pre-deploy-backup-$(date +%Y%m%d%H%M)
  ```
- [ ] **3.2. Database Migrations**: Apply any pending Alembic migrations:
  ```bash
  cd backend && alembic upgrade head
  ```
  Confirm `alembic_version` matches current migration head.

---

## Phase 4: Production Deployment & Traffic Shift

- [ ] **4.1. Tag Release**: Create annotated Git release tag and push to remote:
  ```bash
  git tag -a v2.0.0-rc.3 -m "Release candidate 2.0.0-rc.3"
  git push origin v2.0.0-rc.3
  ```
- [ ] **4.2. Container Deployment**: Deploy production ECS tasks via `.github/workflows/cd-production.yml` (rolling zero-downtime update).
- [ ] **4.3. Frontend Asset Deployment**: Sync static assets to production S3 bucket and invalidate CloudFront edge cache.
- [ ] **4.4. Production Health Probe**:
  ```bash
  curl -fsS https://api.predictiq.io/api/v1/ready
  ```
  Verify HTTP 200 response.

---

## Phase 5: Post-Deployment Monitoring & Sign-Off

- [ ] **5.1. 30-Minute Monitoring Window**: Monitor CloudWatch metrics:
  - HTTP 5xx error rate remains $< 0.1\%$.
  - Database pool active connection gauge remains within normal limits ($< 50\%$).
  - Zero `ml_service_load_failed` or `corrupted_manifest` error logs.
- [ ] **5.2. Rollback Criteria**:
  If any of the following occur within the first 30 minutes, initiate immediate rollback:
  - Sustained 5xx error rate $> 1.0\%$.
  - `/api/v1/ready` returns 503 for $> 2$ minutes.
  - Critical estimation calculation discrepancy reported.
- [ ] **5.3. Formal Sign-Off**: Release manager signs off on deployment in `#ops-releases`.
