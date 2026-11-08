> [!WARNING]
> **Historical - superseded; do not use as guidance.** This document reflects an earlier development phase and is preserved solely for auditability.

Status: Historical | Applies to: Historical (superseded) | Verified against commit: cdca041 | Date: 2026-11-08

# Engineering repair progress — 2026-09-08

All changes are local. Nothing was pushed or deployed. This workspace has no usable Git metadata, so history, branches, and tracked-secret status cannot be verified. Graph tools were unavailable; targeted implementation inspection was used. The structure map is `docs/PROJECT_STRUCTURE_MAP.md`.

## Implemented and verified

- Removed the embedded database connection fallback. Migration credentials must be explicitly supplied. Docker contexts exclude environment files, service accounts, private keys, development tooling, caches, and uploads. Credential rotation remains an external requirement.
- Storage keys no longer incorporate filenames or raw user identifiers. Portable key validation and resolved-path containment protect local reads, writes, deletes, and existence checks. Object reads and upload bodies are bounded.
- Upload, extraction, and analysis use the same owned object-storage reference. Missing, invalid, foreign, empty, or failed objects cannot produce an estimate. Metadata-only upload is retired with HTTP 410. Upload/extraction require editor access. Database insertion failures clean up uploaded objects.
- Document analysis uses extracted values when overrides are absent, preserves explicit empty technology lists and zero integration counts, and accepts the wizard's integration/volatility/experience corrections. The wizard no longer reports extraction failure as success.
- PDF/DOCX signatures and archive expansion limits are checked. PDF size/page limits reject oversized documents. Parsing is offloaded from the event loop. Hard per-process CPU/memory isolation remains pending.
- Firebase verification checks revocation, rejects disabled users, and logs verified identity rather than bearer fragments. Audit logs omit query strings and use route templates. Request-byte limits handle missing/invalid/dishonest length headers, and the shared global rate limiter is actually installed.
- Inference fails closed on missing/incompatible artifacts, feature count/order mismatch, missing/nonfinite inputs, invalid preprocessing, and invalid predictions. Readiness returns 503 when dependencies are unavailable; liveness is separate. Configured model paths are honored.
- Corrected the Adjustment feature's units using the dataset's observed function-point relationship. Feature derivations and log-target transform were checked against the dataset. Confidence/intervals are explicitly heuristic, not calibrated probabilities. See `backend/ml/README.md` for evidence and remaining applicability limitations.
- JSON export supports PostgreSQL UUID/datetime/Decimal values. PDF rendering escapes customer text rather than interpreting it as markup. Model version is persisted consistently with the returned estimate.
- Forward Alembic migration `003_estimate_lineage` adds stable lineage and uniqueness. Concurrent duplicate requests allocate versions under a transaction/advisory lock. Historical rows get separate lineages because their ancestry cannot be safely inferred from names.
- Share reads support expiry and passwords with a restricted public DTO. Shared pages do not require login. Deleted estimates cannot be retrieved/exported/shared. Share passwords are bounded for bcrypt; request bodies carry passwords, not query strings.
- Frontend build/test TypeScript contexts are separated. Result fetch errors can be retried, stale results are cleared, failed deletes remain visible, and risk colors reflect severity. Tailwind processing is installed in Vite.
- Backend dependencies are resolver-generated with hashes for Python 3.13, retaining scikit-learn 1.8.0 required by the actual artifacts. Missing runtime/migration dependencies are declared. Frontend lock updated compatibly. Both audits reported no known vulnerabilities after remediation.
- CI checks now include frontend lint/tests/audit, backend dependency audit, disposable PostgreSQL migrations/integration, and real security failure exits. Staging requires successful CI; production checks the selected commit's CI status. Docker tags and the formerly misleading smoke test are corrected. Public Firebase build configuration is required explicitly.
- Single-host Compose persists uploads in a named volume and explicitly opts into durable local storage. Other production/staging configurations require S3 by default.

## Validation evidence

- Backend full suite (2026-09-09): **466 passed**, **83% app coverage**, including the isolated PostgreSQL integration tests.
- Real isolated PostgreSQL 18: canonical migrations applied through `003_estimate_lineage`; document upload → parser → NLP → real model → persisted estimate → retrieval/export passed. Concurrent versions across renamed ancestors passed, including uniqueness constraints and cross-user rejection.
- Backend mypy: no issues in 40 source files. Ruff and high-severity Bandit pass after the continued repairs. All five workflow YAML files parse successfully.
- Security gate regression: all four checks passed, including a real seeded Bandit high finding that exits nonzero.
- Frontend: **57 tests passed in eight files**; production/test type checks and production build passed. ESLint has zero errors and 20 existing warnings. The restricted runner timed out starting two workers; a fresh unrestricted run passed all files with no unhandled errors.
- Playwright: **8 browser checks passed**, covering landing/auth pages, public share errors/password prompts, security headers, and readiness. These do not substitute for authenticated Firebase wizard E2E.
- Real frontend Docker image build passed. **3 Nginx container checks passed**: HTML/static/error headers and caching, share redirect log privacy, and a 10 MiB body reaching the local upstream with bodies above 11 MiB rejected. The test container was removed automatically.
- Backend Docker image build passed after retrying a package-download DNS failure. Application imports, packaged model loading, and an actual positive-effort prediction passed inside the non-root runtime image with `--network none`, dummy test configuration, and no application `.env` file. Runtime cloud readiness was not claimed by this isolated smoke check.
- No production credentials, live Firebase login, external database, or deployment was used for testing.

## Remaining release work

