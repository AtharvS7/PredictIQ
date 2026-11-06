# Codebase Audit Report

**Audit date:** 2026-09-07 — re-audited with both `.env` files present  
**Project:** PredictIQ / Predictify  
**Inferred context:** Production-oriented FastAPI + React SaaS for software-project cost and timeline estimation. The supplied context placeholders were not filled, so this audit assumes a small team preparing for production and treats live cloud penetration testing, live database inspection, and external account configuration as out of scope.

## Re-audit Changes and Configuration Verification

This revision supersedes the first audit. Both added `.env` files were inspected without emitting secret values. All eight categories and the evidence underlying the existing findings were revisited. Application code and credentials were not modified. Findings concern this workspace and supplied deployment definitions, not verified live production state.

| Check | Re-audit result | Effect on earlier report |
|---|---|---|
| Frontend Firebase configuration | All six variables populated; Vite production env loading and Firebase client initialization passed without signing in | Blanket claim that local Docker lacks Firebase config withdrawn; H-08 narrowed to clean CI/CD builds |
| Backend database setting | Populated; exact URL also occurs in migration script | C-01 retained; no connection or validity test performed |
| Backend Firebase credentials | Configured JSON file absent; no raw-JSON env/process override | Remaining local setup blocker, M-20 |
| ML files | Configured model path exists; inference still uses hardcoded paths | No claim of currently missing artifacts; H-10 is a failure-mode risk |
| Storage | No backend env override | Local default applies; H-01/H-07 remain relevant |
| Docker context | No root or Dockerfile-specific ignore file; broad backend COPY includes env | New H-11 |
| Frontend build/lint | Same 2 TypeScript errors; lint 2 errors / 20 warnings | Independent of missing env |
| Frontend tests | Approved retry: 43 tests pass; 8.61% statements, 8.90% lines | Test-coverage gap confirmed |
| Dependencies | npm: 9 non-dev vulnerable-package entries, 14 full-graph entries; OSV flags 12 pinned Python package names | Package-level findings retained with reachability caveats |
| Backend test runtime | Only Python 3.9 installed, project targets 3.13; backend tests not run | Verification limitation, not a code vulnerability |

The earlier migration filename citation was incorrect and is corrected below. The table is `document_uploads`, not `documents`. Advisory counts are not counts of demonstrated exploits; Firebase Node transports and React Router server features may not execute in this browser SPA. Stable finding IDs are retained for comparison.

## Executive Summary

PredictIQ has a recognizable layered structure, useful backend test breadth, typed frontend code, and reasonable baseline controls such as Firebase authentication, parameterized database calls, CORS allowlisting, request IDs, and structured logging. The added env files resolve local frontend Firebase initialization, but the inspected release path is still **not ready for a production release**: the configured database credential is also embedded in source, the default Windows storage path is traversable, document uploads are disconnected from extraction and estimation, the backend lock file is unsatisfiable, and the frontend production build currently fails.

The operational safety net is also unreliable. Security jobs deliberately suppress failures, deployment is not gated on CI, health checks accept degraded/demo operation, local uploads are ephemeral in the documented production topology, and current dependency scans report multiple high/critical package advisories whose runtime reachability varies. The backend still references an absent Firebase Admin file in this workspace.

| Severity | Count |
|---|---:|
| Critical | 1 |
| High | 11 |
| Medium | 21 |
| Low | 5 |
| Informational | 2 |
| **Total** | **40** |

### Top 3 things to fix this week

1. Rotate and remove the embedded Neon credential, then inspect and rewrite Git history where necessary.
2. Repair the upload-to-extraction-to-estimation data flow and close the Windows storage traversal before accepting any more uploads.
3. Restore a trustworthy release path: regenerate the backend lock, fix the TypeScript build, patch vulnerable dependencies, and make CI/security failures block deployment.

## Project Map

- **Backend:** `backend/main.py` creates the FastAPI app and initializes Firebase, asyncpg, the ML singleton, benchmark data, middleware, and `/api/v1` routers. `backend/app/api/v1/` contains HTTP handlers, `backend/app/services/` contains storage/estimate/parser/ML logic, and `backend/app/core/` contains configuration, database, security, and exception helpers.
- **Frontend:** `frontend/src/App.tsx` owns React Router routes and auth gating. Pages call a shared Axios client in `frontend/src/lib/api.ts`; Zustand stores in `frontend/src/store/` manage auth, estimates, and currency state. Vite produces the static SPA.
- **Primary flow:** Firebase bearer token -> FastAPI auth dependency -> asyncpg/Neon. A document upload is intended to go through `StorageService`, then parser/NLP feature extraction, ML inference, persistence, and result/export/share UI.
- **External integrations:** Firebase Authentication/Admin SDK, Neon PostgreSQL, optional S3-compatible object storage, exchange-rate API, Railway, Vercel, and GitHub Actions.
- **ML:** Pickled model/scaler plus JSON feature/report artifacts in `backend/ml/`; training uses a 740-row, four-source historical dataset.
- **Build/deploy:** Separate backend/frontend Dockerfiles, nginx SPA/API proxy, production Compose, CI plus staging/production GitHub Actions.
- **Tests:** 316 backend test functions across 19 files; Vitest component/store tests; six Playwright smoke tests. Frontend coverage was measured during this audit at 8.61% statements.

## Findings by Severity

### Critical

#### C-01 — Database credential embedded in source

