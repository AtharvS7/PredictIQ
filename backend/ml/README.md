# PredictIQ Machine Learning Architecture (v2.0)

**Version:** 2.0.0-rc.2  
**Status:** PRODUCTION READY  
**Primary Track:** Track 1 Monotone Power Law + Mondrian Conformal Calibration  

---

## 1. Overview & Architecture

PredictIQ v2 replaces all uncalibrated heuristic models and legacy 27-feature pipelines with a mathematically rigorous, transparent, and calibrated effort estimation architecture:

```
                    ┌───────────────────────────────┐
                    │  Input: size_fp (IFPUG/COSMIC)│
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Track 1: Monotone Power Law   │
                    │       E = a * S^b             │
                    │   (b > 0 strictly enforced)   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Mondrian Conformal Calibrator │
                    │   80% Interval (P10 - P90)    │
                    │  (Stratified by Size Strata)  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Serving Result: P10, P50, P90 │
                    │ Tiering, OOD Flags, Lineage   │
                    └───────────────────────────────┘
```

---

## 2. Directory Structure

```
backend/ml/
├── artifacts/             # Verified production model bundles and manifests
│   ├── loader.py          # Cryptographically verified, fail-closed artifact loader
│   ├── production_v2/     # Current production bundle (manifest.json, model.pkl, conformal.pkl)
│   └── train_production.py# Canonical production training script
├── calibration/           # Uncertainty quantification
│   ├── conformal.py       # MondrianConformalPredictor implementation
│   └── run_calibration.py # Offline calibration and coverage validation runner
├── data/                  # Curated empirical dataset
│   ├── projects_v2.csv    # 915 empirical software projects across 6 historical sources
│   ├── sources.yaml       # Source metadata, licenses, and provenance
│   └── LICENSE_SUMMARY.md # Legal and licensing documentation
├── eval/                  # Evaluation protocol and metrics
│   ├── baselines.py       # Statistical baselines (COCOMO, mean/median, unconstrained OLS)
│   ├── metrics.py         # Primary metrics (MdAPE, PRED(25), R², RMSE, MAE)
│   ├── protocol.py        # Leave-One-Source-Out (LOSO) cross-validation splitter
│   └── run_r03_ablation.py# Checkpoint R03 duration ablation experiment
├── track1/                # Primary interpretable models
│   ├── models.py          # MonotonePowerLaw, MultivariateMonotoneModel, SegmentedMonotoneModel
│   └── run_eval.py        # Track 1 LOSO evaluation harness
├── track2/                # Challenger / research models
│   ├── models.py          # Random Forest, Gradient Boosting, MLP with monotonicity penalties
│   └── run_eval.py        # Track 2 LOSO evaluation harness
├── acquire_all.py         # Canonical dataset acquisition pipeline
├── artifact_safety.py     # Revoked checksum blacklist and validation hooks
└── __init__.py
```

---

## 3. Core Principles & Guarantees

1. **Monotonicity Guarantee:** For any functional size $S_1 < S_2$, the model strictly guarantees $\hat{E}(S_1) < \hat{E}(S_2)$ ($\partial \hat{E} / \partial S > 0$ everywhere).
2. **Strict Non-Crossing Quantiles:** At inference time, interval bounds strictly obey $1.0 \le P_{10} \le P_{50} \le P_{90}$.
3. **No Fabricated Features:** Fabricated complexity factors (legacy $T01-T15$), unadjusted metrics, and downstream scores are permanently banned.
4. **Schedule Separation (R03):** Effort point estimation is driven strictly by functional size ($E = a \cdot S^b$). Planned duration is used exclusively for scheduling and timeline feasibility; it does not alter raw effort estimates.
5. **Fail-Closed Artifact Safety:** Startup verifies SHA-256 checksums of all model files against manifest hashes and rejects revoked hashes.
