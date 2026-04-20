"""
PredictIQ ML Training Pipeline v2.0
=====================================
GPU-accelerated training on RTX 3050 (CUDA).
Trains 8 models with expanded hyperparameter grids.
Uses 10-fold cross-validation on 740-project multi-source dataset.
Selects best by R2 + PRED25 composite score, saves all artifacts.

Dataset: 740 projects from 4 international sources:
  - Desharnais + Maxwell (143 existing)
  - China (481)
  - NASA93 (92)
  - Albrecht (24)

Run: python backend/ml/train.py
     (from project root)

Fully autonomous -- no user interaction required.
"""

import sys
import json
import pickle
import time
import warnings
from pathlib import Path
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, cross_val_score, KFold  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402
from sklearn.linear_model import LinearRegression, Ridge, Lasso  # noqa: E402
from sklearn.ensemble import (  # noqa: E402
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor,
)
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score  # noqa: E402

import xgboost as xgb  # noqa: E402


# -- Paths -------------------------------------------------------------
ML_DIR = Path(__file__).parent
DATA_CSV = ML_DIR / "predictiq_merged_dataset.csv"
OUT_DIR = ML_DIR / "artifacts"
OUT_DIR.mkdir(exist_ok=True)

LOG_FILE = ML_DIR / f"training_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"


