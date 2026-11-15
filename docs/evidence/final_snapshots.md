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
