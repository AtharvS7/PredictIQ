"""Unit and integration tests for PredictIQ evaluation harness (CP07).

Tests:
1. Dataset loading and schema assertions.
2. LeaveOneSourceOutSplitter fold integrity and strict disjointness.
3. RepeatedGroupedKFoldSplitter group separation.
4. Evaluation metrics vs hand-calculated references.
5. Baseline predictors fitting, prediction, and positive-finite outputs.
6. LogLinearBaseline handling of missing or optional duration.
7. Macro-averaging aggregation.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from backend.ml.eval.baselines import (
    AlbrechtNominalPredictor,
    COCOMONominalPredictor,
    HuberPowerLawBaseline,
    LogLinearBaseline,
    MedianDummyPredictor,
    MedianProductivityPredictor,
    PowerLawBaseline,
)
from backend.ml.eval.metrics import (
    compute_metrics,
    log_bias,
    macro_average_metrics,
    mae,
    mdape,
    mdmre,
    mmre,
    pred25,
    pred30,
    pred50,
    pred_k,
    r2_score,
    rmse,
    rmsle,
)
from backend.ml.eval.protocol import (
    FoldSplit,
    LeaveOneSourceOutSplitter,
    RepeatedGroupedKFoldSplitter,
    load_dataset,
)


@pytest.fixture(scope="module")
def projects_df() -> pd.DataFrame:
    """Fixture providing loaded projects_v2 dataset."""
    return load_dataset()


# ---------------------------------------------------------------------------
# Protocol & Splitter Tests
# ---------------------------------------------------------------------------


def test_load_dataset_success_and_validation():
    """Verify load_dataset successfully loads and validates 915 rows."""
    df = load_dataset()
    assert len(df) == 915
    assert "project_id" in df.columns
    assert "source" in df.columns
    assert "size_value" in df.columns
    assert "effort_hours" in df.columns
    assert (df["size_value"] > 0).all()
    assert (df["effort_hours"] > 0).all()


def test_load_dataset_nonexistent_path():
    """Verify load_dataset raises FileNotFoundError for missing path."""
    with pytest.raises(FileNotFoundError):
        load_dataset("non_existent_path_xyz123.csv")


def test_loso_folds_strictly_disjoint(projects_df: pd.DataFrame):
    """Test that LeaveOneSourceOutSplitter yields 6 strictly disjoint folds."""
    splitter = LeaveOneSourceOutSplitter()
    folds = list(splitter.split_df(projects_df))

    assert len(folds) == 6, f"Expected 6 folds, got {len(folds)}"

    expected_counts = {
        "china": 499,
        "kitchenham": 145,
        "att_aptness": 104,
        "desharnais": 81,
        "maxwell": 62,
        "albrecht": 24,
    }

    all_test_ids: list[str] = []

    for fold in folds:
        source = fold.fold_name
        assert source in expected_counts, f"Unexpected source {source}"
        assert len(fold.test_df) == expected_counts[source], (
            f"Source {source} expected {expected_counts[source]} rows, got {len(fold.test_df)}"
        )
        assert len(fold.train_df) + len(fold.test_df) == 915

        # Source separation
        assert (fold.test_df["source"] == source).all()
        assert (fold.train_df["source"] != source).all()

        # Strict ID disjointness
        train_ids = set(fold.train_project_ids)
        test_ids = set(fold.test_project_ids)
        assert train_ids.isdisjoint(test_ids), f"Fold {source} has overlapping project IDs!"

        all_test_ids.extend(fold.test_project_ids)

    # Across all 6 folds, every project is tested exactly once
    assert len(all_test_ids) == 915
    assert len(set(all_test_ids)) == 915


def test_fold_split_verify_disjoint_raises_on_leakage():
    """Verify FoldSplit.verify_disjoint catches artificial ID leakage."""
    split = FoldSplit(
        fold_name="test_leak",
        train_indices=np.array([0, 1]),
        test_indices=np.array([2, 3]),
        train_project_ids=["p1", "p2", "leak_id"],
        test_project_ids=["p3", "leak_id"],
        train_df=pd.DataFrame(),
        test_df=pd.DataFrame(),
    )
    with pytest.raises(ValueError, match="Data leakage detected"):
        split.verify_disjoint()


def test_loso_sklearn_split_interface(projects_df: pd.DataFrame):
    """Verify standard scikit-learn split(X, y, groups) interface."""
    splitter = LeaveOneSourceOutSplitter()
    n_splits = splitter.get_n_splits(X=projects_df)
    assert n_splits == 6

    splits = list(splitter.split(projects_df, groups=projects_df["source"]))
    assert len(splits) == 6

    for train_idx, test_idx in splits:
        assert len(train_idx) + len(test_idx) == 915
        assert len(np.intersect1d(train_idx, test_idx)) == 0


def test_repeated_grouped_kfold_disjoint():
    """Verify RepeatedGroupedKFoldSplitter partitions groups without leakage."""
    groups = ["g1", "g1", "g2", "g2", "g3", "g3", "g4", "g4", "g5", "g5", "g6", "g6"]
    X = np.arange(len(groups))

    splitter = RepeatedGroupedKFoldSplitter(n_splits=3, n_repeats=2, random_state=42)
    assert splitter.get_n_splits() == 6

    splits = list(splitter.split(X, groups=groups))
    assert len(splits) == 6

    for train_idx, test_idx in splits:
        train_g = set(groups[i] for i in train_idx)
        test_g = set(groups[i] for i in test_idx)
        assert train_g.isdisjoint(test_g), f"Group leakage detected: {train_g.intersection(test_g)}"


# ---------------------------------------------------------------------------
# Metric Tests (Hand-Computed Reference Cases)
# ---------------------------------------------------------------------------


def test_metrics_hand_computed_case():
    """Test metric functions against analytically hand-computed vectors.

    y_true = [100.0, 200.0, 300.0, 400.0]
    y_pred = [110.0, 180.0, 330.0, 500.0]

    Errors (pred - true) = [10, -20, 30, 100]
    Abs errors = [10, 20, 30, 100]
    MAE = (10 + 20 + 30 + 100) / 4 = 40.0
    Squared errors = [100, 400, 900, 10000] = 11400
    MSE = 11400 / 4 = 2850
    RMSE = sqrt(2850) ≈ 53.38539199...

    y_true mean = 250.0
    SS_tot = (100-250)^2 + (200-250)^2 + (300-250)^2 + (400-250)^2 = 22500 + 2500 + 2500 + 22500 = 50000
    SS_res = 11400
    R^2 = 1 - 11400 / 50000 = 1 - 0.228 = 0.772

    MRE = [10/100, 20/200, 30/300, 100/400] = [0.10, 0.10, 0.10, 0.25]
    MdMRE = median([0.10, 0.10, 0.10, 0.25]) = 0.10
    MdAPE = 10.0%
    MMRE = (0.10 + 0.10 + 0.10 + 0.25) / 4 * 100 = 13.75%

    PRED(10) = 3 / 4 * 100 = 75.0%
    PRED(25) = 4 / 4 * 100 = 100.0%
    PRED(30) = 4 / 4 * 100 = 100.0%
    PRED(5)  = 0 / 4 * 100 = 0.0%
    """
    y_t = np.array([100.0, 200.0, 300.0, 400.0])
    y_p = np.array([110.0, 180.0, 330.0, 500.0])

    assert mae(y_t, y_p) == pytest.approx(40.0, abs=1e-6)
    assert rmse(y_t, y_p) == pytest.approx(math.sqrt(2850.0), abs=1e-6)
    assert r2_score(y_t, y_p) == pytest.approx(0.772, abs=1e-6)

    assert mdmre(y_t, y_p, as_percentage=False) == pytest.approx(0.10, abs=1e-6)
    assert mdape(y_t, y_p) == pytest.approx(10.0, abs=1e-6)
    assert mmre(y_t, y_p, as_percentage=True) == pytest.approx(13.75, abs=1e-6)

    assert pred_k(y_t, y_p, k=0.10, as_percentage=True) == pytest.approx(75.0, abs=1e-6)
    assert pred25(y_t, y_p) == pytest.approx(100.0, abs=1e-6)
    assert pred30(y_t, y_p) == pytest.approx(100.0, abs=1e-6)
    assert pred50(y_t, y_p) == pytest.approx(100.0, abs=1e-6)
    assert pred_k(y_t, y_p, k=0.05, as_percentage=True) == pytest.approx(0.0, abs=1e-6)

    # RMSLE and Log-bias hand calculation
    log_diffs = np.log(y_p) - np.log(y_t)
    expected_rmsle = math.sqrt(np.mean(log_diffs**2))
    expected_log_bias = float(np.mean(log_diffs))
    assert rmsle(y_t, y_p) == pytest.approx(expected_rmsle, abs=1e-6)
    assert log_bias(y_t, y_p) == pytest.approx(expected_log_bias, abs=1e-6)


def test_metrics_perfect_predictions():
    """Test metrics on perfectly accurate predictions."""
    y = np.array([50.0, 100.0, 200.0, 500.0])
    m = compute_metrics(y_true=y, y_pred=y)

    assert m["r2"] == pytest.approx(1.0, abs=1e-6)
    assert m["rmse"] == pytest.approx(0.0, abs=1e-6)
    assert m["mae"] == pytest.approx(0.0, abs=1e-6)
    assert m["mdmre"] == pytest.approx(0.0, abs=1e-6)
    assert m["mdape"] == pytest.approx(0.0, abs=1e-6)
    assert m["pred25"] == pytest.approx(100.0, abs=1e-6)
    assert m["pred30"] == pytest.approx(100.0, abs=1e-6)
    assert m["pred50"] == pytest.approx(100.0, abs=1e-6)
    assert m["rmsle"] == pytest.approx(0.0, abs=1e-6)
    assert m["log_bias"] == pytest.approx(0.0, abs=1e-6)
    assert m["mmre"] == pytest.approx(0.0, abs=1e-6)
    assert m["sa"] == pytest.approx(100.0, abs=1e-6)


def test_metrics_input_validation():
    """Verify metrics raise appropriate errors for invalid inputs."""
    with pytest.raises(ValueError, match="empty"):
        mae([], [])

    with pytest.raises(ValueError, match="Length mismatch"):
        mae([1, 2], [1])

    with pytest.raises(ValueError, match="NaN or infinite"):
        mae([1.0, np.nan], [1.0, 2.0])

    with pytest.raises(ValueError, match="strictly positive"):
        mdmre([-5.0, 10.0], [5.0, 10.0])


def test_macro_average_metrics():
    """Verify macro-average computes arithmetic mean across fold metrics."""
    f1 = {"mae": 10.0, "mdape": 20.0, "r2": 0.5}
    f2 = {"mae": 20.0, "mdape": 40.0, "r2": 0.7}
    res = macro_average_metrics([f1, f2])

    assert res["mae"] == pytest.approx(15.0)
    assert res["mdape"] == pytest.approx(30.0)
    assert res["r2"] == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Baseline Predictor Tests
# ---------------------------------------------------------------------------


def test_median_dummy_predictor(projects_df: pd.DataFrame):
    """Test MedianDummyPredictor predicts constant median of training fold."""
    train_df = projects_df.iloc[:700]
    test_df = projects_df.iloc[700:]

    model = MedianDummyPredictor()
    model.fit(train_df, train_df["effort_hours"])
    preds = model.predict(test_df)

    expected_median = float(np.median(train_df["effort_hours"]))
    assert len(preds) == len(test_df)
    assert np.allclose(preds, expected_median)
    assert (preds > 0).all()
    assert np.isfinite(preds).all()


def test_median_productivity_predictor(projects_df: pd.DataFrame):
    """Test MedianProductivityPredictor computes P * Size."""
    train_df = projects_df.iloc[:700]
    test_df = projects_df.iloc[700:]

    model = MedianProductivityPredictor()
    model.fit(train_df, train_df["effort_hours"])
    preds = model.predict(test_df)

    assert len(preds) == len(test_df)
    assert (preds > 0).all()
    assert np.isfinite(preds).all()

    # Manual verification
    train_prod = train_df["effort_hours"] / train_df["size_value"]
    expected_prod = float(np.median(train_prod))
    expected_preds = expected_prod * test_df["size_value"].to_numpy()
    assert np.allclose(preds, expected_preds)


def test_albrecht_nominal_predictor(projects_df: pd.DataFrame):
    """Test AlbrechtNominalPredictor fits E = a * S^b via log-log regression."""
    train_df = projects_df.iloc[:700]
    test_df = projects_df.iloc[700:]

    model = AlbrechtNominalPredictor()
    model.fit(train_df, train_df["effort_hours"])
    preds = model.predict(test_df)

    assert len(preds) == len(test_df)
    assert (preds > 0).all()
    assert np.isfinite(preds).all()
    assert model.a_ is not None and model.a_ > 0
    assert model.b_ is not None and model.b_ > 0

    # Aliases
    assert COCOMONominalPredictor is AlbrechtNominalPredictor
    assert PowerLawBaseline is AlbrechtNominalPredictor


def test_log_linear_baseline_with_and_without_duration(projects_df: pd.DataFrame):
    """Test LogLinearBaseline with duration present and missing."""
    train_df = projects_df.iloc[:700]
    test_df = projects_df.iloc[700:]

    # With duration
    model = LogLinearBaseline()
    model.fit(train_df, train_df["effort_hours"])
    preds = model.predict(test_df)
    assert len(preds) == len(test_df)
    assert (preds > 0).all()
    assert np.isfinite(preds).all()

    # Without duration column
    df_no_dur = projects_df[["size_value", "effort_hours"]]
    train_no_dur = df_no_dur.iloc[:700]
    test_no_dur = df_no_dur.iloc[700:]

    model2 = LogLinearBaseline()
    model2.fit(train_no_dur, train_no_dur["effort_hours"])
    preds2 = model2.predict(test_no_dur)
    assert len(preds2) == len(test_no_dur)
    assert (preds2 > 0).all()
    assert np.isfinite(preds2).all()


def test_huber_power_law_baseline(projects_df: pd.DataFrame):
    """Test HuberPowerLawBaseline fits robust power law."""
    train_df = projects_df.iloc[:700]
    test_df = projects_df.iloc[700:]

    model = HuberPowerLawBaseline()
    model.fit(train_df, train_df["effort_hours"])
    preds = model.predict(test_df)

    assert len(preds) == len(test_df)
    assert (preds > 0).all()
    assert np.isfinite(preds).all()


def test_all_baselines_loso_integration(projects_df: pd.DataFrame):
    """Test running all baselines through 1 fold of LOSO."""
    splitter = LeaveOneSourceOutSplitter()
    first_fold = next(splitter.split_df(projects_df))

    baselines = [
        MedianDummyPredictor(),
        MedianProductivityPredictor(),
        AlbrechtNominalPredictor(),
        LogLinearBaseline(),
        HuberPowerLawBaseline(),
    ]

    for model in baselines:
        model.fit(first_fold.train_df, first_fold.train_df["effort_hours"])
        preds = model.predict(first_fold.test_df)
        metrics = compute_metrics(first_fold.test_df["effort_hours"], preds)

        assert np.isfinite(metrics["mae"])
        assert np.isfinite(metrics["rmse"])
        assert np.isfinite(metrics["mdape"])
        assert 0.0 <= metrics["pred25"] <= 100.0
        assert 0.0 <= metrics["pred30"] <= 100.0
