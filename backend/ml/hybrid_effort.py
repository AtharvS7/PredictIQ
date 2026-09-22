"""Nested project validation of text plus human-estimate calibration.

Uses only JOSSE's original development partition. Previously exposed test and
calibration projects are excluded. This experiment cannot approve production.
Run from backend: python -m ml.hybrid_effort SOURCE_SQLITE NEW_OUTPUT
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.utils.validation import check_is_fitted

from ml.model_comparison import compare_predictions
from ml.text_effort import load_josse, split_projects
from ml.train_research import metrics


class EstimateCalibrator(RegressorMixin, BaseEstimator):
    """Learn a log-ratio correction; IDs and outcomes never enter features."""

    def __init__(self, alpha=100., use_text=False, correction_weight=1.):
        self.alpha = alpha
        self.use_text = use_text
        self.correction_weight = correction_weight

    def _validate(self, frame):
        hours = frame['expert_hours'].to_numpy(dtype=float)
        if not len(hours) or not np.isfinite(hours).all() or (hours <= 0).any():
            raise ValueError('Positive finite planning estimates required')
        if self.use_text and (frame.text.isna().any() or not frame.text.map(lambda s: isinstance(s, str)).all()):
            raise ValueError('Task descriptions must be strings')
        return hours

    def fit(self, X, y):
        hours = self._validate(X)
        actual = np.asarray(y, dtype=float)
        if actual.shape != hours.shape or not np.isfinite(actual).all() or (actual <= 0).any():
            raise ValueError('Positive finite aligned effort labels required')
        if not 0 <= self.correction_weight <= 1:
            raise ValueError('Correction weight must be between zero and one')
        transformers = [('estimate', FunctionTransformer(np.log, validate=True), ['expert_hours'])]
        if self.use_text:
            transformers.append(('text', TfidfVectorizer(max_features=10000, ngram_range=(1, 2),
                                                        min_df=2, sublinear_tf=True), 'text'))
        self.model_ = make_pipeline(ColumnTransformer(transformers), Ridge(alpha=self.alpha, solver='lsqr'))
        self.model_.fit(X, np.log(actual / hours))
        return self

    def predict(self, X):
        check_is_fitted(self, 'model_')
        hours = self._validate(X)
        # Prespecified guardrail: never silently change a human estimate by >4x.
        correction = np.clip(self.model_.predict(X) * self.correction_weight, -np.log(4), np.log(4))
        return hours * np.exp(correction)


def candidates():
    return {f'{kind}_{alpha}_{weight}': EstimateCalibrator(alpha, kind == 'text', weight)
            for kind in ['estimate', 'text'] for alpha in [10., 100.]
            for weight in [.25, .5, 1.]}


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Never overwrite experiment evidence')
    all_tasks, intake = load_josse(source)
    development, calibration, test = split_projects(all_tasks)
    tasks = development.loc[np.isfinite(development.expert_hours) & development.expert_hours.gt(0)].copy()
    if tasks.project.nunique() < 12 or len(tasks) < 100:
        raise ValueError('Insufficient development projects with planning estimates')
    models = candidates()
    prediction = np.zeros(len(tasks))
    selections = []
    for outer_fit, outer_validation in GroupKFold(4).split(tasks, groups=tasks.project):
        train = tasks.iloc[outer_fit]
        scores = {}
        for name, candidate in models.items():
            errors = []
            for fit, validation in GroupKFold(3).split(train, groups=train.project):
                model = clone(candidate).fit(train.iloc[fit], train.iloc[fit].hours)
                estimate = model.predict(train.iloc[validation])
                errors.extend(abs(np.log(estimate / train.iloc[validation].hours)))
            scores[name] = float(np.mean(errors))
        # Unchanged human estimates compete in the same inner folds.
        scores['human'] = float(np.mean(abs(np.log(train.expert_hours / train.hours))))
        selected = min(scores, key=scores.get)
        validation = tasks.iloc[outer_validation]
        if selected == 'human':
            prediction[outer_validation] = validation.expert_hours
        else:
            model = clone(models[selected]).fit(train, train.hours)
            prediction[outer_validation] = model.predict(validation)
        selections.append({'selected': selected, 'inner_mean_absolute_log_errors': scores,
                           'validation_projects': sorted(validation.project.unique().tolist())})
    report = {'schema': 'hybrid-effort-development-v1', 'features': ['expert_hours', 'task_description'],
              'intake': intake, 'development_tasks': len(tasks), 'development_projects': int(tasks.project.nunique()),
              'excluded_original_calibration_tasks': len(calibration), 'excluded_original_test_tasks': len(test),
              'evaluation': 'Nested 4 outer / 3 inner project folds; development evidence only',
              'selection_metric': 'mean absolute log error', 'folds': selections,
              'candidate': metrics(tasks.hours, prediction), 'human': metrics(tasks.hours, tasks.expert_hours),
              'paired': compare_predictions(tasks.hours, prediction, tasks.expert_hours, tasks.project),
              'source_sha256': hashlib.sha256(Path(source).read_bytes()).hexdigest(),
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'production_approved': False,
              'limitations': ['Development evidence is not independent external validation',
                              'Requires an initial human estimate; cannot infer whole-project cost from text',
                              'Snapshot descriptions and expert estimates lack planning-time history',
                              'Cross-validation fold errors share training data; bootstrap uncertainty is descriptive']}
    output.mkdir(parents=True, exist_ok=False)
    (output / 'evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    tasks.drop(columns='text').assign(predicted_hours=prediction).to_csv(output / 'development_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    report = run(**vars(parser.parse_args()))
    print(json.dumps({k: report[k] for k in ['development_tasks', 'development_projects', 'candidate',
                                           'human', 'paired', 'production_approved']}, indent=2))
