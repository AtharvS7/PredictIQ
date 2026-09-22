"""Provisional Itemlet research; unresolved target provenance forbids promotion."""
import argparse
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler

from ml.acquire_research import ITEMLET
from ml.model_comparison import compare_predictions
from ml.text_effort import split_projects
from ml.train_research import metrics

FEATURES = ['text', 'story_points', 'issuetype_name', 'priority_name']


def load_tasks(path):
    with Path(path).open('rb') as source:
        if hashlib.file_digest(source, 'sha256').hexdigest() != ITEMLET[2]:
            raise ValueError('Unreviewed Itemlet snapshot')
    columns = ['issue_key', 'project_key', 'issue_summary', 'story_points', 'issuetype_name',
               'priority_name', 'created', 'resolutiondate', 'status_statusCategory_name',
               'Total Time Logged (hours)']
    cohorts = []
    total = 0
    for data in pd.read_csv(path, usecols=columns, chunksize=25000, dtype=str):
        total += len(data)
        data['hours'] = pd.to_numeric(data['Total Time Logged (hours)'], errors='coerce')
        start = pd.to_datetime(data.created, errors='coerce', utc=True, format='mixed')
        end = pd.to_datetime(data.resolutiondate, errors='coerce', utc=True, format='mixed')
        data['text'] = data.issue_summary.fillna('').str.replace(r'\s+', ' ', regex=True).str.strip()
        valid = (data.hours.gt(0) & np.isfinite(data.hours) & start.notna() & end.ge(start)
                 & data.status_statusCategory_name.str.casefold().eq('done') & data.text.str.len().ge(10)
                 & data.project_key.notna() & data.issue_key.notna())
        cohorts.append(data.loc[valid].copy())
    frame = pd.concat(cohorts, ignore_index=True)
    eligible = len(frame)
    # Remove all repeated summaries and IDs across projects before partitioning.
    repeats = frame.text.str.casefold().duplicated(keep=False) | frame.issue_key.duplicated(keep=False)
    frame = frame.loc[~repeats].copy()
    frame['story_points'] = pd.to_numeric(frame.story_points, errors='coerce')
    frame.loc[~np.isfinite(frame.story_points) | frame.story_points.lt(0), 'story_points'] = np.nan
    for column in ['issuetype_name', 'priority_name']:
        frame[column] = frame[column].fillna('unknown')
    frame = frame.rename(columns={'project_key': 'project', 'issue_key': 'id'})
    return frame[FEATURES + ['project', 'id', 'hours']], {
        'raw_issues': total, 'eligible_before_deduplication': eligible,
        'excluded_duplicate_rows': int(repeats.sum()), 'eligible_tasks': len(frame),
        'projects': int(frame.project.nunique())}


def candidates():
    numeric = make_pipeline(SimpleImputer(strategy='median', add_indicator=True),
                            FunctionTransformer(np.log1p, validate=True), StandardScaler())
    return {f'ridge_{alpha}_text_{text}': TransformedTargetRegressor(
        regressor=make_pipeline(ColumnTransformer([
            ('points', clone(numeric), ['story_points']),
            ('kind', OneHotEncoder(handle_unknown='ignore'), ['issuetype_name', 'priority_name']),
        ] + ([('text', TfidfVectorizer(max_features=10000, min_df=3, sublinear_tf=True), 'text')] if text else [])),
                               Ridge(alpha=alpha, solver='lsqr')),
        func=np.log, inverse_func=np.exp)
        for alpha in [10., 100.] for text in [False, True]}


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Never overwrite experiment evidence')
    tasks, intake = load_tasks(source)
    train, calibration, test = split_projects(tasks)
    if train.project.nunique() < 4 or min(len(calibration), len(test)) < 100:
        raise ValueError('Insufficient independent project cohorts')
    scores = {}
    models = candidates()
    for name, estimator in models.items():
        folds = []
        for fit, validation in GroupKFold(4).split(train, groups=train.project):
            model = clone(estimator).fit(train.iloc[fit][FEATURES], train.iloc[fit].hours)
            folds.append(metrics(train.iloc[validation].hours, model.predict(train.iloc[validation][FEATURES])))
        scores[name] = {'folds': folds, 'mean_rmsle': float(np.mean([fold['rmsle'] for fold in folds]))}
    winner = min(scores, key=lambda name: scores[name]['mean_rmsle'])
    model = clone(models[winner]).fit(train[FEATURES], train.hours)
    prediction = model.predict(test[FEATURES])
    baseline = DummyRegressor(strategy='median').fit(np.zeros((len(train), 1)), train.hours)
    baseline_prediction = baseline.predict(np.zeros((len(test), 1)))
    report = {'schema': 'itemlet-provisional-research-v1', 'intake': intake, 'features': FEATURES,
              'source_sha256': ITEMLET[2], 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'split_counts': {name: {'tasks': len(frame), 'projects': int(frame.project.nunique())}
                               for name, frame in zip(['train', 'calibration', 'test'], [train, calibration, test])},
              'project_partitions': {name: sorted(frame.project.unique().tolist())
                                     for name, frame in zip(['train', 'calibration', 'test'], [train, calibration, test])},
              'selected': winner, 'development_cv': scores, 'test': metrics(test.hours, prediction),
              'baseline': metrics(test.hours, baseline_prediction),
              'paired': compare_predictions(test.hours, prediction, baseline_prediction, test.project),
              'production_approved': False,
              'limitations': ['Target provenance unresolved: source dictionary and CSV disagree',
                              'Snapshot summaries and story points may have changed after planning',
                              'Project separation does not prove organization or temporal independence',
                              'Task hours are not complete-project effort or currency cost',
                              'Calibration partition reserved; no calibrated interval or release claim']}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'candidate.pkl').write_bytes(pickle.dumps(model))
    report['model_sha256'] = hashlib.sha256((output / 'candidate.pkl').read_bytes()).hexdigest()
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    test[['id', 'project', 'hours']].assign(predicted_hours=prediction).to_csv(output / 'test_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    report = run(**vars(parser.parse_args()))
    print(json.dumps({key: report[key] for key in ['intake', 'split_counts', 'selected', 'test', 'baseline',
                                                  'paired', 'production_approved']}, indent=2))
