"""Research task-effort calibration with purged, chronological validation.

This estimates actual task hours from an existing human estimate. It is NOT a
document-to-project model and must never be silently substituted for one.
Run from backend: python -m ml.task_calibration SOURCE_DIRECTORY NEW_OUTPUT
"""
import argparse
import hashlib
import json
import math
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from ml.train_research import metrics

FEATURES = ['HoursEstimate', 'Category', 'SubCategory']
SEED = 20260918


class HumanEstimate(RegressorMixin, BaseEstimator):
    """The recorded planning estimate is a mandatory comparator."""
    def fit(self, x, y=None):
        return self

    def predict(self, x):
        return x.HoursEstimate.to_numpy(dtype=float)


def load_tasks(directory):
    directory = Path(directory)
    paths = [directory / 'Sip-task-info.csv', directory / 'est-act-dates.csv']
    observations = pd.read_csv(paths[0], encoding='cp1252')
    dates = pd.read_csv(paths[1])
    fields = FEATURES + ['TaskNumber', 'ProjectCode', 'StatusCode', 'HoursActual']
    for frame, columns in [(observations, fields), (dates, ['TaskNumber', 'EstimateOn', 'CompletedOn'])]:
        if not set(columns).issubset(frame.columns) or frame.TaskNumber.isna().any():
            raise ValueError('Missing task identity or source columns')
        for column in columns:
            if (frame.groupby('TaskNumber')[column].nunique(dropna=False) > 1).any():
                raise ValueError('Conflicting repeated task records')
    # Developer rows repeat TASK totals. Never sum HoursActual across them.
    tasks = observations[fields].drop_duplicates('TaskNumber').merge(
        dates[['TaskNumber', 'EstimateOn', 'CompletedOn']].drop_duplicates('TaskNumber'),
        on='TaskNumber', validate='one_to_one', how='left')
    counts = {'raw_developer_rows': len(observations), 'unique_tasks': len(tasks)}
    for column in ['HoursEstimate', 'HoursActual']:
        tasks[column] = pd.to_numeric(tasks[column], errors='raise')
    for column in ['EstimateOn', 'CompletedOn']:
        tasks[column] = pd.to_datetime(tasks[column], format='%d-%b-%y', errors='coerce', utc=True)
    valid = tasks.StatusCode.isin(['FINISHED', 'COMPLETED', 'RELEASED'])
    counts['excluded_noncompleted'] = int((~valid).sum())
    tasks = tasks.loc[valid].copy()
    valid = (np.isfinite(tasks[['HoursEstimate', 'HoursActual']]).all(axis=1)
             & (tasks[['HoursEstimate', 'HoursActual']] > 0).all(axis=1)
             & tasks[['EstimateOn', 'CompletedOn', 'Category', 'SubCategory', 'ProjectCode']].notna().all(axis=1)
             & (tasks.CompletedOn >= tasks.EstimateOn))
    counts['excluded_invalid_completed'] = int((~valid).sum())
    tasks = tasks.loc[valid].sort_values(['EstimateOn', 'TaskNumber']).reset_index(drop=True)
    counts['eligible_tasks'] = len(tasks)
    counts['project_codes'] = int(tasks.ProjectCode.nunique())
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return tasks, counts, hashes


def temporal_split(tasks):
    dates = sorted(tasks.EstimateOn.unique())
    if len(dates) < 20:
        raise ValueError('Insufficient distinct planning dates')
    cal_start, test_start = dates[int(len(dates) * .6)], dates[int(len(dates) * .8)]
    train = tasks[(tasks.EstimateOn < cal_start) & (tasks.CompletedOn < cal_start)]
    calibration = tasks[(tasks.EstimateOn >= cal_start) & (tasks.EstimateOn < test_start)
                        & (tasks.CompletedOn < test_start)]
    test = tasks[tasks.EstimateOn >= test_start]
    if min(map(len, [train, calibration, test])) < 20:
        raise ValueError('Insufficient purged temporal cohorts')
    return train, calibration, test


def candidates():
    numeric = make_pipeline(FunctionTransformer(np.log1p, validate=True), StandardScaler())
    prepare = ColumnTransformer([
        ('hours', numeric, ['HoursEstimate']),
        ('kind', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['Category', 'SubCategory']),
    ])
    result = {'human_estimate': HumanEstimate()}
    for alpha in [1, 10, 100]:
        result[f'log_ridge_{alpha}'] = TransformedTargetRegressor(
            regressor=make_pipeline(clone(prepare), Ridge(alpha=alpha)),
            func=np.log1p, inverse_func=np.expm1)
    for leaf in [7, 15]:
        result[f'log_boost_{leaf}'] = TransformedTargetRegressor(
            regressor=make_pipeline(clone(prepare), HistGradientBoostingRegressor(
                max_iter=150, max_leaf_nodes=leaf, min_samples_leaf=30,
                l2_regularization=10, early_stopping=False, random_state=SEED)),
            func=np.log1p, inverse_func=np.expm1)
    return result


