Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08

# Operational Runbook: Production ML Training, Verification & Promotion

This runbook specifies the operational procedures for training, validating, packaging, and promoting machine learning models for PredictIQ v2.

---

## 1. Production Model Architecture & Invariants

The production machine learning system consists of two tightly coupled components:
1. **Point Estimator (`MultivariateMonotoneModel`)**:
   - Power law relating functional size ($S$, in Function Points) to effort ($E$, in person-hours):
     $$E = a \cdot S^b, \quad a = \exp(\beta_0)$$
   - Fits with $b \approx 0.8270$, guaranteeing strictly sub-linear returns to scale and monotonic non-decreasing effort ($\partial \hat{y} / \partial S \ge 0$).
2. **Uncertainty Estimator (`MondrianConformalPredictor`)**:
   - Stratified conformal inference calibrated across size strata: Small ($< 100$ FP), Medium ($100$–$500$ FP), and Large ($> 500$ FP).
   - Generates outer 80% Plausible Range ($P_{10}$–$P_{90}$) and inner 50% Likely Band ($P_{25}$–$P_{75}$).
3. **Zero-Pickle Serving Guarantee**:
   - Model coefficients and calibration quantiles are serialized exclusively into pure JSON (`model_params.json`). No binary pickle files are executed in the serving path.

---

## 2. Training Dataset Specification

Production models are trained strictly on the gold dataset `backend/ml/data/projects_v2.csv`:
- **Total Completed Projects**: 915
- **Verified SHA-256**: `b05ad3b0111d4ed3ff89b7aa2a0f653e494f81953c701916f27756d1746eede3`
- **Six Historical Data Sources**: China (499), Desharnais (81), Kitchenham (145), Maxwell (62), Albrecht (24), AT&T Aptness (104).
- **Target Variable**: Total observed person-hours (`effort_hours`).

---

## 3. Retraining Execution Procedure

To execute production model retraining:

```bash
# 1. Activate Python 3.12 environment
source backend/.venv/bin/activate  # or backend\.venv\Scripts\activate on Windows

# 2. Run the production training pipeline
cd backend
python -m ml.artifacts.train_production
cd ..
```

### Pipeline Actions Executed
1. Reads `projects_v2.csv` and verifies dataset record count (915) and SHA-256.
2. Fits `MultivariateMonotoneModel` on log-transformed size and effort.
3. Fits `MondrianConformalPredictor` using split-conformal calibration across size strata.
4. Serializes parameters into `backend/ml/artifacts/production_v2/model_params.json`.
5. Computes SHA-256 hashes for all output files and compiles `manifest.json`.

---

## 4. Verification & Promotion Gates

Before promoting new model artifacts to production serving:

### Gate 1: Cryptographic Loader Verification
Verify that `loader.py` validates the newly generated bundle without errors:
```bash
python -c "
from backend.ml.artifacts.loader import load_production_model
bundle = load_production_model()
print('Model loaded successfully:', bundle.model_version, bundle.architecture)
"
```

### Gate 2: Numerical Parity & Serving Integration
Run the serving integration test suite to verify quantile monotonicity and contract adherence:
```bash
pytest backend/tests/test_serving_integration.py -v
```
All tests must pass, confirming:
- $1.0 \le P_{10} \le P_{25} \le P_{50} \le P_{75} \le P_{90}$ everywhere.
- 152 productive hours per person-month conversion.
- Data Quality Tiers A, B, and C correctly assigned.
- Zero fabricated features.

### Gate 3: Release Gate Execution
Run the full unified release gate:
```bash
python scripts/release_gate.py
```
Confirm all 9 checks pass cleanly.