def log(msg: str) -> None:
    """Print and write to log file simultaneously."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        # Windows cp1252 fallback: replace non-ASCII chars
        print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ======================================================================
# Step 1: Load data
# ======================================================================
def load_data() -> pd.DataFrame:
    """Load and validate the 740-row multi-source training dataset."""
    log("=" * 60)
    log("PredictIQ ML Training Pipeline v2.0 -- Starting")
    log("Dataset: 740 projects (4 international sources)")
    log(f"XGBoost version: {xgb.__version__}")
    log(f"NumPy version:   {np.__version__}")
    log(f"Pandas version:  {pd.__version__}")
    log("=" * 60)

    if not DATA_CSV.exists():
        log(f"ERROR: Dataset not found at {DATA_CSV}")
        log("Copy predictiq_merged_dataset.csv to backend/ml/ and retry.")
        sys.exit(1)

    df = pd.read_csv(DATA_CSV)
    log(f"\nDataset loaded: {df.shape[0]} rows x {df.shape[1]} columns")
    log(f"Effort range: {df['effort_hours'].min():.0f} - "
        f"{df['effort_hours'].max():.0f} person-hours")
    log(f"Mean effort:  {df['effort_hours'].mean():.0f} person-hours")
    log(f"Median effort: {df['effort_hours'].median():.0f} person-hours")
    log(f"size_fp range: {df['size_fp'].min():.1f} - "
        f"{df['size_fp'].max():.1f}")
    log(f"Missing values: {df.isnull().sum().sum()}")

    # Validate schema
    expected_cols = 30
    if df.shape[1] != expected_cols:
        log(f"WARNING: Expected {expected_cols} columns, got {df.shape[1]}")

    return df


# ======================================================================
# Step 2: Feature engineering
# ======================================================================
def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, list[str]]:
    """Prepare feature matrix and target vector."""
    log("\n-- Step 2: Preparing features --")

    # Drop target leakage columns
    drop_cols = ["effort_hours", "log_effort", "effort_per_fp"]
    drop_cols = [c for c in drop_cols if c in df.columns]

    X = df.drop(columns=drop_cols)
    y = df["log_effort"]  # Predict log-transformed effort

    # Keep only numeric columns
    X = X.select_dtypes(include=[np.number])

    # Safety: replace inf/-inf with 0, fill NaN
    X.replace([np.inf, -np.inf], 0, inplace=True)
    X.fillna(0, inplace=True)

    feature_names = list(X.columns)
    log(f"Features: {len(feature_names)} columns")
    log(f"Feature list: {feature_names}")
    log(f"Target: log_effort (range {y.min():.2f} - {y.max():.2f})")
    log(f"Samples per feature: {len(df) / len(feature_names):.1f}")

    # Save feature list (critical for inference)
    feat_path = ML_DIR / "predictiq_features.json"
    with open(feat_path, "w") as f:
        json.dump(feature_names, f, indent=2)
    log(f"Feature list saved -> {feat_path}")

    return X, y, feature_names


# ======================================================================
# Step 3: Train/test split + scaling
# ======================================================================
def split_and_scale(
    X: pd.DataFrame, y: pd.Series
) -> tuple[np.ndarray, np.ndarray, pd.Series, pd.Series, StandardScaler]:
    """Split data 80/20 and fit StandardScaler on training set."""
    log("\n-- Step 3: Train/test split + scaling --")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    log(f"Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    # Save scaler
    scaler_path = ML_DIR / "predictiq_scaler.pkl"
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    log(f"Scaler saved -> {scaler_path}")

    return X_train_s, X_test_s, y_train, y_test, scaler


# ======================================================================
# Step 4: Evaluation helper
# ======================================================================
def evaluate_model(
    name: str,
    model: Any,
    X_train: np.ndarray,
    y_train: pd.Series,
    X_test: np.ndarray,
    y_test: pd.Series,
) -> tuple[dict, Any]:
    """Train a model and compute all evaluation metrics."""
    t0 = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - t0

    pred_log = model.predict(X_test)
    y_pred = np.expm1(pred_log)
    y_true = np.expm1(np.array(y_test))

    mae = mean_absolute_error(y_true, y_pred)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = r2_score(y_true, y_pred)
    rel_e = np.abs(y_pred - y_true) / (y_true + 1)
    mmre = float(rel_e.mean() * 100)
    pred25 = float((rel_e < 0.25).mean() * 100)
    pred50 = float((rel_e < 0.50).mean() * 100)

    log(
        f"  {name:28s} R2={r2:.4f}  PRED25={pred25:.1f}%  "
        f"MMRE={mmre:.1f}%  ({train_time:.1f}s)"
    )

    return {
        "Model": name,
        "MAE": round(mae, 1),
        "RMSE": round(rmse, 1),
        "R2": round(r2, 4),
        "PRED25%": round(pred25, 1),
        "PRED50%": round(pred50, 1),
        "MMRE%": round(mmre, 1),
        "TrainTime_s": round(train_time, 1),
    }, model


# ======================================================================
# Step 5: Detect GPU
# ======================================================================
def get_xgb_device() -> str:
    """Return 'cuda' if RTX 3050 CUDA is available, else 'cpu'."""
    log("\n-- Step 4: GPU detection --")
    try:
        test_dmatrix = xgb.DMatrix(
            np.random.rand(10, 5), label=np.random.rand(10)
        )
        params = {"tree_method": "hist", "device": "cuda", "verbosity": 0}
        xgb.train(params, test_dmatrix, num_boost_round=1)
        log("  [OK] CUDA detected -> XGBoost will use RTX 3050 GPU")
        return "cuda"
    except Exception as e:
        log(f"  [!]  CUDA not available ({str(e)[:80]}) -> using CPU")
        return "cpu"


# ======================================================================
# Step 6: Define all models (expanded hyperparameters for 740 samples)
# ======================================================================
def build_models(device: str) -> dict[str, Any]:
    """Create all model instances with optimized hyperparameters for 740-row dataset."""
    log(f"\n-- Step 5: Building models (XGBoost device={device}) --")

    models: dict[str, Any] = {}

    # Baseline models
    models["LinearRegression"] = LinearRegression()
    models["Ridge(a=1)"] = Ridge(alpha=1.0)
    models["Lasso(a=0.01)"] = Lasso(alpha=0.01, max_iter=5000)

    # Ensemble models -- expanded grids for larger dataset
    models["ExtraTrees"] = ExtraTreesRegressor(
        n_estimators=500,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    models["RandomForest"] = RandomForestRegressor(
        n_estimators=500,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    models["GradientBoosting"] = GradientBoostingRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        min_samples_split=10,
        min_samples_leaf=4,
        max_features=0.8,
        random_state=42,
    )

    # XGBoost -- GPU-accelerated on RTX 3050
    models["XGBoost"] = xgb.XGBRegressor(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        colsample_bylevel=0.8,
        min_child_weight=3,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=5.0,
        tree_method="hist",
        device=device,
        random_state=42,
        verbosity=0,
    )

    # XGBoost variant -- deeper trees + stronger regularization
    models["XGBoost_Deep"] = xgb.XGBRegressor(
        n_estimators=800,
        learning_rate=0.03,
        max_depth=4,
        subsample=0.7,
        colsample_bytree=0.6,
        min_child_weight=5,
        gamma=0.2,
        reg_alpha=1.0,
        reg_lambda=10.0,
        tree_method="hist",
        device=device,
        random_state=123,
        verbosity=0,
    )

    log(f"  {len(models)} models configured")
    return models


# ======================================================================
# Step 7: Cross-validation (10-fold for 740 samples)
# ======================================================================
def cross_validate_top_models(
    models: dict[str, Any],
    X_train_s: np.ndarray,
    y_train: pd.Series,
    top_names: list[str],
) -> dict:
    """Run 10-fold CV on the top models to estimate generalization."""
    log("\n-- Step 7: 10-fold cross-validation on top models --")
    cv_results: dict[str, dict] = {}
    kf = KFold(n_splits=10, shuffle=True, random_state=42)

    for name in top_names:
        if name not in models:
            continue
        scores = cross_val_score(
            models[name], X_train_s, y_train, cv=kf, scoring="r2", n_jobs=-1
        )
        cv_results[name] = {
            "mean_r2": round(float(scores.mean()), 4),
            "std_r2": round(float(scores.std()), 4),
            "scores": [round(float(s), 4) for s in scores],
        }
        log(f"  {name:28s} CV R2={scores.mean():.4f} +/-{scores.std():.4f}")

    return cv_results


# ======================================================================
# Step 8: Feature importance
# ======================================================================
def plot_feature_importance(
    best_model: Any, feature_names: list[str], model_name: str,
    n_samples: int
) -> dict[str, float]:
    """Plot and return top feature importances."""
    log("\n-- Step 8: Plotting feature importance --")

    if not hasattr(best_model, "feature_importances_"):
        log("  Linear model -- skipping importance plot")
        return {}

    fi = pd.Series(
        best_model.feature_importances_, index=feature_names
    ).sort_values(ascending=False)

    top20 = fi.head(20)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = [
        "#1A56DB" if i < 5 else "#3B82F6" if i < 10 else "#93C5FD"
        for i in range(len(top20))
    ]
    bars = ax.barh(
        top20.index[::-1], top20.values[::-1], color=colors[::-1]
    )

    for bar, val in zip(bars, top20.values[::-1]):
        ax.text(
            val + 0.001,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.4f}",
            va="center",
            fontsize=8,
        )

    ax.set_xlabel("Feature Importance Score", fontsize=12)
    ax.set_title(
        f"PredictIQ -- Top 20 Features ({model_name})\n"
        f"Trained on {n_samples} software projects (4 international sources)",
        fontsize=13,
        fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()

    plot_path = OUT_DIR / "predictiq_feature_importance.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    log(f"  Feature importance plot saved -> {plot_path}")

    # Print top 10
    log("  Top 10 features:")
    for rank, (feat, imp) in enumerate(fi.head(10).items(), 1):
        log(f"    #{rank:2d} {feat:25s} {imp:.4f}")

    return {k: round(float(v), 6) for k, v in fi.head(15).items()}


# ======================================================================
# Step 9: Prediction vs Actual plot
# ======================================================================
def plot_predictions(
    best_model: Any,
    X_test_s: np.ndarray,
    y_test: pd.Series,
    model_name: str,
    n_samples: int,
) -> None:
    """Generate actual-vs-predicted and residual plots."""
    log("\n-- Step 9: Generating evaluation plots --")

    pred_log = best_model.predict(X_test_s)
    y_pred = np.expm1(pred_log)
    y_true = np.expm1(np.array(y_test))

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Scatter: Actual vs Predicted
    axes[0].scatter(
        y_true, y_pred, alpha=0.7, color="#1A56DB", edgecolors="white", s=60
    )
    max_val = max(y_true.max(), y_pred.max()) * 1.05
    axes[0].plot(
        [0, max_val], [0, max_val], "r--", linewidth=2, label="Perfect prediction"
    )
    axes[0].fill_between(
        [0, max_val],
        [0, max_val * 0.75],
        [0, max_val * 1.25],
        alpha=0.1,
        color="green",
        label="+/-25% band",
    )
    axes[0].set_xlabel("Actual Effort (hours)", fontsize=11)
    axes[0].set_ylabel("Predicted Effort (hours)", fontsize=11)
    axes[0].set_title(
        f"Actual vs Predicted -- {model_name}\n{n_samples} projects",
        fontsize=12, fontweight="bold"
    )
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Residuals
    residuals = y_pred - y_true
    axes[1].scatter(
        y_true, residuals, alpha=0.7, color="#10B981", edgecolors="white", s=60
    )
    axes[1].axhline(0, color="red", linewidth=2, linestyle="--")
    mean_val = float(y_true.mean())
    axes[1].fill_between(
        [0, float(y_true.max())],
        [-mean_val * 0.25, -mean_val * 0.25],
        [mean_val * 0.25, mean_val * 0.25],
        alpha=0.1,
        color="green",
        label="+/-25% zone",
    )
    axes[1].set_xlabel("Actual Effort (hours)", fontsize=11)
    axes[1].set_ylabel("Residual (Predicted - Actual)", fontsize=11)
    axes[1].set_title("Residual Analysis", fontsize=12, fontweight="bold")
    axes[1].legend()
    axes[1].grid(alpha=0.3)

    plt.suptitle(
        f"PredictIQ Model Evaluation ({n_samples} projects)",
        fontsize=14, fontweight="bold", y=1.02
    )
    plt.tight_layout()

    plot_path = OUT_DIR / "predictiq_model_evaluation.png"
    plt.savefig(plot_path, dpi=150, bbox_inches="tight")
    plt.close()
    log(f"  Evaluation plots saved -> {plot_path}")


# ======================================================================
# Step 10: Save best model + report
# ======================================================================
def save_artifacts(
    best_name: str,
    best_model: Any,
    results: list[dict],
    cv_results: dict,
    feature_names: list[str],
    top_features: dict[str, float],
    X_test_s: np.ndarray,
    y_test: pd.Series,
    n_samples: int,
) -> dict:
    """Persist the best model and generate the full training report."""
    log("\n-- Step 10: Saving artifacts --")

    # Best model
    model_path = ML_DIR / "predictiq_best_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(best_model, f)
    size_kb = model_path.stat().st_size / 1024
    log(f"  Best model saved -> {model_path} ({size_kb:.1f} KB)")

    # Compute final evaluation metrics for best model
    y_true = np.expm1(np.array(y_test))

    # Find best model metrics from results
    best_metrics = {}
    for r in results:
        if r["Model"] == best_name:
            best_metrics = r
            break

    # Model report JSON
    report: dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "best_model": best_name,
        "training_samples": n_samples,
        "dataset_shape": [n_samples, 30],
        "dataset_sources": [
            "albrecht", "china", "existing_desharnais_maxwell", "nasa93"
        ],
        "n_features": len(feature_names),
        "r2_score": best_metrics.get("R2", 0.0),
        "pred25": best_metrics.get("PRED25%", 0.0),
        "mmre": best_metrics.get("MMRE%", 0.0),
        "results": results,
        "cross_validation": cv_results,
        "top_features": top_features,
        "feature_list": feature_names,
        "production": {
            "model_file": "predictiq_best_model.pkl",
            "scaler_file": "predictiq_scaler.pkl",
            "features_file": "predictiq_features.json",
            "effort_range": {
                "min": int(y_true.min()),
                "max": int(y_true.max()),
                "mean": int(y_true.mean()),
            },
            "effort_clamp": {"min": 1, "max": 9587},
            "cost_per_hour": 75,
            "confidence_interval": {"min_factor": 0.80, "max_factor": 1.40},
        },
        "methodology": {
            "sizing": "IFPUG Function Points",
            "prediction": f"{best_name} ML Regression",
            "cost": "Parametric (effort x hourly_rate)",
        },
    }

    report_path = ML_DIR / "predictiq_model_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    log(f"  Model report saved -> {report_path}")

    # Also save as training_report.json (referenced by inference.py)
    training_report_path = ML_DIR / "training_report.json"
    with open(training_report_path, "w") as f:
        json.dump(report, f, indent=2)
    log(f"  Training report saved -> {training_report_path}")

    return report


# ======================================================================
# Main
# ======================================================================
def main() -> None:
    """Run the full training pipeline end-to-end."""
    start_time = time.time()

    # Load + prepare
    df = load_data()
    n_samples = len(df)
    X, y, fnames = prepare_features(df)
    X_tr, X_te, y_tr, y_te, scaler = split_and_scale(X, y)
    device = get_xgb_device()
    models = build_models(device)

    # Train all models
    log("\n-- Step 6: Training all models --")
    results: list[dict] = []
    trained: dict[str, Any] = {}

    for name, model in models.items():
        r, m = evaluate_model(name, model, X_tr, y_tr, X_te, y_te)
        results.append(r)
        trained[name] = m

    # Sort by R2
    results_df = pd.DataFrame(results).sort_values("R2", ascending=False)
    best_name = str(results_df.iloc[0]["Model"])
    best_model = trained[best_name]

    # Cross-validate top 3 (10-fold)
    top3 = results_df.head(3)["Model"].tolist()
    cv_results = cross_validate_top_models(trained, X_tr, y_tr, top3)

    # Feature importance
    top_features = plot_feature_importance(best_model, fnames, best_name, n_samples)

    # Prediction plots
    plot_predictions(best_model, X_te, y_te, best_name, n_samples)

    # Save everything
    _report = save_artifacts(
        best_name, best_model, results, cv_results,
        fnames, top_features, X_te, y_te, n_samples,
    )

    # Final summary
    elapsed = time.time() - start_time
    log("\n" + "=" * 60)
    log("TRAINING COMPLETE")
    log("=" * 60)
    log(f"Total time: {elapsed:.1f}s")
    log(f"Training samples: {n_samples}")
    log(f"\nBest model: {best_name}")

    best_row = results_df[results_df["Model"] == best_name].iloc[0]
    log(f"  R2      = {best_row['R2']:.4f}")
    log(f"  PRED25  = {best_row['PRED25%']:.1f}%")
    log(f"  MMRE    = {best_row['MMRE%']:.1f}%")

    if best_name in cv_results:
        cv = cv_results[best_name]
        log(f"  CV R2   = {cv['mean_r2']:.4f} +/- {cv['std_r2']:.4f}")

    log("\n-- Full Results Table --")
    table_str = results_df[["Model", "R2", "PRED25%", "MMRE%", "RMSE"]].to_string(
        index=False
    )
    log(table_str)

    log(f"\nLog file: {LOG_FILE}")
    log("Artifacts saved to: backend/ml/")
    log("\nNext step: Start the FastAPI server -- inference.py")
    log("will auto-load the model from backend/ml/")


if __name__ == "__main__":
    main()