def rolling_folds(train):
    """Disjoint validation windows; only already completed outcomes may fit."""
    dates = sorted(train.EstimateOn.unique())
    for start_fraction, end_fraction in [(.4, .6), (.6, .8), (.8, 1.0)]:
        start = dates[int(len(dates) * start_fraction)]
        fit = train[(train.EstimateOn < start) & (train.CompletedOn < start)]
        mask = train.EstimateOn >= start
        if end_fraction < 1:
            mask &= train.EstimateOn < dates[int(len(dates) * end_fraction)]
        validation = train[mask]
        if fit.empty or validation.empty:
            raise ValueError('Insufficient completed outcomes for rolling validation')
        yield fit, validation


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Existing experiment cannot be overwritten')
    tasks, intake, hashes = load_tasks(source)
    train, calibration, test = temporal_split(tasks)
    models = candidates()
    scores = {}
    for name, estimator in models.items():
        fold_scores = []
        for fit, val in rolling_folds(train):
            model = clone(estimator).fit(fit[FEATURES], fit.HoursActual)
            fold_scores.append(metrics(val.HoursActual, model.predict(val[FEATURES])))
        scores[name] = {'folds': fold_scores, 'mean_mae': float(np.mean([v['mae_hours'] for v in fold_scores]))}
    winner = min(scores, key=lambda name: scores[name]['mean_mae'])
    model = clone(models[winner]).fit(train[FEATURES], train.HoursActual)
    cal_prediction = model.predict(calibration[FEATURES])
    metrics(calibration.HoursActual, cal_prediction)
    residual = np.abs(np.log1p(calibration.HoursActual) - np.log1p(cal_prediction))
    radius = float(np.sort(residual)[math.ceil((len(residual) + 1) * .9) - 1])
    prediction = model.predict(test[FEATURES])
    scores_test = metrics(test.HoursActual, prediction)
    baseline = metrics(test.HoursActual, test.HoursEstimate)
    lower = np.maximum(0, np.expm1(np.log1p(prediction) - radius))
    upper = np.expm1(np.log1p(prediction) + radius)
    slices = {}
    for key, cohort in test.groupby('ProjectCode'):
        indices = test.index.get_indexer(cohort.index)
        if len(cohort) >= 2:
            slices[str(key)] = metrics(cohort.HoursActual, prediction[indices])
    report = {'schema': 'task-human-estimate-calibration-research-v1', 'features': FEATURES,
              'target': 'actual_task_person_hours', 'seed': SEED, 'source_hashes': hashes,
              'intake': intake, 'split_counts': dict(zip(['train', 'calibration', 'test'], map(len, [train, calibration, test]))),
              'purged_tasks': len(tasks) - len(train) - len(calibration) - len(test),
              'selected_model': winner, 'development_cv': scores, 'future_test': scores_test,
              'human_baseline': baseline, 'test_by_project': slices,
              'interval': {'nominal': .9, 'log_radius': radius,
                           'coverage': float(np.mean((test.HoursActual >= lower) & (test.HoursActual <= upper))),
                           'median_width_hours': float(np.median(upper - lower))},
              'production_approved': False,
              'limitations': ['One organization, historical data; no modern cross-organization validation',
                              'Calibrates existing human task estimates; cannot infer project totals from documents',
                              'Category snapshots may have changed after initial planning',
                              'Public research data; production redistribution license unresolved',
                              'Tasks within projects are dependent; nominal conformal coverage is not guaranteed',
                              'Task intervals must not be summed as a calibrated project interval'],
              'source_url': 'https://github.com/Derek-Jones/SiP_dataset'}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'candidate.pkl').write_bytes(pickle.dumps(model))
    report['model_sha256'] = hashlib.sha256((output / 'candidate.pkl').read_bytes()).hexdigest()
    report['code_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    test[['TaskNumber', 'ProjectCode', 'HoursEstimate', 'HoursActual']].assign(
        predicted_hours=prediction, lower_hours=lower, upper_hours=upper).to_csv(output / 'test_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    result = run(**vars(parser.parse_args()))
    print(json.dumps({k: result[k] for k in ['intake', 'split_counts', 'purged_tasks', 'selected_model',
          'future_test', 'human_baseline', 'interval', 'production_approved']}, indent=2))
