# Milestone Push Procedure (MPP) Evidence: RC2_M1

**Program:** `PREDICTIQ_V2_RC2_HARDENING_PROGRAM`  
**Milestone:** `RC2_M1` (`dev3-rc2-m1-wiring-cleanup`)  
**Date:** 2026-11-07  
**Branch:** `dev3`  
**Commit SHA:** `4544c38f714ef27983bce802c40ed5de0ca90c38`  
**Tag:** `dev3-rc2-m1-wiring-cleanup` (`39d86de05ed300a6866bc403c8c8e30bdbe2aa12`)  
**Compare URL:** `https://github.com/AtharvS7/PredictIQ/compare/dev2...dev3`

---

## 1. Remote Branch Protection Verification

Command:
```powershell
git ls-remote origin dev2 main
```

Output:
```text
d7a66b4095b8ae84f818900c2199c243f9d46b5f	refs/heads/dev2
894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43	refs/heads/main
```

Result: **VERIFIED**. Exactly matches baseline SHAs recorded in `docs/evidence/rc2_snapshot.md`. Zero changes to protected branches.

---

## 2. Remote Push Verification

Command:
```powershell
git ls-remote origin dev3 dev3-rc2-m1-wiring-cleanup
```

Output:
```text
4544c38f714ef27983bce802c40ed5de0ca90c38	refs/heads/dev3
39d86de05ed300a6866bc403c8c8e30bdbe2aa12	refs/tags/dev3-rc2-m1-wiring-cleanup
```

Result: **VERIFIED**. Remote `origin/dev3` is synchronized with local HEAD, and annotated tag `dev3-rc2-m1-wiring-cleanup` exists.

---

## 3. Mandatory Quality Gates & Real Test Counts

| Quality Gate | Command | Result | Notes |
|---|---|---|---|
| **Python Linting** | `ruff check backend/app backend/ml --select E,W,F,I --ignore E501,E402` | **PASS (0 errors)** | Clean |
| **Python Typing** | `mypy app/ --ignore-missing-imports --no-strict-optional --exclude 'ml/'` | **PASS (0 issues)** | 48 source files clean |
| **Full Backend Tests** | `pytest backend/tests -q --tb=short` | **PASS (655 passed, 6 skipped, 0 failed)** | 82% coverage (2,514 stmts), 104.56s |
| **Scripts Tests** | `pytest scripts/tests -q --tb=short` | **PASS (25 passed, 4 skipped, 0 failed)** | 6.89s |
| **Frontend Typecheck** | `npm --prefix frontend run typecheck` | **PASS (0 errors)** | `tsc` + `tsc -p tsconfig.test.json` clean |
| **Frontend Vitest** | `npx vitest run --pool=forks --no-file-parallelism` | **PASS (131 passed across 24 suites)** | 170.14s |
| **Frontend Build** | `npm --prefix frontend run build` | **PASS (0 errors)** | Production bundle in `frontend/dist/` in 5.61s |
| **Secret Scan** | Git diff regex scan for keys/tokens/.env | **PASS (0 matches)** | Clean |
| **Tracked Files** | `git ls-files` check against forbidden extensions and >50MB | **PASS (0 violations)** | Clean |

---

## 4. Checkpoints Delivered in Milestone RC2_M1

- **R00 (Orientation & Truth Baseline):** Remote safety verified; baseline recorded; test paths stabilized.
- **R01 (Decouple Legacy Predictor from Runtime):** Production decoupled from revoked predictor; readiness checks fail-closed.
- **R02 (Dead Code Removal in `backend/ml/`):** 30MB revoked pickle and 25 obsolete research scripts deleted.
- **R03 (Model Input Validity & Frozen Decision Rule):** Frozen decision rule evaluated; duration rejected under Brooks' Law; team size removed from model inputs; authentic provenance and HTTP 422 validations enforced.
- **R04 (Propagate Size Uncertainty into Effort Intervals):** Log-space variance combination preserves $\ge 80\%$ empirical coverage ($82.54\%$ verified over 10,000 simulations). Strict non-crossing quantiles enforced.
