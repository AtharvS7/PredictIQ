# PredictIQ Final Demonstration Snapshots

This document records the immutable verification snapshots and milestone tags for the final demonstration program on branch `dev3`.

---

## Remote Branch Baselines (Invariant)

| Remote Branch | Required SHA-1 Checksum | Verification Status |
|:--------------|:------------------------|:-------------------:|
| `origin/dev2` | `d7a66b4095b8ae84f818900c2199c243f9d46b5f` | **VERIFIED** |
| `origin/main` | `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43` | **VERIFIED** |

---

## Checkpoint Milestones

### H00: Baseline Environment and Safety Verification
- **Tag:** `backup-before-final-demo`
- **Scope:** Repository audit, disk and memory baselines, local backup archive (`_backups/PredictIQ-dev3-before-final.zip`), quarantine directories initialized.
- **Status:** PASS

### H01: Single-Command Production Demonstration Launcher
- **Tag:** `dev3-final-01`
- **Scope:** Production demonstration launcher (`run.py`), dynamic port allocation (backend 8010-8019, frontend 5173-5179), CORS dynamic dev origin allowance, Vite preview proxy, preflight audits, canonical model validation, and clean process lifecycle management.
- **Tests:** 6 launcher unit tests passed; 3-run cold start verification gate passed in 35.4s, 19.3s, 25.1s (<45s threshold).
- **Status:** PASS

### H02: Landing Page and Authentication Experience
- **Tag:** `dev3-final-02`
- **Scope:** Executive landing page overhaul, 3-step workflow guidance, enterprise capability highlights, unauthenticated navigation with Sign In / Sign Up buttons, route-level redirect preservation, and automated prohibited terminology checks.
- **Tests:** 11 vitest tests passed; typecheck passed; production build passed in 10.54s; live launcher gate verified HTTP 200 on `/` in 0.078s and `/auth` in 0.016s (<2.0s threshold).
- **Status:** PASS

### H03: User Interface Refinement, Terminology Governance & Performance
- **Tag:** `dev3-final-03`
- **Scope:** Complete elimination of prohibited technical jargon and legacy brand tokens across components, modals, and store modules; WCAG AA light/dark contrast verification; responsive layout testing (360px, 768px, 1280px); automated DOM prohibited terms audit.
- **Tests:** 152 vitest tests passed across all 27 test files (100%); typecheck passed; production build passed in 18.89s; live launcher gate verified HTTP 200 on `/` in 0.031s, `/auth` in 0.031s, and `/api/v1/ready` in 0.454s (<2.0s threshold) with 0 prohibited terms in served HTML.
- **Status:** PASS