- **Category:** Security
- **Location:** `backend/scripts/run_migration.py:7-10`
- **Impact:** The file contains a real-looking Neon PostgreSQL URL with username and password. If usable, anyone with source or build-log access can read or modify production data. Even if currently revoked, it must be treated as exposed because Git history and downstream copies may retain it.
- **Effort:** S for rotation/removal; M for history cleanup and incident review
- **Recommendation:** Immediately rotate the database password, invalidate pooled connections, remove the fallback entirely, load only from a secret manager/environment variable, and scan all branches/tags/artifacts. Rewrite published Git history where appropriate and notify collaborators to reclone. Add provider-side IP/network restrictions and least-privilege migration credentials.
- **Re-audit evidence:** The literal exactly matches `DATABASE_URL` in the new backend `.env` (comparison returned a boolean only). Validity, privileges, and historical exposure were not tested. Critical priority is retained for a configured secret in source; no compromise is claimed.

### High

#### H-01 — Authenticated arbitrary file write on default Windows storage backend

- **Category:** Security
- **Location:** `backend/app/services/storage_service.py:56-60,210-216`; `backend/app/api/v1/documents.py:69-107`; `backend/app/core/config.py:43`
- **Impact:** `generate_key()` replaces `/` but not Windows `\\`; `LocalStorageBackend` joins the resulting key without resolving and checking containment. An authenticated user can supply a filename containing backslashes and `..` segments and write outside the upload directory with the backend process's permissions. The configured default is local storage. A read-only path-resolution proof during this audit showed a generated key escaping to the repository's `backend` directory.
- **Effort:** S
- **Recommendation:** Discard the client filename for object keys and generate a UUID plus a server-selected extension. Resolve the final path and require it to remain under the resolved base directory (`Path.is_relative_to`), rejecting absolute paths, drive prefixes, `..`, `/`, `\\`, NULs, and alternate separators. Apply editor RBAC and add traversal tests for Windows and POSIX.

#### H-02 — Core document analysis pipeline does not read uploaded objects

- **Category:** Architecture & design
- **Location:** `backend/app/api/v1/documents.py:105-122,205-241`; `backend/app/api/v1/estimates.py:62-92`; `backend/migrations/001_initial_schema.sql:23-33`; `supabase/migrations/001_initial_schema.sql:33-42`
- **Impact:** Upload writes bytes to `StorageService` and stores metadata, but extraction still reads the legacy `document_uploads.file_data` column. Extraction therefore returns “No file data stored”; estimate analysis substitutes empty bytes and can silently generate a plausible estimate from defaults/overrides instead of the uploaded specification. This invalidates the product's primary promise without necessarily surfacing an error.
- **Effort:** M
- **Recommendation:** Define one storage contract. Fetch bytes from the recorded `storage_path` through `StorageService` in both extraction and analysis, validate ownership/status, and fail closed when the object is absent or parsing fails. Remove the legacy BYTEA path after migration. Add an integration test that uploads a real fixture, extracts features, creates an estimate, and asserts document-derived values affect the result.

#### H-03 — Backend lock file is unsatisfiable and incomplete

- **Category:** Dependencies & supply chain
- **Location:** `backend/requirements.lock.txt:58-60`; `backend/requirements.txt:8-49`; `Dockerfile.backend:19-20`; `.github/workflows/ci.yml:73-76`
- **Impact:** The lock pins `limits` to two different exact versions. It also omits direct runtime dependencies including `asyncpg` and `firebase-admin`; S3 and migration code import `boto3`, `alembic`, and `sqlalchemy`, which are absent from both manifests. Clean Docker/CI installs cannot reliably construct a runnable application.
- **Effort:** S
- **Recommendation:** Declare every direct runtime and migration dependency once, split runtime/dev/tooling groups, and regenerate a resolver-produced, hashed lock for the supported Python version. Make a clean-image install/import/startup test mandatory in CI.

#### H-04 — Frontend production build currently fails

- **Category:** Code quality & maintainability
- **Location:** `frontend/src/components/__tests__/ErrorBoundary.test.tsx:19,22`; `frontend/tsconfig.json:6,28`; `frontend/package.json:8`; `.github/workflows/ci.yml:49-51,103-109`
- **Impact:** `npm run build` exits with TypeScript errors because test globals `beforeEach` and `afterEach` are not typed while tests are included in the production compiler input. Frontend artifacts and Docker images cannot be produced from the current tree.
- **Effort:** S
- **Recommendation:** Add `vitest/globals` to test compiler types or use a dedicated test tsconfig, and exclude tests from the production build tsconfig. Keep both test type-checking and production type-checking as separate CI commands.

#### H-05 — Production JavaScript dependency graph has known critical/high vulnerabilities

