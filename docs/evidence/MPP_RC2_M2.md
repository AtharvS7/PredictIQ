# Milestone Push Procedure (MPP) Evidence: Milestone RC2_M2

**Program:** `PREDICTIQ_V2_RC2_HARDENING_PROGRAM`  
**Milestone:** `RC2_M2: Model & Data`  
**Tag:** `dev3-rc2-m2-model-data`  
**Local Commit SHA:** `70348785f37b63019b55ef882dde50f1f54b2ec6`  
**Date:** 2026-11-08  
**Compare URL:** https://github.com/AtharvS7/PredictIQ/compare/dev2...dev3  

---

## 1. Remote Branch Protection Attestation

Prior to push, remote tracking references were confirmed strictly against pre-registered baseline SHAs:

```text
git ls-remote origin dev2 main
d7a66b4095b8ae84f818900c2199c243f9d46b5f	refs/heads/dev2
894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43	refs/heads/main
```

- `origin/dev2` remains strictly locked at `d7a66b4095b8ae84f818900c2199c243f9d46b5f` (UNTOUCHED).
- `origin/main` remains strictly locked at `894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43` (UNTOUCHED).
- All changes are pushed strictly to `origin/dev3` and annotated milestone tags.

---

## 2. Checkpoints Covered in Milestone RC2_M2

- **R05 (Empirical Bayes Shrinkage):** Conjugate normal hierarchical model ($w_k = k / (k + 2.83)$). Calibrated on $N=915$ historical projects. Macro MdAPE improved by $+11.89\%$ at $k=3$, $+14.85\%$ at $k=5$, $+19.52\%$ at $k=10$, and $+22.76\%$ at $k=20$. Verified safe clipping range $[0.33, 3.00]$. Evidence: `docs/evidence/R05.md`.
- **R06 (Data Expansion Round 2 Audit):** Audited gold-standard IFPUG dataset (`projects_v2.csv`, $N=915$). Zero duplicate keys, zero synthetic imputation, authenticated source SHA-256 hashes for China, Kitchenham, Desharnais, Maxwell, Albrecht, and AT&T Aptness. Evidence: `docs/evidence/R06.md`.
- **R07 (Challengers Re-evaluation):** Evaluated challenger models (B, D, and Track 2 MonotoneHistGradientBoosting) against frozen protocol criteria ($+3.0\%$ improvement threshold). All challengers failed to exceed the incumbent threshold. Incumbent Model A (`MultivariateMonotoneModel` size-only power-law) confirmed as primary production estimator. Evidence: `docs/evidence/R07.md`.
- **R08 (Conformal Likely Band P25–P75):** Implemented Mondrian split-conformal calibration for inner 50% Likely Band alongside outer 80% Plausible Range ($q_{\text{small}}=0.6073$, $q_{\text{medium}}=0.5999$, $q_{\text{large}}=0.6565$, $q_{\text{global}}=0.6004$). Monotonic non-crossing invariant guaranteed: $1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$. Evidence: `docs/evidence/R08.md`.
- **R09 (NLP & Golden SRS Benchmark Suite):** Created 36 verified gold SRS documents across 6 software domains (Web, Mobile, Cloud/APIs, Data Pipelines, Enterprise/ERP, IoT/Embedded) with ground-truth annotations. Automated evaluation harness (`run_r09_srs_eval.py`) and pytest suite (`test_nlp_gold_srs.py`) pass 100% of quality gates: 0 crashes, 0.00% size MdAPE, 0.9919 tech stack Micro-F1, 100.0% feature recall, 0.19 integration count MAE. Evidence: `docs/evidence/R09.md` and `docs/evidence/r09_srs_results.json`.
- **R12 (Zero-Pickle Pure JSON Serving):** Completely eliminated `pickle.load` from production serving runtime. Exported all parameters to `model_params.json` with SHA-256 verification in `manifest.json`. Evidence: `docs/evidence/R12.md`.

---

## 3. Real Verification Suite Counts

1. **Python Linting:** `ruff check backend/app backend/ml --select E,W,F,I --ignore E501,E402` &rarr; **0 errors**.
2. **Python Static Typing:** `mypy app/` (in `backend/`) &rarr; **0 errors across 48 source files**.
3. **Backend Test Suite:** `pytest backend/tests -q` &rarr; **661 passed, 6 skipped in 167.0s**.
4. **Scripts Test Suite:** `pytest scripts/tests -q` &rarr; **50 passed, 4 skipped in 7.3s**.
5. **Frontend Typecheck:** `npm --prefix frontend run typecheck` &rarr; **0 errors**.
6. **Frontend Unit/Component Tests:** `npx --prefix frontend vitest run --root frontend --pool=forks` &rarr; **132 passed across 24 test files in 110.6s**.
7. **Frontend Production Build:** `npm --prefix frontend run build` &rarr; **dist/ built cleanly in 48.8s**.
8. **Security & Hygiene Audit:** **0 secrets, 0 forbidden files (.env, *.pem, serviceAccount*.json), 0 files > 50MB**.

---

## 4. Remote Verification

```text
git ls-remote origin dev3 dev3-rc2-m2-model-data
70348785f37b63019b55ef882dde50f1f54b2ec6	refs/heads/dev3
ab96ad3a9c78f7b0e6f98d2958c43824b86855d8	refs/tags/dev3-rc2-m2-model-data
```
