# Release checklist — PredictIQ

Updated September 26, 2026. This replaces the obsolete dev/main/tag release instructions. Authorized backups go only to `dev2`. Budget remains ₹0. Deployment was deferred while ML quality is unresolved; do not promote research artifacts to bypass readiness.

| Gate | Current evidence | Remaining work |
|---|---|---|
| Source and hosting | dev2 backups; approved Render workspace and Vercel preview project | Deploy the reviewed backend only after model acceptance |
| Credentials/configuration | Credentials supplied; storage round-trip previously passed; Neon access verified | Re-run offline preflight and live connectivity for the release configuration |
| Database migration | Neon migrated through `005_role_retry`; original-record checksums preserved | No further schema change currently required |
| Backend correctness | September 26: 552 broad-suite tests passed; all six focused database tests passed afterward | Exact release-commit CI |
| UI/build | Type checking/build passed; 67 frontend tests passed serially; nine browser tests and three fresh-container checks passed; lint has 19 warnings, no errors | Lint-warning cleanup |
| Authentication | September 27 emulator E2E passed sign-in, estimation, persistence and cross-user denial | Repeat with live providers and an approved model |
| Recovery | New populated local rehearsal passed at 005 with table/object checksums | Live Neon/S3 recovery rehearsal |
| ML | Training authorized; larger datasets and candidates evaluated; research Ridge improves median-baseline MAE by 7.1% | Adequate absolute accuracy, planning-time parity and independent production acceptance remain open |
| Security/load | Authorization/parser/storage regression checks pass; Python production audit and frontend full dependency audit found no known vulnerabilities | Exact-commit CI, hosted limits and monitoring verification |
| Release | No accepted production ML bundle; UI preview exists | Live readiness, full authenticated estimation, restart persistence and rollback acceptance |

Completion of local contract tests does not establish model accuracy or live production readiness. See [ML evidence](runbooks/PRODUCTION_ML.md), [deployment runbook](runbooks/production-deployment.md), and [walkthrough](walkthrough.md).