- **Category:** Dependencies & supply chain
- **Location:** `frontend/package.json:39-52`; `frontend/package-lock.json`
- **Impact:** On 2026-09-07, `npm audit --package-lock-only --omit=dev` reported **9 production vulnerabilities: 1 critical, 6 high, and 2 moderate**. Confirmed chains include direct `axios@1.15.0`, React Router 7.14.0, and Firebase 11.10.0 transitives such as `faye-websocket@0.11.4`, `websocket-driver@0.7.4`, `@grpc/grpc-js@1.9.15`, and `protobufjs@7.5.5`. The full graph reported 14 vulnerable-package entries. These include propagated/transitive entries, not unique CVEs or proven exploits. Firebase Node websocket/gRPC transports are not established as browser-bundle code; server-only Axios and React Router SSR/RSC advisories likewise need reachability analysis. The app imports Firebase Auth, not a websocket server. High denotes unresolved dependency-remediation priority, not a demonstrated critical remote app exploit.
- **Effort:** M
- **Recommendation:** Upgrade direct packages to versions that resolve the lock graph, run unit/e2e regression tests, and gate merges on `npm audit --omit=dev --audit-level=high`. Document accepted advisories with exploitability evidence and expiry dates rather than suppressing the command. Triage the websocket critical advisory ([GHSA-xv26-6w52-cph6](https://github.com/advisories/GHSA-xv26-6w52-cph6)).

#### H-06 — Pinned Python environment contains known high-severity vulnerabilities

- **Category:** Dependencies & supply chain
- **Location:** `backend/requirements.lock.txt`
- **Impact:** An OSV query of each pinned package on 2026-09-07 identified high-severity advisories affecting, among others, `python-multipart 0.0.24` (CPU/unbounded-header denial of service), `starlette 1.0.0` (form-limit bypass and Windows UNC behavior), `ecdsa 0.19.2` (timing side channel), `cryptography 46.0.7` (affected bundled OpenSSL), and `lxml 6.0.3` (XXE in relevant parser configurations). Multipart ingress makes relevant parser advisories worth prioritizing. No exploit was attempted; StaticFiles, ecdsa, or lxml configurations may be unused. The recheck matched 12 pinned package names; PYSEC/GHSA aliases require deduplication. This is a lock-manifest audit, not a successfully installed backend inventory.
- **Effort:** M
- **Recommendation:** First repair the dependency manifest, then regenerate against patched compatible versions and run `pip-audit`/OSV in CI. Remove unused packages to reduce exposure. Validate upload and crypto flows after upgrades. Relevant examples: [GHSA-5rvq-cxj2-64vf](https://github.com/advisories/GHSA-5rvq-cxj2-64vf), [GHSA-pp6c-gr5w-3c5g](https://github.com/advisories/GHSA-pp6c-gr5w-3c5g), [GHSA-82w8-qh3p-5jfq](https://github.com/advisories/GHSA-82w8-qh3p-5jfq).

#### H-07 — Uploaded documents are stored on ephemeral container disk by default

- **Category:** DevOps / CI-CD / Operations
- **Location:** `backend/app/core/config.py:43,49`; `docker-compose.yml:21-24`; `backend/.env.example:1-28`
- **Impact:** Production Compose mounts only ML artifacts while the default storage backend is local. Uploaded customer documents disappear on replacement/redeploy and may differ across replicas. Railway-style ephemeral filesystems amplify the data-loss risk.
- **Effort:** M
- **Recommendation:** Require durable object storage in staging/production, fail startup if local storage is selected outside development/test, document all S3 settings, encrypt objects, set lifecycle/retention policy, and test restore/deletion behavior. If local Compose persistence is intentionally supported, mount a named uploads volume and back it up.

#### H-08 — Clean CI/CD builds do not provision Firebase client configuration

- **Category:** DevOps / CI-CD / Operations
- **Location:** `frontend/src/lib/firebase.ts:8-18`; `Dockerfile.frontend:19-28`; `.gitignore` env rules; `.github/workflows/ci.yml:104-109`; `.github/workflows/cd-production.yml:33-39`; `.github/workflows/cd-staging.yml:16-20`
- **Impact:** **Local finding corrected:** Vite loads the new `frontend/.env`, and the Docker COPY currently includes it in local builds. All Firebase keys loaded and client initialization passed. Fresh Git checkouts normally exclude this ignored file, however, and the supplied CI/CD jobs provide no Firebase variables. Those builds remain liable to produce an unauthenticated frontend after H-04 is fixed. Provider-side settings outside this workspace were not inspected.
- **Effort:** S
- **Recommendation:** Explicitly provision public Firebase settings in every frontend build and validate them. Do not commit backend secrets or rely on a developer's local env. Coordinate H-11's Docker exclusions with explicit frontend config injection; test login against an isolated project.

#### H-09 — Security gates are intentionally fail-open

- **Category:** DevOps / CI-CD / Operations
- **Location:** `.github/workflows/ci.yml:130-147`; `.github/workflows/security-weekly.yml:46-64`
- **Impact:** Bandit first ignores its exit status, then a broad `except` catches the script's own `SystemExit`, so high findings pass. The weekly npm audit's final `|| true` suppresses its deliberate nonzero exit, meaning issue creation does not run for Node advisories. This was validated against the current lock, which contains high/critical findings.
- **Effort:** S
- **Recommendation:** Remove blanket suppression, parse only expected file/JSON errors, explicitly exit nonzero at policy thresholds, always upload reports, and add a small CI self-test fixture proving each gate fails when seeded with a finding.

#### H-10 — Inference silently falls back to plausible demo estimates

- **Category:** Architecture & design
- **Location:** `backend/ml/inference.py:52-75,113-116,139-186,225-249`; `backend/main.py:57-74`; `backend/app/api/v1/health.py:19-64`
- **Impact:** Current model files are present; this is a fallback-code risk, not an observed model outage. Missing/corrupt artifacts or any prediction exception produce realistic-looking fixed estimates and 60% “confidence.” Startup continues after model-load failure and health remains HTTP 200. The estimate response schema drops the predictor's `model_mode`, losing the distinction before the results UI. Customers can receive fabricated production estimates without a hard failure or prominent distinction.
- **Effort:** S
- **Recommendation:** Fail startup or mark readiness unavailable in production when artifacts cannot load. On per-request inference errors, return a typed 5xx error rather than demo output. Permit demo mode only behind an explicit development flag and expose it unmistakably in UI/API responses and telemetry.

#### H-11 — Backend env secrets would be copied into Docker images

- **Category:** Security
- **Location:** `Dockerfile.backend:42` (`COPY backend/ .`); `backend/.env`; absent `.dockerignore` / `Dockerfile.backend.dockerignore`
- **Impact:** A successful local backend image build would embed the newly added env file and its database credential in the final image layer. Git ignore rules do not exclude Docker context files. A service-account JSON placed under backend would also be included. Anyone with image access could recover those secrets. No image was built or published in this audit; H-03 currently blocks the build earlier.
- **Effort:** S
- **Recommendation:** Exclude env/service-account/cache files from Docker context and inject backend secrets at runtime. Rebuild and rotate if an affected image was distributed. Preserve explicit public frontend config injection when excluding frontend env files.

### Medium

#### M-01 — Revoked Firebase tokens are accepted

- **Category:** Security
- **Location:** `backend/app/core/security.py:102,110-145`
- **Impact:** `verify_id_token()` is called without `check_revoked=True`; the `RevokedIdTokenError` handler is therefore ineffective under the Admin SDK default. A revoked/disabled session can continue until token expiry.
- **Effort:** S
- **Recommendation:** Enable revocation checks for privileged and sensitive operations, or implement a documented cache/session-version strategy where latency is a concern. Test revoked and disabled users explicitly.

#### M-02 — Viewer role can upload files and trigger extraction

- **Category:** Security
- **Location:** `backend/app/api/v1/documents.py:69-73,205-209`
- **Impact:** These costly, mutating routes require authentication but not the editor role used by the metadata upload route. A viewer can consume storage/CPU and can chain the upload route with H-01.
- **Effort:** S
- **Recommendation:** Apply `require_role("editor")` consistently to upload/extract/mutation routes and create a route-by-role authorization matrix test.

#### M-03 — Upload validation permits memory/CPU exhaustion and parser bombs

- **Category:** Security
- **Location:** `backend/app/api/v1/documents.py:80-103`; `backend/app/services/document_parser.py:56-145`
- **Impact:** The server reads the entire upload into memory before enforcing size and trusts client MIME. PDF and DOCX parsing occurs in-process; a small compressed/complex document can expand or consume disproportionate memory/CPU.
- **Effort:** M
- **Recommendation:** Stream to bounded temporary/object storage while counting bytes, verify signatures rather than MIME alone, enforce PDF page/object and archive expansion limits, and isolate parsing behind timeout/memory/CPU limits. Reject encrypted/malformed documents with a generic error.

#### M-04 — JSON body-size middleware is bypassable and can raise on malformed headers

- **Category:** Security
- **Location:** `backend/main.py:109-126`; `Dockerfile.frontend:62-69`
- **Impact:** The middleware relies only on `Content-Length`, skips every multipart request, does not cap chunked/no-length requests, and parses the header with unguarded `int()`. Direct backend deployments may therefore bypass nginx's controls or cause a 500.
- **Effort:** M
- **Recommendation:** Enforce streaming byte limits in ASGI and configure equivalent ingress limits in every deployment. Handle malformed/duplicate length headers with 400/413 and retain route-specific upload limits.

#### M-05 — Intended global rate limit is not installed

- **Category:** Security
- **Location:** `backend/main.py:91-94`; `backend/app/api/v1/estimates.py:42,294-300`; `Dockerfile.frontend:63-68`
- **Impact:** The app configures SlowAPI default limits but does not add `SlowAPIMiddleware`; only the separately decorated share route is clearly limited. Parser, ML, export, auth-adjacent, and public currency endpoints remain abuse-prone. Proxy IP trust is also not explicitly configured, risking a single shared proxy bucket or spoofed client identity.
- **Effort:** S
- **Recommendation:** Install and test the middleware, use one limiter instance, set tighter per-route limits for expensive operations, and configure trusted proxy headers at the ASGI server/ingress boundary.

#### M-06 — Raw exception details are returned to clients

- **Category:** Security
- **Location:** `backend/app/api/v1/documents.py:61-66,153-157,197-201,286-290`; `backend/app/api/v1/estimates.py:172-174,213-215,235-237,253-255,271-273,289-291,315-317`; `backend/app/api/v1/export.py:80-82,111-113`; `backend/app/core/security.py:127-145`
- **Impact:** Database, parser, provider, and authentication internals can leak through `detail=str(e)`, making reconnaissance easier and exposing operational data.
- **Effort:** S
- **Recommendation:** Map known domain failures to stable public error codes/messages. Log the original exception server-side with request ID and sanitized context; return a generic 500 for unexpected failures.

#### M-07 — Audit logs retain bearer-token fragments and arbitrary query strings

- **Category:** Security
- **Location:** `backend/app/middleware/audit_log.py:35-40,57`
- **Impact:** Logging the last eight token characters creates unnecessary credential material, while raw query parameters may capture sensitive future values. The token suffix is not a reliable user identity despite the middleware's audit purpose.
- **Effort:** S
- **Recommendation:** Populate a verified user ID/role in request context after authentication, log that identifier and route template, remove all token fragments, and redact/allowlist query fields. Define log retention and access controls.

#### M-08 — Share links are created but cannot be opened

- **Category:** Architecture & design
- **Location:** `backend/app/services/estimate_service.py:349-385`; `frontend/src/pages/ResultsPage.tsx:79-84`; `frontend/src/App.tsx:194-217`; `README.md:266`
- **Impact:** The backend creates tokens and the UI copies `/share/{token}`, but there is no frontend route or public backend read endpoint/password verification. Links redirect to the app root and rows accumulate without delivering the feature.
- **Effort:** M
- **Recommendation:** Implement a minimal public, expiry-aware, password-aware read DTO and `/share/:token` page, or remove/disable link creation until complete. Avoid exposing owner/private fields and test expired, revoked, guessed, and password-protected links.

#### M-09 — Health and smoke checks report degraded/crashed deployments as healthy

- **Category:** DevOps / CI-CD / Operations
- **Location:** `backend/app/api/v1/health.py:19-64`; `Dockerfile.backend:54-56`; `docker-compose.yml:26-31`; `.github/workflows/ci.yml:170-179`; `.github/workflows/cd-staging.yml:53-64`; `.github/workflows/cd-production.yml:62-73`
- **Impact:** Dependency/model degradation still returns HTTP 200, so orchestrators and CD accept an unusable/demo instance. The Docker smoke test never checks container state or health after startup and can pass after a crash.
- **Effort:** S
- **Recommendation:** Split `/live` from `/ready`; return 503 readiness when required DB/Firebase/model dependencies fail. In CI wait for Docker health and assert a successful authenticated/minimal API response; fail on container exit.

#### M-10 — Database schema and migration paths have diverged

- **Category:** Architecture & design
- **Location:** `backend/migrations/001_initial_schema.sql`; `backend/alembic/versions/2026_04_001_initial_initial_schema.py`; `supabase/migrations/001_initial_schema.sql`; `backend/alembic/env.py:12-13`
- **Impact:** The Neon SQL baseline and Alembic initial migration substantially agree, but the legacy Supabase lineage differs on identity types, auth foreign keys/RLS, document bytes, and share storage. Role/email are later Alembic additions, so applying only the SQL baseline also omits them. There is no deployment migration step, and migration dependencies are undeclared. Environment setup can produce schemas incompatible with application assumptions.
- **Effort:** L
- **Recommendation:** Select Alembic as the canonical schema history, baseline the live Neon schema, create forward migrations for all required changes, archive the Supabase path, declare tooling dependencies, and run `alembic upgrade head` as a gated release phase with backup/rollback procedures.

#### M-11 — Deployment bypasses CI and is non-reproducible

- **Category:** DevOps / CI-CD / Operations
- **Location:** `.github/workflows/cd-staging.yml:3-32`; `.github/workflows/cd-production.yml:3-48`; `.github/workflows/cd-production.yml:19-31,45,56`
- **Impact:** Pushes/tags deploy without consuming a successful CI artifact or checking CI status. Production manual dispatch usually ignores its requested tag because `github.ref_name` is nonempty, and both Railway/Vercel CLIs are installed from unpinned latest versions. Failing or differently built code can reach production. CI also uses uppercase Docker repository tags (`Predictify-backend:ci` / `Predictify-frontend:ci`, `ci.yml:167-176`), which Docker rejects; lowercase them before relying on the gate.
- **Effort:** M
- **Recommendation:** Trigger CD only from a successful CI workflow, promote immutable tested artifacts by digest, correctly select the dispatch input, pin actions and CLI versions, run migrations, and implement rollback to the prior digest.

#### M-12 — Critical frontend behavior is effectively untested

- **Category:** Testing
- **Location:** `frontend/src/**/__tests__`; `frontend/e2e/smoke.spec.ts:9-51`; `frontend/playwright.config.ts:29-35`; `.github/workflows/ci.yml:38-51,91-109`
- **Impact:** Vitest passed 43 tests, but measured coverage is **8.61% statements / 8.90% lines**. `App.tsx`, all pages, API client, auth store, and estimate store are at 0%. CI runs neither `npm test` nor ESLint; Playwright has six smoke tests, is not run in CI, and starts only the frontend even though tests call port 8000. The broken upload/share/result-error flows escaped detection.
- **Effort:** M
- **Recommendation:** Add CI unit/lint gates and an authenticated Playwright flow covering login, upload, extraction, estimate, results, export, and share. Provision both services and isolated Firebase/DB fixtures. Set an initially realistic coverage floor and ratchet it upward.

#### M-13 — Backend tests mock away the highest-risk integration boundaries

- **Category:** Testing
- **Location:** `backend/tests/test_api_integration.py:76-79,200-207,285-400`; `backend/tests/test_phase3.py:58-145`
- **Impact:** The suite has broad function count but does not exercise upload-file -> object storage -> extract -> estimate against a coherent schema. Storage tests use benign keys, health tests encode “always 200,” and several assertions accept success or multiple error codes, allowing regressions to pass.
- **Effort:** M
- **Recommendation:** Retain fast unit tests but add contract tests with a temporary Postgres/schema, local/S3-compatible storage, real parser fixtures, and strict expected statuses. Add Windows/POSIX traversal cases and remove permissive multi-status assertions unless explicitly parameterized by a documented condition.

#### M-14 — Reported model evaluation and “confidence” are not statistically valid guarantees

- **Category:** Architecture & design
- **Location:** `backend/ml/train.py:151-171,177-216,589-617`; `backend/ml/inference.py:162-223`
- **Impact:** Eight models are ranked using the held-out test set, and the winning model's same scores are then published as final performance. Cross-validation is applied only after ranking. Scaling is performed before CV folds, and the displayed confidence is an arbitrary formula based on R², nonzero inputs, and fixed bonuses; the 0.8/1.4 interval is not calibrated. Users can interpret optimistic selection bias and heuristics as probabilistic certainty.
- **Effort:** L
- **Recommendation:** Use nested CV or train/validation/test splits with an untouched final test set, place preprocessing inside sklearn pipelines, report bootstrap/calibrated prediction intervals, and rename/remove `confidence_pct` until calibration is measured. Version data, code, metrics, and artifacts together.

#### M-15 — Historical training data has no drift or applicability controls

- **Category:** Architecture & design
- **Location:** `backend/ml/train.py:1-13,79-109`; `backend/ml/inference.py:166-169,216-223`
- **Impact:** The 740 projects combine small historical datasets (documented elsewhere as spanning legacy eras), while the product accepts modern technology stacks and costs. Inputs are silently zero-filled/clamped, with no out-of-distribution warning, uncertainty widening, production error measurement, or drift monitoring.
- **Effort:** L
- **Recommendation:** Document the model card and supported domain, collect consented modern outcomes, add feature/range validation and OOD flags, monitor drift and post-project error, and require human review for materially consequential estimates.

#### M-16 — Result UI can misstate risk and hide failures

- **Category:** Code quality & maintainability
- **Location:** `frontend/src/pages/ResultsPage.tsx:90-120`; `frontend/src/store/estimateStore.ts:66-75`; `frontend/src/pages/EstimatesPage.tsx:86-94`; `frontend/src/store/estimateStore.ts:79-89`
- **Impact:** “Low” risk is rendered red while “High” is green. A failed result fetch leaves `currentEstimate` null and renders an endless skeleton instead of the stored error. Delete failures are swallowed by the store, after which the page still announces successful deletion.
- **Effort:** S
- **Recommendation:** Use a centralized semantic risk palette, render explicit retryable error/404 states, and let mutations return/throw typed results so success UI occurs only after confirmed success. Add component tests for each state.

#### M-17 — Duplicate estimate versioning is race-prone

- **Category:** Architecture & design
- **Location:** `backend/app/services/estimate_service.py:296-332`
- **Impact:** `MAX(version)` and `INSERT` are separate operations without a transaction/unique constraint. Concurrent duplicate requests can create the same version or inconsistent lineage.
- **Effort:** M
- **Recommendation:** Add a unique constraint on the lineage key plus version, and allocate/insert inside a transaction with row/advisory locking or retry on conflict.

#### M-18 — Setup, API, and version documentation contradict the running system

- **Category:** Documentation
- **Location:** `README.md:29,53,117,163,197,207,234-268`; `backend/.env.example:20-28`; `frontend/package.json:4`; `backend/app/core/config.py:14,32-49`; `backend/ml/inference.py:57-61`; `run.py:59`; Docker image labels
- **Impact:** The README describes React 18 and Supabase while the code uses React 19, Firebase, and Neon; it advertises nonexistent share-read and CSV endpoints. Storage/S3/pool settings are absent from the environment template, ML path settings are ignored by inference, and version strings span 2.5.0 through 3.2.0. New deployments and incident responders can follow instructions that produce an incompatible or unauthenticated system.
- **Effort:** M
- **Recommendation:** Generate API documentation from the running OpenAPI schema, rewrite setup/deployment instructions around Firebase + Neon + durable storage, remove or implement advertised routes, make inference consume the configured artifact paths, and define one build-sourced application version.

#### M-19 — Admin role updates can leave Firebase and the database inconsistent

- **Category:** Architecture & design
- **Location:** `backend/app/api/v1/admin.py:86-107`; `backend/app/core/security.py:110-119`
- **Impact:** The database role is updated before the external Firebase custom claim, with only an in-request manual rollback. Process/network failures can leave the stores disagreeing, while authorization trusts the Firebase claim and profile/admin displays may trust the database.
- **Effort:** M
- **Recommendation:** Choose and document one authorization source of truth. For dual writes, persist a transactional outbox/job with idempotent retries and reconciliation, expose pending/failed state, and test every partial-failure ordering.

#### M-20 — Backend env points to an absent Firebase Admin credential file

- **Category:** DevOps / CI-CD / Operations
- **Location:** `backend/.env` (`FIREBASE_CREDENTIALS_PATH`); `backend/app/core/security.py:30-69`; `backend/main.py:51-55`
- **Impact:** The configured file does not exist when resolved from the documented backend working directory. There is no raw-JSON override in the env file or current process. Once dependencies are available, `init_firebase()` will raise before DB/model initialization. This is a local setup blocker, not proof of missing credentials on the deployed service.
- **Effort:** S
- **Recommendation:** Supply the matching service-account JSON at the configured path or securely inject `FIREBASE_CREDENTIALS_JSON`. Keep it out of Git/Docker layers, validate frontend/backend project alignment, and then run an authenticated integration check.

#### M-21 — JSON export does not encode PostgreSQL UUID objects

- **Category:** Code quality & maintainability
- **Location:** `backend/app/api/v1/export.py:85-113`; `backend/migrations/001_initial_schema.sql` UUID columns
- **Impact:** The route constructs `JSONResponse` directly after converting only values with `isoformat()` and excluding bytes. asyncpg returns UUID objects, which have no `isoformat()` and are unsupported by the standard JSON encoder. Normal estimate rows therefore fail serialization. This is a source/type-contract finding; no live database reproduction was performed.
- **Effort:** S
- **Recommendation:** Use FastAPI's `jsonable_encoder` or an explicit export model handling UUID/datetime/Decimal values. Test the endpoint with actual UUID objects rather than string-only mocks.

### Low

#### L-01 — Synchronous parser, PDF, and object reads block async workers

- **Category:** Performance
- **Location:** `backend/app/api/v1/export.py:65`; `backend/app/services/document_parser.py:56-145`; `backend/app/services/storage_service.py:150-159`; `backend/ml/inference.py:142-186`
- **Impact:** CPU-heavy PDF/DOCX parsing, PDF rendering, model inference, and S3 body reads execute from async request paths. Under concurrent workloads they block event-loop workers and increase tail latency.
- **Effort:** M
- **Recommendation:** Offload bounded synchronous work to a worker/thread pool or task queue, stream S3 reads safely, apply concurrency limits/timeouts, and benchmark representative concurrent uploads/exports before choosing worker counts.

#### L-02 — Several API models accept unbounded or semantically invalid values

- **Category:** Code quality & maintainability
- **Location:** `backend/app/api/v1/profile.py:25-31`; `backend/app/models/estimate.py:11-20,29-38`; `backend/app/models/document.py:9-14`; `backend/app/api/v1/documents.py:18-38`
- **Impact:** Profile fields, technology arrays, project types, and legacy document metadata lack length/enumeration/URL/timezone constraints. This permits junk or oversized data and leaves a metadata route able to claim arbitrary storage paths.
- **Effort:** S
- **Recommendation:** Add Pydantic bounds, enums/Literals, strict URL/timezone validation, collection limits, finite-number checks, and server-owned storage metadata. Remove the legacy metadata-only upload route if unused.

#### L-03 — Browser/security and CI supply-chain hardening is incomplete

- **Category:** Security
- **Location:** `backend/main.py:129-139`; `Dockerfile.frontend:76-80`; `.github/workflows/*.yml`
- **Impact:** CSP and HSTS are absent, nginx/backend frame policies disagree, obsolete `X-XSS-Protection` remains, and GitHub Actions are pinned only to mutable major tags. These are defense-in-depth gaps rather than demonstrated exploits.
- **Effort:** S
- **Recommendation:** Define CSP/HSTS at the public ingress after compatibility testing, use one frame policy, remove the obsolete header, and pin third-party actions by reviewed commit SHA with automated update tooling.

#### L-04 — Declared MIT licensing is incomplete and dependency licenses are not checked

- **Category:** Dependencies & supply chain
- **Location:** `README.md`; repository root; `.github/workflows/`
- **Impact:** The README declares MIT but no `LICENSE` file was found, leaving distribution terms ambiguous. There is no automated dependency-license policy check, so incompatible additions may go unnoticed.
- **Effort:** S
- **Recommendation:** Confirm ownership and intended terms, add the canonical MIT license text and copyright holder/year, then add a lightweight license inventory/policy check for both ecosystems.

#### L-05 — Firebase test helper is coupled to a live project and fixed credentials

- **Category:** Security
- **Location:** `backend/scripts/test_firebase.py:5-31`
- **Impact:** The helper embeds a Firebase web API key/project coupling and creates a fixed email/password account. Firebase web keys are normally public identifiers rather than server secrets, but an interrupted cleanup can leave a predictable test principal in the configured project.
- **Effort:** S
- **Recommendation:** Require an explicitly selected emulator/test project, generate random per-run identity and password values, guarantee cleanup in `finally`, and block execution against production project IDs.

### Informational

#### I-01 — Positive engineering controls already present

- **Category:** Informational
- **Location:** `backend/app/core/security.py`; `backend/app/core/database.py`; `backend/main.py`; `frontend/src/lib/api.ts`; `backend/tests/`; `frontend/src/**/*.test.tsx`
- **Impact:** No action required. The codebase already uses server-side Firebase token verification, parameterized asyncpg calls, ownership filters on major resources, CORS allowlisting, request IDs, type checking, structured modules, and a substantial backend unit-test base. No clear SQL injection, shell execution, template injection, or stored React `dangerouslySetInnerHTML` path was found in reviewed application code.
- **Effort:** —
- **Recommendation:** Preserve these controls while fixing the integration and operational gaps above.

#### I-02 — Audit limitations

- **Category:** Informational
- **Location:** Repository/environment-wide
- **Impact:** The required code-review-graph MCP tools were not exposed in this session, so targeted filesystem inspection was used after confirming their absence. The workspace contained no usable `.git` repository, preventing history/branch analysis. Python 3.9 was inaccessible in the sandbox but ran after approval; it is insufficient for the declared Python 3.13 environment. Backend tests were not run and the referenced Firebase Admin file is absent. Frontend initialization/install/build/lint/coverage checks were rerun; sandbox test-worker timeouts cleared on the approved retry. No live cloud credentials, Firebase project, Neon database, Railway, Vercel, or S3 service was probed.
- **Effort:** —
- **Recommendation:** Re-run history secret scanning and the full backend suite in CI/a normal Python environment, and validate provider configuration separately before launch.

## Category Deep-Dives

### 1. Security

The urgent risks are the embedded database credential (C-01) and Windows path traversal (H-01). Authentication exists and most data access is owner-filtered, but revocation is not actually checked (M-01), viewer authorization is inconsistent (M-02), upload/parser resource controls are weak (M-03/M-04), intended global rate limiting is inactive (M-05), raw failures leak detail (M-06), and audit logs retain token/query material (M-07). Current dependencies add remotely relevant multipart and websocket exposure (H-05/H-06). No significant direct SQL injection, command injection, template injection, or React raw-HTML sink was found in the reviewed paths.

### 2. Code quality & maintainability

The immediate quality blocker is the failing TypeScript production build (H-04). Result-state and mutation error contracts are inconsistent and produce misleading UI (M-16); request models also duplicate or weaken validation compared with domain models (L-02). Broad exception-to-HTTP conversion is duplicated across routers and should be centralized. Naming/version drift (`PredictIQ`, `Predictify`, mixed artifact casing, and versions 2.5/3.0/3.1/3.2) increases operational ambiguity.

### 3. Architecture & design

The most serious design break is two competing document persistence models (H-02). Share-link write and read halves are disconnected (M-08), three migration histories disagree (M-10), duplicate version allocation is non-atomic (M-17), and production inference can silently turn into a demo (H-10). ML evaluation/calibration and domain applicability need explicit product constraints (M-14/M-15). Otherwise the router/service/core separation is understandable and there was no obvious circular-import hotspot in the inspected application modules.

### 4. Testing

Backend test quantity is encouraging, but integration realism is weak at storage/database/auth boundaries (M-13). Frontend coverage is 8.61% statements, core stores/pages are untested, Playwright is not self-contained or run in CI, and the current production build fails (H-04/M-12). Missing tests map directly to escaped product defects: traversal, disconnected document bytes, missing share route, result errors, risk colors, degraded readiness, and fail-open security gates.

### 5. Performance

The primary concerns are unbounded in-process document parsing (M-03), inactive rate limiting (M-05), and synchronous parser/render/model/object operations in async paths (L-01). No clear database N+1 loop was found in the reviewed endpoints. Admin list operations are unpaginated and should be paginated before user volume grows.

### 6. Dependencies & supply chain

The Python lock is both broken and incomplete (H-03), and both ecosystems contain known high/critical advisories (H-05/H-06). The frontend lockfile is present and `npm ci` succeeded, which is positive. However Python's broad minimum manifest plus ad-hoc freeze is not a safe lock strategy, security gates fail open (H-09), GitHub Actions/CLIs are not immutably pinned (M-11/L-03), and unused packages have not been pruned.

The README declares MIT, but no `LICENSE` file was found and CI performs no license-policy scan. Add the intended license text after ownership confirmation and automate dependency license review; treat this as a release/legal housekeeping item rather than a vulnerability.

### 7. DevOps / CI-CD / Operations

Clean backend installation, frontend compilation, clean-CI Firebase configuration, and upload durability remain release concerns (H-03/H-04/H-07/H-08). Local Firebase client initialization now passes; local backend credentials still reference a missing file (M-20). Docker secret isolation is newly relevant (H-11). Security checks cannot enforce policy (H-09), health and smoke tests accept unusable deployments (M-09), schema migrations are not part of release (M-10), and CD can deploy untested, non-reproducibly built code (M-11). Logging exists, but no concrete metrics, alert thresholds, tracing, backup-restore drill, dead-letter strategy, or rollback automation was found.

### 8. Documentation

`README.md` still describes React 18 and Supabase while the application uses React 19, Firebase, and Neon; it documents a nonexistent shared-estimate endpoint and CSV export. Version strings differ across the frontend package, backend config/example, Docker labels, startup banner, and historical audit. `backend/.env.example` omits storage, S3, and pool settings and advertises ML paths that inference ignores. Rewrite setup/deployment/API documentation from executable configuration, add an architecture decision record for Firebase/Neon/storage, a model card, incident/rollback/restore runbooks, and an actual license file.

## Prioritized Action Plan

1. **Contain the credential incident:** rotate the Neon secret, remove it from code, inspect access logs and Git history, then add a blocking secret scanner.
2. **Stop unsafe uploads:** disable upload/extract routes temporarily if exposed; patch key generation/containment, apply editor RBAC, and add traversal/resource-limit tests.
3. **Repair the core data contract:** make object storage the single source for document bytes, migrate/remove `file_data`, fail closed on parse/object errors, and prove the complete upload-to-estimate flow.
4. **Restore deterministic builds:** fix the test tsconfig, declare all Python dependencies, regenerate the lock, and verify clean Docker builds and startup.
5. **Patch dependencies:** upgrade the confirmed npm/Python vulnerable chains and retain regression evidence for any accepted advisory.
6. **Make safety checks real:** fail CI on security policy violations, run frontend lint/unit tests and self-contained e2e, enforce readiness, and correct Docker smoke checks.
7. **Harden production configuration:** exclude Docker secrets, supply local Firebase Admin credentials for verification, require durable object storage and live ML artifacts, supply Firebase build configuration, separate liveness/readiness, and remove production demo fallback.
8. **Unify schema/release management:** baseline Alembic, add migrations to CD, gate deployment on successful CI, and promote immutable artifacts with rollback.
9. **Complete or remove unfinished features:** implement secure share reads, then fix result-state/risk display and atomic estimate versioning.
10. **Establish ML governance:** create a model card, unbiased evaluation, calibrated intervals, OOD handling, drift/error monitoring, and a data refresh plan.
11. **Refresh operational documentation:** rewrite README/env/API/version/license/runbooks and add backup-restore and incident procedures.

## Quick Wins

Each of these should be achievable in under an hour independently:

- Rotate the exposed database password and delete the source fallback.
- Reject all path separators/`..` and use UUID-only object keys; add a resolved-path containment assertion.
- Add `vitest/globals` or split the production/test TypeScript configs.
- Add editor-role dependencies to file upload and extraction routes.
- Change Firebase verification to check revocation on sensitive routes.
- Remove `detail=str(e)` from public 500 responses.
- Remove bearer-token suffixes and raw query strings from audit logs.
- Remove `|| true` and the broad `except` from security workflows.
- Make readiness return 503 for unavailable DB/Firebase/model dependencies.
- Correct Low/High risk colors and render stored result-load errors.
- Disable share-link creation until the read route/page exists.
- Provision Firebase client values in clean CI/CD builds; local env loading is verified.
- Exclude backend env/service-account files from Docker layers.
- Supply the missing Firebase Admin credential file locally.
- Encode UUIDs correctly in JSON export.
- Remove the duplicate `limits` pin and add the missing direct dependencies before regenerating the lock.
- Add `npm test` and `npm run lint` to CI.
- Add a real `LICENSE` file if MIT is the confirmed intended license.

## Verification Performed

- `npm ci --ignore-scripts`: succeeded (384 packages installed).
- `npm run build`: failed on missing Vitest global types in `ErrorBoundary.test.tsx`.
- `npm run lint`: failed with 2 errors and 20 warnings; the errors were in `frontend/src/store/authStore.ts:231,234` (`preserve-caught-error`).
- Re-audit `npm run test:coverage`: sandbox fork workers timed out before tests; approved retry passed 5 files / 43 tests, 8.61% statements, 8.06% branches, 7.91% functions, 8.90% lines. The initial 0% timeout report is not a valid coverage measurement.
- Playwright: six existing smoke tests re-inspected; configuration starts only frontend. Full browser/authenticated e2e was not rerun.
- `npm audit --package-lock-only --omit=dev --json`: 1 critical, 6 high, 2 moderate production vulnerabilities at audit time.
- OSV batch lookup of pinned Python packages: multiple current high-severity results, summarized in H-06.
- Backend static inventory: 316 `test_*` functions across 19 test files.
- Backend execution: not run; only Python 3.9 installed (confirmed outside sandbox), project targets 3.13, lock conflicts persist, and Firebase Admin file is absent.
- Vite production env load plus Firebase `initializeApp`/`getAuth`: passed with all six keys populated; no network sign-in.
- Read-only Windows path resolution: generated-style backslash traversal escapes upload base; no file written outside workspace.
- Secret equality: migration URL matches backend env URL; neither value emitted.
- OSV recheck: 12 pinned package names matched advisories; npm production recheck confirmed 9 vulnerable-package entries (1 critical / 6 high / 2 moderate).
- Docker build and live authenticated end-to-end checks were not performed.
