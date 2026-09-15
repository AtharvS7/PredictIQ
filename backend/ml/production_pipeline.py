"""Prospective project-effort pipeline. NOT executed until the owner authorizes it.

Input: a local manifest of licensed CSV sources with the canonical schema below.
Output: immutable candidate bundle, evaluation and provenance; never auto-promotes.
Run later from backend: python -m ml.production_pipeline manifest.json output-directory
"""
import argparse
import hashlib
import json
import math
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ['size_fp', 'team_size', 'feature_count', 'integration_count', 'volatility_score', 'team_experience']
CATEGORICAL = ['project_type', 'complexity', 'methodology']
FEATURES = NUMERIC + CATEGORICAL
SCHEMA = 'predictiq-planning-inputs-v1'
SEED = 20260915


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_projects(manifest_path):
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    frames, provenance = [], []
    for source in manifest['sources']:
        if (source.get('schema') != SCHEMA or source.get('grain') != 'completed_project'
                or source.get('effort_unit') != 'person_hours' or source.get('rights_approved') is not True
                or not source.get('license_evidence') or not source.get('feature_parity_evidence')
                or source.get('features_recorded_at') != 'planning'):
            raise ValueError('Source requires licensed, planning-time project features and observed person-hours')
        path = (manifest_path.parent / source['path']).resolve()
        if not path.is_relative_to(manifest_path.parent) or digest(path) != source['sha256']:
            raise ValueError('Source path or checksum mismatch')
        frame = pd.read_csv(path)
        mapping = source.get('column_map', {})
        if len(set(mapping.values())) != len(mapping):
            raise ValueError('Ambiguous source column mapping')
        if mapping:
            if not set(mapping.values()).issubset(frame.columns):
                raise ValueError('Mapped source columns are missing')
            frame = frame.rename(columns={original: canonical for canonical, original in mapping.items()})
        if frame.columns.duplicated().any():
            raise ValueError('Duplicate canonical source columns')
        required = FEATURES + ['project_id', 'organization_id', 'effort_hours', 'partition', 'planning_date', 'completion_date']
        if not set(required).issubset(frame.columns):
            raise ValueError('Source missing canonical columns; do not invent missing observations')
        frame = frame[required].copy()
        frame['source'] = source['name']
        for column in ['planning_date', 'completion_date']:
            frame[column] = pd.to_datetime(frame[column], utc=True, errors='raise')
        if frame[['planning_date', 'completion_date']].isna().any().any() or (frame.completion_date < frame.planning_date).any():
            raise ValueError('Invalid project chronology')
        # Organization IDs must be globally stable across sources; do not prefix by source.
        if frame[['project_id', 'organization_id']].isna().any().any():
            raise ValueError('Missing project or organization identity')
        for column in ['project_id', 'organization_id']:
            frame[column] = frame[column].astype(str).str.strip()
            if frame[column].eq('').any():
                raise ValueError('Empty project or organization identity')
        for column in CATEGORICAL:
            frame[column] = frame[column].map(lambda value: value.strip() if isinstance(value, str) else value)
            if frame[column].dropna().map(lambda value: not isinstance(value, str) or not value).any():
                raise ValueError('Categories must be nonempty text')
        for column in NUMERIC + ['effort_hours']:
            frame[column] = pd.to_numeric(frame[column], errors='raise')
            present = frame[column].dropna()
            if not np.isfinite(present).all() or (present < 0).any():
                raise ValueError('Invalid numeric observation')
        if frame[['size_fp', 'effort_hours']].isna().any().any() or (frame[['size_fp', 'effort_hours']] <= 0).any().any():
            raise ValueError('Size and actual effort must be positive and observed')
        if not set(frame.partition).issubset({'train', 'calibration', 'external_test'}):
            raise ValueError('Explicit train/calibration/external_test partitions required')
        frames.append(frame)
        provenance.append({k: source[k] for k in ['name', 'sha256', 'license_evidence', 'feature_parity_evidence', 'schema']})
    if not frames:
        raise ValueError('No source datasets')
    data = pd.concat(frames, ignore_index=True)
    if data.project_id.duplicated().any():
        raise ValueError('Duplicate global project IDs')
    if (data.groupby('organization_id').partition.nunique() > 1).any():
        raise ValueError('Organization leakage between partitions')
    # Conservative protection against copied records with altered source identifiers.
    fingerprints = pd.util.hash_pandas_object(data[FEATURES + ['effort_hours']], index=False)
    if fingerprints.duplicated().any():
        raise ValueError('Repeated project observations require explicit deduplication')
    return data, provenance


def preprocessing():
    return ColumnTransformer([
        ('numeric', Pipeline([('impute', SimpleImputer(strategy='median', add_indicator=True)),
                              ('scale', StandardScaler())]), NUMERIC),
        ('categorical', Pipeline([('impute', SimpleImputer(strategy='most_frequent')),
                                  ('encode', OneHotEncoder(handle_unknown='ignore', sparse_output=False))]), CATEGORICAL),
    ])


def summarize(actual, predicted):
    if not np.isfinite(predicted).all() or (predicted <= 0).any():
        raise ValueError('Non-finite or nonpositive prediction')
    relative = np.abs(actual - predicted) / actual
    return {'mae_hours': float(np.mean(np.abs(actual - predicted))),
            'mdape': float(np.median(relative)), 'pred25': float(np.mean(relative <= .25))}


