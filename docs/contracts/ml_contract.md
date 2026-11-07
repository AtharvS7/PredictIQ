# PredictIQ ML Contract (v2.0-FROZEN)

**Version:** `2.0.0-contract`  
**Status:** FROZEN  
**Applies To:** All training pipelines (`backend/ml/**`), inference engines (`backend/ml/inference.py`), and serving layers (`backend/app/services/ml_service.py`).

---

## 1. Allowed Inference Inputs

Under the v2 upgrade program, the machine learning models are strictly prohibited from consuming fabricated or synthetic features. Every feature supplied to the model at inference time MUST be directly provided by the user or honestly extracted from requirements documents.

### Permitted Inputs:
1. **`size_fp`** (*Required*, `float > 0`):
   - Unit: Function Points (IFPUG 4.x or COSMIC functional size units).
   - Provenance: Either manually entered by user or derived with calibrated uncertainty from requirements text by the NLP cascade.
   - Primary input driving the production monotone power-law effort estimate ($E = a \cdot S^b$).
2. **`duration_months`** (*Optional*, `float > 0` or `null`):
   - Label in UI: **"Planned Target Duration"** (used strictly for schedule display, timeline planning, and staffing feasibility; per frozen R03 decision, does not alter raw effort estimates).
3. **`team_size`** (*Optional*, `int >= 1` or `null`):
   - Planned team size in full-time equivalent software developers (used for timeline calculation, schedule feasibility, and cost display; excluded from effort model inputs).
4. **`platform` / `language` / `dev_type`** (*Optional*, categoricals):
   - Permitted ONLY if covered by empirical historical data without imputation.

### Strictly FORBIDDEN Inputs (Fabrication Ban):
The following legacy features from v1/dev2 are permanently dropped:
- `T01` through `T15` (General System Characteristics / technical complexity factors)
- `Transactions`, `Entities`, `PointsNonAdjust`, `Adjustment`
- `TeamExp`, `ManagerExp`
- `risk_score` (computed downstream from risk analyzer, never an input to effort)
- Any target-derived feature, productivity ratio, or unit conversion lacking empirical evidence.

Train/serve skew rule: If an input cannot be honestly collected from a real user or NLP in production, it MUST NOT exist in training matrices.

---

## 2. Model Outputs & Uncertainty

The model outputs probability-calibrated interval estimates in natural units:
1. **`effort_hours`**:
   - `p10`: 10th percentile effort estimate (person-hours)
   - `p50`: Median expected effort estimate (person-hours)
   - `p90`: 90th percentile effort estimate (person-hours)
   - Monotonic constraint: `p10 <= p50 <= p90`.
2. **`person_months`**:
   - Converted from `effort_hours` using a cited, standard conversion: 152 productive hours per person-month.
3. **`data_quality_tier`**:
   - `A`: High quality — Verified user Function Points within empirical training domain.
   - `B`: Medium quality — NLP-extracted Function Points with quantified uncertainty, or slight extrapolation.
   - `C`: Wide uncertainty / Out-of-distribution — Substantial extrapolation or low document parsing confidence.
4. **`ood_flags`**:
   - List of out-of-distribution indicators (e.g. `size_fp_exceeds_training_max`, `duration_compression_extreme`). OOD conditions widen the prediction interval; they never silently clamp predictions to arbitrary thresholds.

---

## 3. Versioning & Serialization Safety

1. **Semantic Versioning:** Format `2.0.0-rc.1`.
2. **Artifact Manifest:** Every model bundle must include `manifest.json` containing:
   - Git commit hash
   - Dataset SHA-256 hash
   - Training timestamp
   - Scikit-learn, numpy, pandas versions
   - Candidate model family and parameters
   - SHA-256 hashes of all `.pkl` / weights files.
3. **Startup Verification:** Serving MUST verify:
   - Artifact hash is NOT in `REVOKED_MODEL_SHA256`.
   - Python environment matches major/minor version of training environment.
   - Missing or altered artifacts trigger immediate fail-closed startup errors.

