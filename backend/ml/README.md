# Predictify ML Artifacts

This directory contains the trained ML model and supporting files for effort prediction.

## Files

| File | Description | Git-tracked? |
|------|-------------|:---:|
| `Predictify_best_model.pkl` | Trained XGBoost regressor (≈6.4 MB) | ❌ `.gitignore` |
| `Predictify_scaler.pkl` | StandardScaler fitted on training data | ❌ `.gitignore` |
| `Predictify_features.json` | Ordered list of 27 model features | ✅ |
| `Predictify_merged_dataset.csv` | 740-row training dataset | ✅ |
| `Predictify_model_report.json` | Training metrics (R², MAE, MAPE) | ✅ |
| `train.py` | Training pipeline script | ✅ |
| `evaluate.py` | Model evaluation & visualization | ✅ |
| `inference.py` | Prediction engine used at runtime | ✅ |

## Regenerating Models

If `.pkl` files are missing (e.g., fresh clone), run:

```bash
cd backend
python -m ml.train
```

This reads `Predictify_merged_dataset.csv`, trains the XGBoost model, and writes the `.pkl` artifacts.

## Model Architecture

- **Algorithm**: XGBoost Regressor
- **Features**: 27 numeric features (T-factors, function points, team metrics)
- **Target**: `effort_hours` (log-transformed during training)
- **Dataset**: 740 rows merged from ISBSG, COCOMO, and Desharnais benchmarks
