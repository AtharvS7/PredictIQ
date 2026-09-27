# Release checklist — PredictIQ

Updated September 27, 2026. This replaces the obsolete dev/main/tag release instructions. Authorized backups go only to `dev2`. Budget remains ₹0. A free Render staging backend is live; production promotion remains deferred while ML quality is unresolved; do not promote research artifacts to bypass readiness.

| Gate | Current evidence | Remaining work |
|---|---|---|
| Source and hosting | dev2 backups; free Render staging live at commit `2759161`; separate Vercel UI preview | Connect the final frontend and promote only after model acceptance |
| Credentials/configuration | Credentials supplied; storage round-trip previously passed; Neon access verified | Re-run offline preflight and live connectivity for the release configuration |
| Database migration | Neon migrated through `005_role_retry`; original-record checksums preserved | No further schema change currently required |
| Backend correctness | September 26: 552 broad-suite tests passed; all six focused database tests passed afterward | CI passed at `2759161`; rerun for the eventual release commit |
| UI/build | Type checking/build passed; 67 frontend tests passed serially; nine browser tests and three fresh-container checks passed; lint now has zero warnings/errors; pagination and retry fixes tested | CI passed at `2759161`, including browser and authenticated contract tests |
| Authentication | September 27 emulator E2E passed sign-in, estimation, persistence and cross-user denial | Live Firebase/Neon/S3 API smoke passed sign-in, profile, upload, extraction and ownership denial; full estimation awaits an approved model |
| Recovery | Live Neon snapshot restored locally with all four table checksums (13 profiles, 21 documents, 23 estimates, 2 shares); new uploaded object restored and hash-verified; 20 owner-confirmed legacy test uploads absent | Retain private backup and exact-ID exceptions; cloud failover remains unverified |
| ML | Training authorized; larger datasets and candidates evaluated; research Ridge improves median-baseline MAE by 7.1% | Adequate absolute accuracy, planning-time parity and independent production acceptance remain open |
| Security/load | Authorization/parser/storage regression checks pass; Python production audit and frontend full dependency audit found no known vulnerabilities | CI passed; hosted 20-request check: liveness 10/10, p95 391 ms; readiness correctly 503. Scheduling and notification delivery remain unverified |
| Release | No accepted production ML bundle; UI preview exists | Live readiness, full authenticated estimation, restart persistence and rollback acceptance |

Completion of local contract tests does not establish model accuracy or live production readiness. See [ML evidence](runbooks/PRODUCTION_ML.md), [deployment runbook](runbooks/production-deployment.md), and [walkthrough](walkthrough.md).
