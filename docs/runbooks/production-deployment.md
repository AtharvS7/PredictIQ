# Production deployment runbook

Updated September 26, 2026. Source branch: **dev2 only**. Do not push main, another branch, or a tag. The earlier Railway/tag workflow is obsolete. Approved targets are the existing Vercel preview project and Render's My Workspace, within the ₹0 budget. Deployment is currently deferred while model acceptance remains open.

## Required release evidence

1. Verify the exact dev2 commit with backend tests, frontend type/lint/tests/build, browser acceptance, authenticated E2E, dependency checks and CI.
2. Independently approve a production model bundle. Research test gains are insufficient: verify absolute errors, planning-time feature parity, provenance, uncertainty and intended applicability. Keep the revoked model rejected.
3. Populate ignored production environment configuration with the approved manifest path/hash and provider values. Run `python scripts/production_preflight.py` with those values in the process environment; the command deliberately does not load a development `.env`. Never print secrets or commit environment files.
4. Verify actual Firebase, Neon and durable S3 connectivity separately. Neon is already migrated through `005_role_retry`; do not reapply historical SQL or alter migration history.
5. Back up the database and objects and verify restoration to isolated destinations before a production change. The local rehearsal below verifies mechanics only; it is not evidence of production backup coverage.
6. Deploy the reviewed commit to the approved backend, connect the frontend HTTPS API URL, and configure exact CORS origins. Confirm `/api/v1/live` and `/api/v1/ready`; degraded or fixture-backed behavior is not production acceptance.
7. Exercise real sign-in, document upload, extraction, estimation, persistence, export/share, sign-out and cross-user denial. Verify private object access and persistence across restart.
8. Verify resource limits, monitoring and alert delivery, retention, load behavior and rollback. Record commit, model-manifest hash, provider deployment IDs and recovery evidence before declaring completion.

## Local verification

Use only the isolated PostgreSQL integration endpoint, `127.0.0.1:15439/predictiq_integration`, through `PREDICTIQ_TEST_DATABASE_URL`. The authenticated test server rejects another endpoint. Apply canonical migrations to that disposable database first.

From frontend, run normal browser acceptance with `npx playwright test`. Run authentication with the Firebase Auth emulator: `firebase emulators:exec --only auth --project demo-predictiq --config firebase.test.json "npx playwright test --config playwright.auth.config.ts"`. The CI workflow installs Firebase CLI 15.29.0 and uses a disposable PostgreSQL service. These tests deliberately use a deterministic model fixture and do not measure prediction accuracy.

From the repository root, run `backend/.venv/Scripts/python.exe scripts/rehearse_recovery.py --output .tools/recovery-UNIQUE` with the same isolated database environment variable. The tool creates two new uniquely named databases, applies migrations, inserts synthetic related records, dumps/restores the database and document bytes, and compares all four application tables and object contents. It leaves databases and evidence for inspection, does not modify the existing integration database, and does not connect to production. PostgreSQL binaries can be selected with `--pg-bin`.

## Rollback

Retain the last accepted deployment and matching model/configuration references before replacement. Roll back application and frontend deployments through their approved provider projects; verify readiness, authentication and persisted data afterward. Additive database migrations should not be automatically reversed. Restore data only into an isolated destination first and compare it before any destructive production recovery.

The September 27 live Neon snapshot restored successfully to a local isolated database, and the live S3 probe passed. The owner confirmed 20 old test upload objects are absent; this exception does not permit ignoring any new missing documents. Cloud failover and approved-model hosted estimation remain open gates. See [release checklist](../RELEASE_CHECKLIST.md) for current evidence.

## Live-provider recovery and operations

Run `python scripts/rehearse_live_recovery.py --config backend/.env.production --output .tools/recovery-UNIQUE` with the isolated local database environment variable and PostgreSQL binaries available. It uses a read-only exported Neon snapshot, verifies TLS certificates, restores into a fresh local database and compares UTC-normalized table checksums. Referenced objects are backed up and restored to unique S3 rehearsal keys before only those new keys are removed. Private dumps and manifests are constrained to `.tools`.

A missing object normally fails the run. Only use `--known-missing-file` with an explicitly reviewed JSON list of legacy document IDs; the September 27 list records the owner's confirmed old test data. `passed_with_legacy_gaps` means those originals were not recovered, and must never be reported as complete object recovery. Retain the result and private manifests outside Git.

After deployment, run `python scripts/check_operations.py --base-url https://BACKEND_HOST --requests 20 --concurrency 2`. Set the repository Actions variable `PREDICTIQ_API_BASE_URL` to the approved backend URL before enabling the operations workflow. It checks health semantics and p95 latency and exits nonzero on failure. No active scheduling or alert delivery is claimed until a real hosted run and a deliberate failure notification have been verified. For a free sleeping backend, record cold-start behavior separately; never hide failed readiness or use synthetic prediction fixtures to pass a production gate.
