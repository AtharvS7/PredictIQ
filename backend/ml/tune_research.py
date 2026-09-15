"""Tune research candidates on training-source folds; never overwrite serving artifacts.

Run from backend: python -m ml.tune_research
Previously observed test metrics are diagnostic, not new independent evidence.
"""
import json
import pickle

import numpy as np
import pandas as pd
from sklearn.base import clone

from ml.train_research import ROOT, candidates, metrics, split_projects


def tuning_candidates():
    base = candidates()
    result = {}
    for alpha in [0.01, 0.1, 1, 10, 100]:
        result[f'ridge_{alpha}'] = clone(base['power_law_ridge']).set_params(regressor__ridge__alpha=alpha)
    for epsilon in [1.1, 1.35, 1.75, 2.0]:
        result[f'huber_{epsilon}'] = clone(base['power_law_huber']).set_params(regressor__huberregressor__epsilon=epsilon)
    for leaf in [4, 8, 16, 32]:
        result[f'forest_{leaf}'] = clone(base['random_forest']).set_params(regressor__randomforestregressor__min_samples_leaf=leaf)
    return result


def main():
    data = pd.read_csv(ROOT / 'experiments/reconstructed-v1/projects.csv')
    train, _, test = split_projects(data)
    x, y = data[['size_fp']], data.effort_hours
    models, scores = tuning_candidates(), {}
    for name, model in models.items():
        folds = []
        for source in sorted(data.source.unique()):
            val = train[data.iloc[train].source.to_numpy() == source]
            fit = train[data.iloc[train].source.to_numpy() != source]
            fit = fit[~data.iloc[fit].duplicate_group.isin(data.iloc[val].duplicate_group)]
            fitted = clone(model).fit(x.iloc[fit], y.iloc[fit])
            folds.append(metrics(y.iloc[val], fitted.predict(x.iloc[val]))['rmsle'])
        scores[name] = float(np.mean(folds))
    winner = min(scores, key=scores.get)
    fitted = models[winner].fit(x.iloc[train], y.iloc[train])
    report = {'selected': winner, 'training_source_cv_rmsle': scores,
              'observed_test_diagnostic': metrics(y.iloc[test], fitted.predict(x.iloc[test])),
              'production_approved': False,
              'limitations': ['Previously observed test set', 'Source rights unresolved',
                              'One common input feature; richer schema needs compatible observations',
                              'No prospective cost outcomes or external validation']}
    destination = ROOT / 'experiments/tuned-v1'
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False))
    (destination / 'candidate.pkl').write_bytes(pickle.dumps(fitted))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
