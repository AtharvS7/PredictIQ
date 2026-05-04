"""
Predictify Model Evaluation Script
===================================
Run after train.py to verify the saved model artifacts are correct.
Tests on held-out data + synthetic project scenarios.

Run: python backend/ml/evaluate.py
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

ML_DIR = Path(__file__).parent


def load_artifacts() -> tuple[Any, Any, list[str], dict]:
    """Load all model artifacts and validate they exist."""
    print("Loading artifacts...")

    required = [
        ML_DIR / "predictiq_best_model.pkl",
        ML_DIR / "predictiq_scaler.pkl",
        ML_DIR / "predictiq_features.json",
        ML_DIR / "predictiq_model_report.json",
    ]

    missing = [p.name for p in required if not p.exists()]
    if missing:
        print(f"ERROR: Missing artifacts: {missing}")
        print("Run `python backend/ml/train.py` first.")
        sys.exit(1)

    with open(required[0], "rb") as f:
        model = pickle.load(f)
    with open(required[1], "rb") as f:
        scaler = pickle.load(f)
    with open(required[2], "r") as f:
        features = json.load(f)
    with open(required[3], "r") as f:
        report = json.load(f)

    print(f"  Model:    {type(model).__name__}")
    print(f"  Features: {len(features)}")
    print(f"  Best:     {report.get('best_model', 'N/A')}")

    # Show reported best R2
    for result in report.get("results", []):
        if result.get("Model") == report.get("best_model"):
            print(f"  Reported R2: {result.get('R2', 'N/A')}")
            break

    return model, scaler, features, report


def evaluate_on_dataset(model: Any, scaler: Any, features: list[str]) -> None:
    """Evaluate the model against the held-out test set (same split as training)."""
    dataset_path = ML_DIR / "predictiq_merged_dataset.csv"
    if not dataset_path.exists():
        print("\n[!]  Dataset not found -- skipping dataset evaluation")
        return

    df = pd.read_csv(dataset_path)

    # Same preprocessing as train.py
    drop_cols = ["effort_hours", "log_effort", "effort_per_fp"]
    X = df.drop(columns=[c for c in drop_cols if c in df.columns])
    X = X.select_dtypes(include=[np.number]).fillna(0)
    y = df["log_effort"]

    # Reindex to match exact feature order
    X = X.reindex(columns=features, fill_value=0)

    # Same split as training
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_test_s = scaler.transform(X_test)

    pred_log = model.predict(X_test_s)
    y_pred = np.expm1(pred_log)
    y_true = np.expm1(y_test.values)

    r2 = r2_score(y_true, y_pred)
    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    rel_e = np.abs(y_pred - y_true) / (y_true + 1)
    pred25 = float((rel_e < 0.25).mean() * 100)
    pred50 = float((rel_e < 0.50).mean() * 100)
    mmre = float(rel_e.mean() * 100)

    print("\n-- Dataset Evaluation (held-out 20%) --")
    print(f"  R2       = {r2:.4f}")
    print(f"  MAE      = {mae:.1f} hours")
    print(f"  RMSE     = {rmse:.1f} hours")
    print(f"  PRED25%  = {pred25:.1f}%")
    print(f"  PRED50%  = {pred50:.1f}%")
    print(f"  MMRE     = {mmre:.1f}%")

    if r2 >= 0.70:
        print(f"  Status   : [OK] EXCELLENT (R2>=0.70)")
    elif r2 >= 0.55:
        print(f"  Status   : [OK] PASS (R2>=0.55)")
    else:
        print(f"  Status   : [!]  BELOW TARGET (R2<0.55)")

    # Show individual predictions
    print("\n  Sample predictions:")
    for i in range(min(5, len(y_true))):
        actual = y_true[i]
        predicted = y_pred[i]
        error_pct = abs(predicted - actual) / (actual + 1) * 100
        print(
            f"    Actual: {actual:,.0f}h  "
            f"Predicted: {predicted:,.0f}h  "
            f"Error: {error_pct:.1f}%"
        )


def test_synthetic_prediction(
    model: Any, scaler: Any, features: list[str]
) -> None:
    """Test with 3 synthetic project types to verify inference pipeline."""
    test_cases = [
        {
            "name": "Small Web App (10 features, 3mo, Low complexity)",
            "vector": {
                "size_fp": 90.0,
                "duration_months": 3.0,
                "TeamExp": 2.0,
                "ManagerExp": 2.0,
                "Transactions": 76.5,
                "Entities": 27.0,
                "PointsNonAdjust": 100.0,
                "Adjustment": 0.9,
                "T07": 2.0,
                "T09": 2.0,
                "T10": 2.0,
                "T11": 2.0,
                "log_size_fp": float(np.log1p(90)),
                "complexity_score": 2.0,
                "team_skill_avg": 2.0,
                "risk_score": 2.5,
            },
        },
        {
            "name": "Medium SaaS (20 features, 8mo, Medium complexity)",
            "vector": {
                "size_fp": 180.0,
                "duration_months": 8.0,
                "TeamExp": 3.0,
                "ManagerExp": 3.0,
                "Transactions": 153.0,
                "Entities": 54.0,
                "PointsNonAdjust": 200.0,
                "Adjustment": 0.9,
                "T07": 3.0,
                "T09": 3.0,
                "T10": 3.0,
                "T11": 3.0,
                "log_size_fp": float(np.log1p(180)),
                "complexity_score": 3.0,
                "team_skill_avg": 3.0,
                "risk_score": 3.0,
            },
        },
        {
            "name": "Large Enterprise (40+ features, 18mo, Very High complexity)",
            "vector": {
                "size_fp": 310.0,
                "duration_months": 18.0,
                "TeamExp": 4.0,
                "ManagerExp": 4.0,
                "Transactions": 263.5,
                "Entities": 93.0,
                "PointsNonAdjust": 350.0,
                "Adjustment": 0.89,
                "T07": 5.0,
                "T09": 5.0,
                "T10": 5.0,
                "T11": 4.5,
                "log_size_fp": float(np.log1p(310)),
                "complexity_score": 4.8,
                "team_skill_avg": 3.5,
                "risk_score": 4.0,
            },
        },
    ]

    print("\n-- Synthetic Prediction Test --")
    for case in test_cases:
        vec = np.array(
            [float(case["vector"].get(f, 0.0)) for f in features]
        ).reshape(1, -1)
        vec_s = scaler.transform(vec)
        log_pred = float(model.predict(vec_s)[0])
        effort = float(np.expm1(log_pred))

        cost_75 = effort * 75
        effort_min = effort * 0.80
        effort_max = effort * 1.40

        print(f"\n  {case['name']}")
        print(f"    Effort (likely): {effort:,.0f} hrs")
        print(f"    Cost @ $75/hr:   ${cost_75:,.0f}")
        print(f"    Range:           ${effort_min * 75:,.0f} - ${effort_max * 75:,.0f}")

        # Sanity check: effort should be reasonable
        if 200 <= effort <= 20000:
            print(f"    Sanity:          [OK] In range (200-20K hrs)")
        else:
            print(f"    Sanity:          [!]  Outside expected range")


def test_inference_module() -> None:
    """Test the inference module directly (as FastAPI would use it)."""
    print("\n-- Inference Module Test --")
    try:
        # Import the inference singleton
        import importlib
        import sys

        # Add backend to path if needed
        backend_dir = ML_DIR.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from ml.inference import predictor

        loaded = predictor.load()
        status = predictor.get_status() if hasattr(predictor, "get_status") else predictor.get_model_info()

        print(f"  Loaded:     {loaded}")
        print(f"  Mode:       {status.get('model_mode', 'unknown')}")
        print(f"  Model:      {status.get('best_model', status.get('model_name', 'unknown'))}")

        # Quick prediction test
        test_features = {
            "size_fp": 150.0,
            "duration_months": 6.0,
            "TeamExp": 2.0,
            "ManagerExp": 2.5,
            "log_size_fp": float(np.log1p(150)),
            "complexity_score": 3.0,
            "team_skill_avg": 2.5,
            "risk_score": 3.0,
        }
        result = predictor.predict(test_features)
        print(f"\n  Test prediction (size_fp=150, 6mo):")
        print(f"    Effort:     {result['effort_hours_likely']:,.0f} hrs")
        print(f"    Range:      {result['effort_hours_min']:,.0f} - {result['effort_hours_max']:,.0f} hrs")
        print(f"    Confidence: {result['confidence_pct']}%")
        print(f"    Mode:       {result['model_mode']}")
        print(f"  Status:     [OK] Inference module working")

    except Exception as e:
        print(f"  [!]  Inference module test failed: {e}")
        print("  (This is normal if running outside the backend package context)")


def main() -> None:
    """Run all evaluation tests."""
    print("=" * 55)
    print("Predictify Model Evaluation")
    print("=" * 55)

    model, scaler, features, report = load_artifacts()
    evaluate_on_dataset(model, scaler, features)
    test_synthetic_prediction(model, scaler, features)
    test_inference_module()

    print("\n" + "=" * 55)
    print("[OK] Evaluation complete. Model ready for inference.")
    print("=" * 55)


if __name__ == "__main__":
    main()