def train(manifest_path, destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Output must be a new directory; existing experiments are immutable')
    data, sources = load_projects(manifest_path)
    train_set, calibration, external = [data[data.partition == part].copy()
                                         for part in ['train', 'calibration', 'external_test']]
    # Initial engineering gates, documented for product review before execution.
    if len(data) < 1000 or len(train_set) < 600 or len(calibration) < 100 or len(external) < 200:
        raise ValueError('Need >=1000 genuine projects, >=600 train, >=100 calibration, >=200 external')
    if train_set.organization_id.nunique() < 5 or external.organization_id.nunique() < 2:
        raise ValueError('Insufficient independent organization cohorts')
    earlier = data[data.partition != 'external_test']
    if external.planning_date.min() <= earlier.completion_date.max():
        raise ValueError('External projects must start after development outcomes were available')
    if external.planning_date.min().year < 2020:
        raise ValueError('Modern external validation requires projects planned in 2020 or later')
    if (train_set[FEATURES].notna().mean() < .8).any():
        raise ValueError('Each selected feature requires >=80% observed training coverage')
    for column in CATEGORICAL:
        train_set[column] = train_set[column].fillna(np.nan)
    pipeline = Pipeline([('prepare', preprocessing()), ('model', Ridge())])
    wrapped = TransformedTargetRegressor(regressor=pipeline, func=np.log1p, inverse_func=np.expm1)
    grid = [
        {'regressor__model': [Ridge()], 'regressor__model__alpha': [.1, 1, 10, 100]},
        {'regressor__model': [RandomForestRegressor(n_estimators=300, random_state=SEED, n_jobs=1)],
         'regressor__model__min_samples_leaf': [5, 15, 30]},
        {'regressor__model': [HistGradientBoostingRegressor(random_state=SEED, early_stopping=False)],
         'regressor__model__max_leaf_nodes': [7, 15], 'regressor__model__l2_regularization': [1, 10]},
    ]
    search = GridSearchCV(wrapped, grid, cv=GroupKFold(5), scoring='neg_mean_absolute_error',
                          n_jobs=1, error_score='raise', refit=True)
    search.fit(train_set[FEATURES], train_set.effort_hours, groups=train_set.organization_id)
    selected = search.best_estimator_
    calibrated = selected.predict(calibration[FEATURES])
    summarize(calibration.effort_hours.to_numpy(), calibrated)
    residual = np.abs(np.log1p(calibration.effort_hours.to_numpy()) - np.log1p(calibrated))
    rank = math.ceil((len(residual) + 1) * .9)
    radius = float(np.sort(residual)[rank - 1])
    prediction = selected.predict(external[FEATURES])
    scores = summarize(external.effort_hours.to_numpy(), prediction)
    median = DummyRegressor(strategy='median').fit(np.zeros((len(train_set), 1)), train_set.effort_hours)
    baseline = summarize(external.effort_hours.to_numpy(), median.predict(np.zeros((len(external), 1))))
    lower = np.maximum(0, np.expm1(np.log1p(prediction) - radius))
    upper = np.expm1(np.log1p(prediction) + radius)
    coverage = float(np.mean((external.effort_hours >= lower) & (external.effort_hours <= upper)))
    width_ratio = float(np.median((upper - lower) / prediction))
    gates = {'baseline_improvement': scores['mae_hours'] <= baseline['mae_hours'] * .85,
             'mdape': scores['mdape'] <= .30, 'pred25': scores['pred25'] >= .60,
             'coverage': coverage >= .85, 'useful_intervals': width_ratio <= 2.0}
    slices = {}
    for organization, cohort in external.groupby('organization_id'):
        positions = external.index.get_indexer(cohort.index)
        slices[str(organization)] = summarize(cohort.effort_hours.to_numpy(), prediction[positions])
    gates['organization_slices'] = all(score['mdape'] <= .5 for score in slices.values())
    destination.mkdir(parents=True)
    model_path = destination / 'pipeline.pkl'
    model_path.write_bytes(pickle.dumps(selected))
    report = {'schema': SCHEMA, 'features': FEATURES, 'target': 'effort_hours', 'seed': SEED,
              'sklearn_version': sklearn.__version__, 'model_sha256': digest(model_path),
              'training_code_sha256': digest(__file__), 'sources': sources,
              'counts': data.partition.value_counts().to_dict(), 'external_metrics': scores,
              'baseline_metrics': baseline, 'interval_coverage': coverage, 'interval_width_ratio': width_ratio,
              'organization_metrics': slices,
              'log_radius': radius, 'gates': gates, 'eligible_for_review': all(gates.values()),
              'production_approved': False,
              'ranges': {column: [float(train_set[column].min()), float(train_set[column].max())] for column in NUMERIC},
              'categories': {column: sorted(train_set[column].dropna().unique().tolist()) for column in CATEGORICAL}}
    (destination / 'manifest.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    external.assign(prediction_hours=prediction, lower_hours=lower, upper_hours=upper).to_csv(destination / 'external_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    cli = argparse.ArgumentParser()
    cli.add_argument('manifest')
    cli.add_argument('destination')
    args = cli.parse_args()
    train(args.manifest, args.destination)
