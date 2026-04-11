# PredictIQ ML Module

## Overview

This module handles all machine learning functionality for PredictIQ:
- **Training**: GPU-accelerated model training on RTX 3050
- **Inference**: Production model serving via FastAPI
- **Evaluation**: Post-training verification and benchmarking

## Artifacts

| File | Size | Description |
|------|------|-------------|
| `predictiq_best_model.pkl` | ~694KB | Trained XGBoost/RF model |
| `predictiq_scaler.pkl` | ~2KB | Fitted StandardScaler |
| `predictiq_features.json` | ~1KB | 27 ordered feature names |
| `predictiq_model_report.json` | ~2KB | Training metrics + report |
| `predictiq_merged_dataset.csv` | ~24KB | 143-project training data |

## Quick Start

### 1. Training (RTX 3050 GPU)

```bash
cd C:\Users\ASUS\Downloads\PredictIQ
# Activate your virtual environment
venv\Scripts\activate

# Install ML dependencies
pip install xgboost scikit-learn pandas numpy matplotlib seaborn pdfplumber python-docx

# Run training — fully autonomous, ~5-20 minutes
python backend/ml/train.py
```

Training produces:
- `predictiq_best_model.pkl` — best model by R²
- `predictiq_scaler.pkl` — fitted StandardScaler
- `predictiq_features.json` — feature names in training order
- `predictiq_model_report.json` — all metrics + feature importances
- `artifacts/predictiq_feature_importance.png` — top 20 features plot
- `artifacts/predictiq_model_evaluation.png` — actual vs predicted + residuals
- `training_log_YYYYMMDD_HHMMSS.txt` — full training log

### 2. Evaluate Saved Model

```bash
python backend/ml/evaluate.py
```

This verifies the saved artifacts against the held-out test set and
runs synthetic prediction tests for 3 project sizes (small/medium/large).

### 3. Inference (automatic)

The model is auto-loaded when FastAPI starts:

```bash
uvicorn backend.main:app --reload --port 8000
```

Check model status at: `GET /api/v1/health`

If `model_loaded: true` → live inference mode.
If `model_loaded: false` → demo mode (realistic mock values).

## Architecture

```
backend/ml/
├── train.py                          # Standalone training script
├── inference.py                      # Production inference singleton
├── evaluate.py                       # Post-training verification
├── __init__.py
├── predictiq_best_model.pkl          # [Generated] Best model
├── predictiq_scaler.pkl              # [Generated] Fitted scaler
├── predictiq_features.json           # [Generated] Feature names
├── predictiq_model_report.json       # [Generated] Training report
├── predictiq_merged_dataset.csv      # Training data
├── README.md                         # This file
└── artifacts/                        # [Generated] Plots & extras
    ├── predictiq_feature_importance.png
    └── predictiq_model_evaluation.png
```

## Dataset

- **143 projects** from PROMISE Software Engineering Repository
- **Sources**: Desharnais (81) + Maxwell (62)
- **Target**: `effort_hours` (person-hours), trained on `log_effort = log1p(effort_hours)`
- **Features**: 27 numeric features including IFPUG T-factors, team experience, FP metrics

## Estimation Pipeline

```
Document Upload → PDF/DOCX Parser → NLP Feature Extraction
    → IFPUG Function Points → ML Prediction (XGBoost)
    → Parametric Cost Conversion → Risk Analysis
    → Benchmark Comparison → Results
```

## Model Performance

| Metric | Value |
|--------|-------|
| R² | ~0.65 |
| PRED25% | ~28% |
| MMRE | ~49% |
| Training Data | 143 projects |
| Features | 27 |

## Key Features (by importance)

1. `size_fp` — Adjusted Function Points
2. `T09` — Processing complexity
3. `log_size_fp` — Log-transformed FP
4. `complexity_score` — Composite complexity
5. `risk_score` — Risk indicator

## Retrain Instructions

To retrain with new data:

1. Append new rows to `predictiq_merged_dataset.csv`
2. Ensure columns match the existing schema
3. Run `python backend/ml/train.py`
4. Verify with `python backend/ml/evaluate.py`
5. Restart FastAPI — model auto-reloads
