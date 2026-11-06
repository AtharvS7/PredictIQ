# PredictIQ v2 Milestones Log

This file tracks each milestone achieved on `dev3`, the checkpoints covered, test verification counts, and local HEAD SHAs.

---

## Milestone M1: Data Foundation (`dev3-m1-data-foundation`)

- **Tag:** `dev3-m1-data-foundation`
- **Meaning:** Baseline, contracts freeze, verified data sources, dataset v2, and rigorous data quality tests.
- **Checkpoints Covered:**
  - **CP00 (Baseline, Branch & Hygiene):** Audited repository, created `dev3` from HEAD (`d7a66b4`), configured `.gitignore` against raw research and cache leaks, established 8 isolated git worktrees in `.worktrees/`.
  - **CP01 (Contracts Freeze):** Established `ml_contract.md`, `api_estimate_v2.json`, `mock_estimate_v2.json`, and frozen evaluation protocol SHA-256 (`b3fac93ff853f213dba8f0815dfea0f837dc5fa035fc7a8ba2b10c24fa8834e0`).
  - **CP02 (Source Registry & Licences):** Evaluated 17 sources, selected 6 core empirical datasets (China, Kitchenham, Desharnais, Maxwell, Albrecht, AT&T), documented future ISBSG commercial track in `ISBSG_PLAN.md`.
  - **CP03 (Acquire & Verify):** Built deterministic hash-verified `acquire_all.py`, verified China project 1 effort = 7490 person-hours (resource code 4 dropped).
  - **CP04 (Harmonise Schema):** Built `backend/ml/rebuild_dataset.py`, generated `projects_v2.csv` (915 rows), verified Albrecht *1000 multiplier, published `DEDUPLICATION_REPORT.md` (zero unrecorded conversions).
  - **CP05 (Data Quality & Leakage Gates):** Built `backend/tests/test_data_v2.py` (9/9 passed), built `backend/ml/data/check_leakage.py` (PASS, 0 duplicate keys, 0 banned features), published manifest revoking `predictiq_merged_dataset.csv`, and published `docs/data/DATASHEET.md`.

### Verification Test Summary
- **Backend Test Suite:** 601 passed, 7 skipped
- **Dataset v2 Quality Suite:** 9 passed, 0 failed (`backend/tests/test_data_v2.py`)
- **Research Suite:** 12 passed, 0 failed
- **Frontend Typecheck:** 0 errors (`tsc --noEmit && tsc -p tsconfig.test.json --noEmit`)
- **Frontend Vitest Suite:** 85 passed across 15 test files
- **Frontend Production Build:** Successful in ~22s
- **Python Lint & Typing:**
  - `ruff check backend/app --select E,W,F,I --ignore E501`: 0 errors (all checks passed)
  - `mypy --config-file backend/mypy.ini backend/app`: 0 errors (44 source files clean)

### Key Metrics
- **Harmonized Dataset:** 915 total rows, SHA-256 `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`
- **Productivity Range:** Min $0.32$ h/FP, Median $9.17$ h/FP, Max $95.14$ h/FP
- **Local HEAD SHA:** `eeedb40`
