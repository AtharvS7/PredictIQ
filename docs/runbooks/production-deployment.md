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

The live Neon/S3 recovery rehearsal and approved-model hosted estimation remain open gates. See [release checklist](../RELEASE_CHECKLIST.md) for current evidence.
