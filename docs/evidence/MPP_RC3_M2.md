# Milestone Push Procedure (MPP) Evidence: Milestone RC3_M2

<!-- STATUS:START -->
**Status:** Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08
<!-- STATUS:END -->

**Program:** `PREDICTIQ_RC3_PORTABILITY_VALIDITY_DOCS_PROGRAM`  
**Milestone:** `RC3_M2: Data, NLP & Product`  
**Tag:** `dev3-rc3-m2-data-nlp-product`  
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

## 2. Checkpoints Covered in Milestone RC3_M2

- **S03 (Data Expansion Round 3):** Evaluated 18 candidate software datasets. Preserved 100% pure IFPUG FP + audited person-hours for primary training pool (`projects_v2.csv`, $N=915$). Documented secondary tracks in `docs/data/sources.yaml`. Evidence: `docs/evidence/S03.md`.
- **S04 (Model Challengers Evaluation):** Re-evaluated Hierarchical mixed-effects, Quantile regression L1, and MonotoneHistGradientBoosting under frozen protocol RC3. Incumbent Model A confirmed and retained. Evidence: `docs/evidence/S04.md`.
- **S05 (Real-Document NLP Validation):** Curated 18 authentic public requirements specifications (PURE open corpus, 95,299 words). Relabeled synthetic fixtures to regression sets. Provided user labeling kit `docs/data/nlp_real_labeling_template.csv`. Evidence: `docs/evidence/S05.md`.
- **S06 (Bulk Project Import & Org Calibration):** Authored `org_calibration.py` with Empirical Bayes shrinkage factor $w = \frac{k}{k + 2.57}$, shifted intercept, slope preservation, and monotonic quantile scaling. Added `POST /api/v1/estimates/bulk-import` and `POST /api/v1/estimates/calibration-preview`. Evidence: `docs/evidence/S06.md`.
- **S07 (Frontend Quality & Responsive Review):** Aligned all UI components to Monotone Power-Law, Brooks' Law capacity planning, and empirical conformal coverage citations. Vitest component suite (132/132 tests) passing. Evidence: `docs/evidence/S07.md`.

---

## 3. Real Verification Suite Counts

1. **Organizational Calibration Unit Tests:** `pytest backend/tests/test_org_calibration.py` &rarr; **5 passed**.
2. **Bulk Import API Tests:** `pytest backend/tests/test_bulk_import.py` &rarr; **7 passed**.
3. **Frontend Strict Typecheck:** `npm --prefix frontend run typecheck` &rarr; **0 errors**.
4. **Frontend Vitest Suite:** `npx --prefix frontend vitest run --root frontend --pool=forks` &rarr; **132 passed across 24 test files**.
5. **Frontend Production Build:** `npm --prefix frontend run build` &rarr; **dist/ built cleanly**.
6. **NLP Robustness Suite:** `pytest backend/tests/test_nlp_robustness.py` &rarr; **19 passed**.
