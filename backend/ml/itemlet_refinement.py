"""Train-only nonlinear model selection; exposed test cohorts remain excluded."""
import argparse
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder

from ml.itemlet_research import FEATURES, load_tasks
from ml.itemlet_research import candidates as ridge_candidates
from ml.text_effort import split_projects
from ml.train_research import metrics


def candidates():
    models = {'ridge_reference': ridge_candidates()['ridge_100.0_text_True']}
    for text in [False, True]:
        for leaves in [7, 15]:
            columns = [
                ('points', make_pipeline(SimpleImputer(strategy='median', add_indicator=True, keep_empty_features=True),
                                         FunctionTransformer(np.log1p, validate=True)), ['story_points']),
                ('kind', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['issuetype_name', 'priority_name'])]
            if text:
                columns.append(('text', make_pipeline(
                    TfidfVectorizer(max_features=10000, min_df=3, sublinear_tf=True),
                    TruncatedSVD(n_components=32, random_state=20260922)), 'text'))
            models[f'boost_{leaves}_text_{text}'] = TransformedTargetRegressor(
                regressor=make_pipeline(ColumnTransformer(columns), HistGradientBoostingRegressor(
                    max_iter=150, max_leaf_nodes=leaves, min_samples_leaf=30, l2_regularization=10,
                    early_stopping=False, random_state=20260922)), func=np.log, inverse_func=np.exp)
    return models


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Existing experiment evidence cannot be overwritten')
    data, intake = load_tasks(source)
    train, calibration, test = split_projects(data)
    models = candidates()
    scores = {}
    for name, estimator in models.items():
        folds = []
        for fit, validation in GroupKFold(4).split(train, groups=train.project):
            model = clone(estimator).fit(train.iloc[fit][FEATURES], train.iloc[fit].hours)
            folds.append(metrics(train.iloc[validation].hours, model.predict(train.iloc[validation][FEATURES])))
        scores[name] = {'folds': folds, 'mean_rmsle': float(np.mean([fold['rmsle'] for fold in folds])),
                        'mean_mae_hours': float(np.mean([fold['mae_hours'] for fold in folds])),
                        'mean_pred25_percent': float(np.mean([fold['pred25_percent'] for fold in folds]))}
        print(f'{name}: development RMSLE {scores[name]["mean_rmsle"]:.4f}', flush=True)
    winner = min(scores, key=lambda name: scores[name]['mean_rmsle'])
    model = clone(models[winner]).fit(train[FEATURES], train.hours)
    report = {'schema': 'itemlet-training-refinement-v1', 'intake': intake, 'features': FEATURES,
              'selected': winner, 'development_cv': scores,
              'training_tasks': len(train), 'training_projects': int(train.project.nunique()),
              'excluded_calibration_tasks': len(calibration), 'excluded_test_tasks': len(test),
              'training_project_ids': sorted(train.project.unique().tolist()),
              'production_approved': False, 'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations': ['Training cross-validation selects candidates; it is not independent accuracy evidence',
                              'Original label verification covers a small sample, not the whole collection',
                              'Planning-time snapshots and organization independence remain unverified',
                              'No test-set reevaluation or calibration-set tuning was performed']}
    output.mkdir(parents=True, exist_ok=False)
    artifact = pickle.dumps(model)
    (output / 'candidate.pkl').write_bytes(artifact)
    report['model_sha256'] = hashlib.sha256(artifact).hexdigest()
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    report = run(**vars(parser.parse_args()))
    print(json.dumps({'selected': report['selected'], 'production_approved': False}))
