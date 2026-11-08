# Milestone Push Procedure (MPP) Evidence: Milestone RC3_M1

<!-- STATUS:START -->
**Status:** Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08
<!-- STATUS:END -->

**Program:** `PREDICTIQ_RC3_PORTABILITY_VALIDITY_DOCS_PROGRAM`  
**Milestone:** `RC3_M1: Portability & Evidence`  
**Tag:** `dev3-rc3-m1-portability-evidence`  
**Date:** 2026-11-08  
**Compare URL:** https://github.com/AtharvS7/PredictIQ/compare/dev2...dev3  

---

## 1. Remote Branch Protection Attestation

Prior to milestone delivery, remote tracking references were confirmed strictly against pre-registered baseline SHAs:

```text
git ls-remote origin dev2 main
d7a66b4095b8ae84f818900c2199c243f9d46b5f	refs/heads/dev2
894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43	refs/heads/main
```

- `origin/dev2` remains strictly locked at `d7a66b4095b8ae84f818900c2199c243f9d46b5f` (UNTOUCHED).
- `origin/main` remains strictly locked at `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43` (UNTOUCHED).

---

## 2. Checkpoints Covered in Milestone RC3_M1

- **S00 (Orientation & Linux Truth Baseline):** Reproduced Linux hash divergence bug, recorded baseline test counts in Linux container and Windows host, established `docs/evidence/rc3_snapshot.md` and `docs/evidence/S00_findings.md`.
- **S01 (Portability & Artifact Hardening):** Added root `.gitattributes` (`eol=lf`), implemented deterministic UTF-8 canonical JSON hashing (`8066e9cf...`), purged all `.pkl` files and `pickle.load` references from `loader.py`, verified model loading in Linux container (`predictiq-backend-local-check:20260917`). Evidence: `docs/evidence/S01.md`.
- **S02 (Truthful Model Validation Evidence):** Executed 6-fold Leave-One-Source-Out (LOSO) cross-validation across all 915 records of `projects_v2.csv`. Generated single source of truth `model_report.json`, metrics floor `metrics_floor.json`, and rendered `docs/MODEL_VALIDATION_SUMMARY.md`. Evidence: `docs/evidence/S02.md`.

---

## 3. Real Verification Suite Counts

1. **Model Loader & Integrity Tests:** `pytest backend/tests/test_model_loader.py` &rarr; **20 passed**.
2. **Model Sanity & Quantiles:** `pytest backend/tests/test_model_sanity.py` &rarr; **35 passed**.
3. **Health & Readiness:** `pytest backend/tests/test_health_ready.py` &rarr; **3 passed**.
4. **Metrics Floor Validator:** `python scripts/check_metrics_floor.py` &rarr; **ALL GATES PASSED**.
5. **Documentation Specification Audit:** `python scripts/docs_audit.py` &rarr; **129 files, 100% compliant**.
6. **Linux Container Verification:** Docker container execution confirmed identical model loading and quantiles.