1. Rotate the exposed database credential and inspect provider access logs and any historical Git/image copies. No claim is made that it was revoked or never exposed.
2. Supply the missing Firebase Admin service account securely and verify a real authenticated staging flow. Configure the six public `VITE_FIREBASE_*` repository/environment variables and durable storage.
3. Expand authenticated wizard E2E using an isolated Firebase emulator/test project. Public browser checks and the frontend unit suite are passing.
4. Establish artifact provenance/signatures and an unbiased training evaluation with calibrated uncertainty; resolve zero-imputation/domain applicability and collect modern outcomes. No model was retrained during these repairs.
5. Add durable reconciliation for Firebase/database role dual writes, stronger parser process resource isolation, immutable release artifact promotion, migration release/rollback procedures, backup/restore verification, and provider-side security controls.
6. Confirm license ownership/terms before adding a license. Review remaining documentation and lower-priority audit items rather than assuming the entire audit is closed.

Local PostgreSQL testing uses a separate cluster under `.tools/postgres-test`, bound only to `127.0.0.1:15439`. It does not reuse the configured application database.

## Continued repairs — 2026-09-09

- Persist feature count, integration count, volatility, team experience, and calculated function points in estimate inputs. Real PostgreSQL regression checks verify retrieval, duplication, and public sharing retain them. The results page displays them; historical values remain unknown rather than being invented.
- Validate estimate UUIDs before database access across read/delete/duplicate/share/export routes. Manual and document override strings/lists now have matching bounds and reject blank names/technology entries.
- Profile endpoints now use the existing shared validation model instead of an unbounded duplicate. Rates, names, theme, currency format, avatar HTTP(S) scheme, and timezone length are checked. The currency schema permits the broader three-letter choices supported by the application.
- Apply `no-referrer` consistently and `no-store` to share error responses as well as successful reads. Fixed ambiguous browser test locators by scoping alerts to the main page.
- Replaced the frontend Dockerfile's divergent inline Nginx configuration with the checked-in configuration, preserving the 11 MiB multipart envelope budget. Nginx cache headers now share server scope with security headers, and the global access-log format omits URLs/query strings/referrers even after SPA internal redirects. The builder uses Node 22. Generated test/audit artifacts are excluded from image contexts.
- Added opt-in real-container regression coverage and wired it into the existing CI Docker job. Its upstream is a local stub; image builds use test-only public Firebase values during local verification.
- PDF generation and share-password hashing now run in the thread pool. Regression tests assert they execute outside the request event-loop thread; the full backend suite passed afterward.

Nginx configuration rationale is checked against its official [header inheritance](https://nginx.org/en/docs/http/ngx_http_headers_module.html) and [request logging](https://nginx.org/en/docs/http/ngx_http_log_module.html) documentation.

## Data integrity and UI milestone — 2026-09-09 (supersedes ML readiness above)

- Confirmed 481 Resource-to-effort column mapping errors in the 740-row merged CSV.
  Reconstructed 787 source project records and trained five fixed candidates with
  training-only source-held-out selection and separate calibration/test partitions.
- Selected Huber power law: held-out MAE 1740 hours versus median baseline 2076;
  median percentage error 51.29%. This is a research candidate, not a validated
  production improvement. See `ml_rebuild_2026-09-09.md` for artifacts and sources.
- Revoked the exact bad model and prevented the corrupted CSV from entering legacy
  retraining or historical benchmarks. Predictions/readiness are unavailable until
  a validated compatible replacement is installed. Existing artifacts preserved.
  Earlier successful runtime/container checks do not establish model quality;
  images built before this correction are stale and must not be promoted.
- Applied ui-ux-pro-max guidance to responsive shared navigation, consistent theme
  preferences, keyboard/account controls, authentication labels, dashboard mobile
  layout, risk colors and accessible estimate links. Scope and visual decisions
  are documented in `ui_ux_improvements_2026-09-09.md`.
- Validation: 475 backend tests passed including isolated PostgreSQL, 60 frontend
  tests passed in the full run plus 2 new theme tests passed in focused coverage.
  Backend CI lint and frontend type checks passed; frontend lint has the existing
  20 warnings and no errors. Browser/build verification is recorded below.
- No push, deployment, paid data purchase, external account change or credential
  rotation. Graph tooling was unavailable; this workspace has no .git metadata.

### Latest verification and authorization follow-up

- Full backend suite: **477 passed**, including isolated PostgreSQL integration.
- Full frontend suite: **67 passed** with unrestricted thread workers. A restricted
  fork-worker run failed collection because its temporary cache file disappeared;
  the unrestricted rerun passed without weakening tests.
- Chromium smoke suite: **9 passed**; expanded workspace check also passed after
  adding wizard/settings/results mobile coverage and correcting chart controls.
- Backend CI lint and mypy (40 application files) passed. Frontend build and type
  checks passed; existing ESLint warnings remain.
- Admin role updates now preserve unrelated Firebase custom claims and offload the
  blocking SDK calls to a thread. Regression tests cover preservation and provider
  read failure. This is **not** closure of M-19: durable reconciliation and partial
  failure handling still need work. Firebase documents claims replacement behavior
  at https://firebase.google.com/docs/auth/admin/custom-claims.
- Overall completion percentage is **unverified**, not 80% or 100%. The six remaining
  workstreams are model/data validation and serving; further UI quality; authenticated
  E2E; authorization/document-processing reliability; release/backup/restore checks;
  and user-owned credential/provider configuration. Tests passing is not a project
  completion percentage. Existing historical estimates need revalidation against a
  trustworthy replacement model before being used for commercial quoting.
