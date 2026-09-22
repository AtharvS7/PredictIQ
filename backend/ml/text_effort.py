"""Project-held-out task-text benchmark on JOSSE, not production approval.

Uses description text only; no comments/activity counts or task/project IDs.
JIRA effort seconds are explicitly converted to person-hours. Source snapshots
do not establish planning-time text, so this is retrospective research evidence.
"""
import argparse
import hashlib
import json
import math
import pickle
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, GroupShuffleSplit
from sklearn.pipeline import make_pipeline

from ml.model_comparison import compare_predictions
from ml.train_research import metrics

SEED = 20260922


def load_josse(path):
    uri = Path(path).resolve().as_uri() + '?mode=ro'
    with sqlite3.connect(uri, uri=True) as connection:
        connection.execute('PRAGMA trusted_schema=OFF')
        connection.execute('PRAGMA query_only=ON')
        frame = pd.read_sql_query('SELECT id, corpus, expert_estimated_effort, actual_effort FROM "case"', connection)
    initial = len(frame)
    frame['project'] = frame.id.str.extract(r'^([A-Za-z][A-Za-z0-9_]*)-\d+$', expand=False)
    frame['text'] = frame.corpus.fillna('').map(lambda value: re.sub(r'\s+', ' ', value).strip())
    frame['hours'] = pd.to_numeric(frame.actual_effort, errors='raise') / 3600
    frame['expert_hours'] = pd.to_numeric(frame.expert_estimated_effort, errors='coerce') / 3600
    valid = frame.project.notna() & frame.text.str.len().ge(10) & np.isfinite(frame.hours) & frame.hours.gt(0)
    invalid = int((~valid).sum())
    frame = frame.loc[valid].copy()
    if frame.id.duplicated().any():
        raise ValueError('Duplicate issue identity')
    # Remove repeated normalized descriptions entirely, before any group split.
    # Keeping a duplicate under another project would contaminate held-out text.
    duplicates = frame.text.str.casefold().duplicated(keep=False)
    repeated = int(duplicates.sum())
    frame = frame.loc[~duplicates, ['id', 'project', 'text', 'hours', 'expert_hours']].reset_index(drop=True)
    return frame, {'raw_tasks': initial, 'excluded_invalid': invalid, 'excluded_repeated_text': repeated,
                   'eligible_tasks': len(frame), 'projects': int(frame.project.nunique())}


def split_projects(frame):
    development, test = next(GroupShuffleSplit(n_splits=1, test_size=.2, random_state=SEED).split(frame, groups=frame.project))
    subset = frame.iloc[development]
    train, calibration = next(GroupShuffleSplit(n_splits=1, test_size=.25, random_state=SEED + 1).split(subset, groups=subset.project))
    return [frame.iloc[indices].copy() for indices in [development[train], development[calibration], test]]


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Use a new output directory; never overwrite experiment evidence')
    frame, intake = load_josse(source)
    train, calibration, test = split_projects(frame)
    if train.project.nunique() < 4 or min(len(calibration), len(test)) < 100:
        raise ValueError('Insufficient project-separated cohorts')
    models = {
        f'text_ridge_{alpha}': TransformedTargetRegressor(
            regressor=make_pipeline(TfidfVectorizer(max_features=15000, ngram_range=(1, 2),
                                                  min_df=3, sublinear_tf=True),
                                    Ridge(alpha=alpha, solver='lsqr')),
            func=np.log, inverse_func=np.exp)
        for alpha in [10, 100]
    }
    cv = {}
    for name, estimator in models.items():
        folds = []
        for fit, validation in GroupKFold(4).split(train, groups=train.project):
            model = clone(estimator).fit(train.iloc[fit].text, train.iloc[fit].hours)
            folds.append(metrics(train.iloc[validation].hours, model.predict(train.iloc[validation].text)))
        cv[name] = {'folds': folds, 'mean_rmsle': float(np.mean([fold['rmsle'] for fold in folds]))}
    winner = min(cv, key=lambda name: cv[name]['mean_rmsle'])
    model = clone(models[winner]).fit(train.text, train.hours)
    cal_prediction = model.predict(calibration.text)
    metrics(calibration.hours, cal_prediction)
    residuals = np.abs(np.log(calibration.hours) - np.log(cal_prediction))
    radius = float(np.sort(residuals)[math.ceil((len(residuals) + 1) * .9) - 1])
    prediction = model.predict(test.text)
    baseline_model = DummyRegressor(strategy='median').fit(np.zeros((len(train), 1)), train.hours)
    baseline = baseline_model.predict(np.zeros((len(test), 1)))
    expert = np.isfinite(test.expert_hours) & test.expert_hours.gt(0)
    report = {
        'schema': 'task-text-person-hours-research-v1', 'seed': SEED, 'features': ['task_description'],
        'target': 'logged_task_person_hours', 'intake': intake,
        'split_counts': {name: {'tasks': len(data), 'projects': int(data.project.nunique())}
                         for name, data in zip(['train', 'calibration', 'test'], [train, calibration, test])},
        'project_partitions': {name: sorted(data.project.unique().tolist())
                               for name, data in zip(['train', 'calibration', 'test'], [train, calibration, test])},
        'selected_model': winner, 'development_cv': cv,
        'test_metrics': metrics(test.hours, prediction), 'median_baseline': metrics(test.hours, baseline),
        'paired_comparison': compare_predictions(test.hours, prediction, baseline, test.project),
        'expert_subset': None,
        'interval': {'nominal': .9, 'log_radius': radius,
                     'coverage': float(np.mean((test.hours >= prediction * np.exp(-radius)) &
                                               (test.hours <= prediction * np.exp(radius)))),
                     'median_width_hours': float(np.median(prediction * (np.exp(radius) - np.exp(-radius))))},
        'production_approved': False,
        'source_sha256': hashlib.sha256(Path(source).read_bytes()).hexdigest(),
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'source_url': 'https://github.com/ml-see/josse', 'source_license': 'MIT; retain upstream notice',
        'limitations': ['No planning-time text history or chronological split available in source database',
                       'Project separation does not establish organization independence',
                       'Logged task effort is not complete-project cost; no automatic aggregation',
                       'Observed conformal coverage is not a guarantee under project shift',
                       'No prospective validation or modern private-project evidence'],
    }
    if expert.sum() >= 2:
        report['expert_subset'] = {
            'tasks': int(expert.sum()), 'model': metrics(test.loc[expert].hours, prediction[expert]),
            'human': metrics(test.loc[expert].hours, test.loc[expert].expert_hours),
            'paired': compare_predictions(test.loc[expert].hours, prediction[expert],
                                          test.loc[expert].expert_hours, test.loc[expert].project)}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'candidate.pkl').write_bytes(pickle.dumps(model))
    report['model_sha256'] = hashlib.sha256((output / 'candidate.pkl').read_bytes()).hexdigest()
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    # Descriptions stay in the source; output only IDs and quantitative evidence.
    test.drop(columns='text').assign(predicted_hours=prediction).to_csv(output / 'test_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    result = run(**vars(parser.parse_args()))
    print(json.dumps({k: result[k] for k in ['intake', 'split_counts', 'selected_model', 'test_metrics',
          'median_baseline', 'paired_comparison', 'expert_subset', 'interval', 'production_approved']}, indent=2))
