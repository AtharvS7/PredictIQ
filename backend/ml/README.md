# PredictIQ Machine Learning Architecture (v2.0)

**Version:** 2.0.0-rc.3  
**Architecture:** Monotone Power-Law with Mondrian Split-Conformal Prediction & Empirical Bayes Shrinkage  
**Validation Evidence:** [MODEL_VALIDATION_SUMMARY.md](../../docs/MODEL_VALIDATION_SUMMARY.md)  
**Model Card:** [docs/ml/model-card.md](../../docs/ml/model-card.md)  

---

## 1. Overview & Architecture

PredictIQ v2 provides transparent, empirically grounded software project effort and uncertainty estimation. The core prediction engine uses a univariate Monotone Power-Law where effort depends strictly on functional size ($size\_fp$), augmented with Mondrian split-conformal prediction intervals and Empirical Bayes organization calibration.

```
                    ┌───────────────────────────────┐
                    │  Input: size_fp (IFPUG FP)    │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Monotone Power Law            │
                    │       E = a * S^b             │
                    │   (b = 0.8270 > 0 enforced)   │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Mondrian Conformal Calibrator │
                    │   80% Plausible (P10 - P90)   │
                    │   50% Likely    (P25 - P75)   │
                    │  (Stratified by Size Strata)  │
                    └───────────────┬───────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │ Serving Result: P10..P90      │
                    │ Pure JSON, Zero-Pickle        │
                    └───────────────────────────────┘
```

---

## 2. Directory Structure

```
backend/ml/
├── artifacts/             # Verified production model bundles and manifests
│   ├── loader.py          # Cryptographically verified, pure JSON zero-pickle loader
│   ├── production_v2/     # Active bundle: manifest.json, model_params.json
│   └── train_production.py# Canonical production training script
├── calibration/           # Uncertainty quantification
│   ├── conformal.py       # MondrianConformalPredictor implementation
│   └── run_calibration.py # Calibration and coverage validation runner
├── data/                  # Curated empirical dataset
│   ├── projects_v2.csv    # 915 empirical software projects across 6 historical sources
│   ├── sources.yaml       # Source metadata, licenses, and provenance
│   └── LICENSE_SUMMARY.md # Legal and licensing documentation
├── eval/                  # Evaluation protocol and empirical benchmarks
│   ├── baselines.py       # Statistical baselines (median dummy, log-linear OLS)
│   ├── metrics.py         # Primary metrics (MdAPE, PRED(25), MAE)
│   ├── protocol.py        # Leave-One-Source-Out (LOSO) cross-validation splitter
│   ├── run_s02_validation.py # Empirical 6-fold LOSO validation runner
│   └── run_r07_challengers.py# Challenger model evaluation harness
└── reports/               # Generated sources of truth
    └── model_report.json  # Canonical single source of truth for all metrics
```

---

## 3. Serving Runtime & Security

- **Pure JSON Artifacts:** Model parameters reside in `artifacts/production_v2/model_params.json` with zero pickle dependencies.
- **Deterministic Canonical Hashing:** Integrity is verified via UTF-8 canonical JSON SHA-256 (`8066e9cf4c18f5fa45957bad9050cbab6effb68923a787f974640a463ede93d2`) ensuring line-ending invariance across Windows and Linux.
- **Fail-Closed Runtime:** Missing artifacts, schema drift, or checksum tampering immediately abort startup with descriptive diagnostics.
