# Authentication and model validation — September 15, 2026

## Dataset and model evidence

The research collection is now **891 project records**, up from 787 reconstructed records and 740 legacy records. The 104 added AT&T records come from the authors' [JSE data archive](https://jse.amstat.org/datasets/aptness.dat.txt), with [column definitions](https://jse.amstat.org/datasets/aptness.txt) and [source paper](https://jse.amstat.org/v15n2/datasets.matson.html). These are real completed projects from 1986–1991, not modern or real-time projects. No size/effort pairs overlapped the earlier collection. Size/effort matching is conservative overlap screening, not proof of universal project identity.

AT&T provides four potential input parameters: adjusted function points (`size_fp`), operating system, database system, and language. Actual `effort_hours` is the target. The current cross-source candidates use only `size_fp`; the three categorical fields are missing from earlier reconstructed sources and are not invented or silently supplied with defaults. Provenance and evaluation-partition fields are not predictors.

`ml.tune_research` evaluated 13 parameter configurations using source-held-out folds within the original training partition. Huber epsilon 2.0 won that selection. Its previously observed test-set MAE was 1732.12 hours; this diagnostic result is not new independent evidence.

Frozen baseline and tuned models were then evaluated on the 104 newly acquired AT&T records:

| Metric | Baseline | Tuned |
|---|---:|---:|
| MAE, hours | 6484.92 | 6536.23 |
| Median absolute percentage error | 58.85% | 59.57% |
| Predictions within 25% of actual effort | 22.12% | 21.15% |
| R² | 0.139 | 0.126 |

Tuning did not improve external accuracy. **Neither model is approved for production.** The evaluation source is now observed and must not be reused as an untouched test after tuning. No live cost-accuracy claim is supported: effort multiplied by a supplied hourly rate is a calculated cost, not independently validated actual project cost.

Data rights, source measurement compatibility, modern prospective observations, richer consistently available features, and useful uncertainty bounds remain unresolved. Do not merge task/story observations into project totals or generate synthetic rows to advertise a larger real-project dataset. Source data and experiment artifacts remain excluded from Git and Docker.

Reproduce from `backend` after obtaining the source files described in [ML rebuild](ml_rebuild_2026-09-09.md):

```powershell
.venv/Scripts/python.exe -m ml.tune_research
# Save the JSE data file to ml/data/research/aptness.dat.txt
.venv/Scripts/python.exe -m ml.external_validation
```

The scripts write isolated `ml/experiments/tuned-v1` and `expanded-v2` outputs. The latter includes source and artifact SHA-256 hashes and preserves the external evaluation partition. It does not overwrite serving artifacts.

## Authentication verification

The local Firebase Admin file parses successfully, matches the frontend project, and successfully exchanges credentials with Google. No secret values were printed. This verifies credential validity, not a complete live-user workflow.

A dedicated browser harness uses the Firebase Auth Emulator, actual client SDK sign-in, and actual Admin SDK verification through the application's `get_current_user` and `require_role` dependencies. The test verifies identity, rejects invalid tokens, and denies editor access to an admin route. The harness does not use the production database or prediction model. Profile/dashboard persistence and live OAuth remain outside this test's scope.

Use an installed Firebase CLI from `frontend` to run the emulator and test together; `emulators:exec` waits for readiness before launching Playwright:

```powershell
firebase emulators:exec --only auth --project demo-predictiq --config firebase.test.json "node node_modules/@playwright/test/cli.js test --config playwright.auth.config.ts --reporter=line"
```

The frontend emulator switch works only in development builds and requires project `demo-predictiq`. Backend application configuration rejects `FIREBASE_AUTH_EMULATOR_HOST` outside isolated test/CI environments. Never launch the test-only API harness as the application server.

## Remaining acceptance gates

Verification completed: 488 of 490 backend tests passed on the broad run; two PostgreSQL tests failed because the isolated database server was stopped. After starting that cluster, all three lineage/persistence tests passed on targeted rerun. The extended emulator browser test passed including reload persistence, sign-out and protected-route redirect. TypeScript, production build and focused Ruff passed. Backup scans found no local secret matches or tracked environment files; the only pattern warning was the disposable emulator account's explicit test password.

Production model accuracy and compatibility remain blocked by evidence above. Authenticated document-to-persisted-result E2E, live provider authorization consistency, parser process isolation, production recovery, and full accessibility acceptance remain open. Passing this bounded authentication test does not close all of those gates. A whole-project completion percentage is still not measured.
