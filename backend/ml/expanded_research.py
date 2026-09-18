"""Source-held-out historical experiment; never a production promotion command.

Run from backend: python -m ml.expanded_research OUTPUT_DIRECTORY
Fits the 891-row development collection, reserves Albrecht for external diagnosis.
Previously evaluated development sources are explicitly reused as development.
"""
import argparse
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler
from sklearn.svm import SVR

from ml.rebuild_dataset import read_source
from ml.train_research import ROOT, candidates, metrics


def validate_projects(frame):
    required = ['source', 'project_id', 'size_fp', 'effort_hours']
    if not set(required).issubset(frame.columns) or frame.empty:
        raise ValueError('Missing project fields or empty dataset')
    frame = frame[required].copy()
    if frame[['source', 'project_id']].isna().any().any():
        raise ValueError('Missing project identity')
    if frame.duplicated(['source', 'project_id']).any():
        raise ValueError('Duplicate project identity')
    for col in ['size_fp', 'effort_hours']:
        frame[col] = pd.to_numeric(frame[col], errors='raise')
        if not np.isfinite(frame[col]).all() or (frame[col] <= 0).any():
            raise ValueError('Invalid size or effort')
    return frame


def read_albrecht(path):
    raw = read_source(path)
    # Source documentation: adjusted FP and effort in THOUSANDS of person-hours.
    return validate_projects(pd.DataFrame({
        'source': 'albrecht', 'project_id': raw.index.astype(str),
        'size_fp': pd.to_numeric(raw['AdjFP'], errors='raise'),
        'effort_hours': pd.to_numeric(raw['Effort'], errors='raise') * 1000,
    }))


def exclude_pairs(fit, validation):
    pairs = set(zip(validation.size_fp, validation.effort_hours))
    return fit.loc[[pair not in pairs for pair in zip(fit.size_fp, fit.effort_hours)]]


def run(destination):
    destination = Path(destination)
    if destination.exists():
        raise ValueError('Use a new experiment directory; previous evidence is immutable')
    development_path = ROOT / 'experiments/expanded-v2/projects.csv'
    external_path = ROOT / 'data/research/albrecht.arff'
    development = validate_projects(pd.read_csv(development_path))
    external = exclude_pairs(read_albrecht(external_path), development)
    if len(external) < 10 or development.source.nunique() < 3:
        raise ValueError('Insufficient independent sources or external observations')
    models = candidates()
    # Fixed small search, selected exclusively by development-source CV.
    for c in [0.1, 1.0, 10.0]:
        models[f'svr_{c}'] = TransformedTargetRegressor(
            regressor=make_pipeline(FunctionTransformer(np.log1p, validate=True),
                                    StandardScaler(), SVR(C=c, epsilon=0.2)),
            func=np.log1p, inverse_func=np.expm1)
    scores = {}
    for name, model in models.items():
        folds = {}
        for source in sorted(development.source.unique()):
            validation = development.loc[development.source == source]
            fit = exclude_pairs(development.loc[development.source != source], validation)
            fitted = clone(model).fit(fit[['size_fp']], fit.effort_hours)
            folds[source] = metrics(validation.effort_hours, fitted.predict(validation[['size_fp']]))
        scores[name] = {'folds': folds, 'mean_source_rmsle': float(np.mean(
            [fold['rmsle'] for fold in folds.values()]))}
    winner = min(scores, key=lambda name: scores[name]['mean_source_rmsle'])
    fitted = clone(models[winner]).fit(development[['size_fp']], development.effort_hours)
    prediction = fitted.predict(external[['size_fp']])
    comparisons = {}
    for name in ['median', 'power_law_huber']:
        baseline = clone(models[name]).fit(development[['size_fp']], development.effort_hours)
        comparisons[name] = metrics(external.effort_hours, baseline.predict(external[['size_fp']]))
    report = {
        'selected_model': winner, 'development_rows': len(development),
        'external_rows': len(external), 'collection_rows': len(development) + len(external),
        'features': ['size_fp'], 'target': 'effort_hours', 'source_cv': scores,
        'external_metrics': metrics(external.effort_hours, prediction),
        'external_baselines': comparisons, 'production_approved': False,
        'hashes': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [development_path, external_path, Path(__file__)]},
        'external_source': 'https://github.com/Derek-Jones/Software-estimation-datasets/blob/main/albrecht.arff',
        'limitations': ['Historical projects, not modern prospective validation',
                       'Source is not organization identity; organization separation unverified',
                       'Research access does not establish production redistribution rights',
                       'One measured size input; not compatible with nine-input production serving',
                       'No validation of NLP-derived size against recorded function points',
                       'External cohort is small and now observed; do not tune against it'],
    }
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'candidate.pkl').write_bytes(pickle.dumps(fitted))
    report['model_sha256'] = hashlib.sha256((destination / 'candidate.pkl').read_bytes()).hexdigest()
    (destination / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    external.assign(prediction_hours=prediction).to_csv(destination / 'external_predictions.csv', index=False)
    development = development.assign(partition='development')
    pd.concat([development, external.assign(partition='external_diagnostic')]).to_csv(destination / 'projects.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    report = run(parser.parse_args().output)
    print(json.dumps({key: report[key] for key in ['selected_model', 'collection_rows',
          'development_rows', 'external_rows', 'external_metrics', 'external_baselines', 'production_approved']}, indent=2))
