"""Training-only error diagnosis; never evaluates or promotes a production model."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GroupKFold

from ml.itemlet_research import FEATURES, candidates, load_tasks
from ml.text_effort import split_projects
from ml.train_research import metrics


def diagnose(frame, predictions, minimum_cohort=20):
    if not isinstance(minimum_cohort, int) or isinstance(minimum_cohort, bool) or minimum_cohort < 2:
        raise ValueError('Cohort metrics require at least two observations')
    actual = frame.hours.to_numpy(dtype=float)
    predicted = np.asarray(predictions, dtype=float)
    if (len(frame) == 0 or predicted.shape != actual.shape
            or not np.isfinite(actual).all() or not np.isfinite(predicted).all()
            or (actual <= 0).any() or (predicted <= 0).any()):
        raise ValueError('Diagnosis requires aligned positive finite observations')
    cohorts = {
        'planning_points': np.where(frame.story_points.gt(0), 'observed_positive', 'missing_or_zero'),
        'issue_type': frame.issuetype_name.fillna('unknown').to_numpy(),
        'project': frame.project.to_numpy(),
        # Outcome slices diagnose error, never supply inference-time features.
        'actual_effort_hours': pd.cut(actual, [0, 1, 4, 16, 64, np.inf],
                                      labels=['0-1', '1-4', '4-16', '16-64', '64+']).astype(str),
    }
    result = {}
    for family, labels in cohorts.items():
        summaries = {}
        for label in sorted(set(labels)):
            positions = np.asarray(labels) == label
            count = int(positions.sum())
            summary = {'tasks': count, 'metrics_suppressed': count < minimum_cohort}
            if count >= minimum_cohort:
                summary.update(metrics(actual[positions], predicted[positions]))
                summary['median_actual_hours'] = float(np.median(actual[positions]))
                summary['median_prediction_hours'] = float(np.median(predicted[positions]))
                summary['underestimated_fraction'] = float(np.mean(predicted[positions] < actual[positions]))
            summaries[str(label)] = summary
        result[family] = summaries
    return result


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Existing experiment evidence cannot be overwritten')
    tasks, intake = load_tasks(source)
    training, calibration, test = split_projects(tasks)
    if training.project.nunique() < 4:
        raise ValueError('Four training projects are required')
    reference = candidates()['ridge_100.0_text_True']
    predictions = np.full(len(training), np.nan)
    fold_reports = []
    for fold, (fit, validation) in enumerate(GroupKFold(4).split(training, groups=training.project)):
        fit_projects = set(training.iloc[fit].project)
        validation_projects = set(training.iloc[validation].project)
        if fit_projects & validation_projects:
            raise ValueError('Project leakage in development folds')
        model = clone(reference).fit(training.iloc[fit][FEATURES], training.iloc[fit].hours)
        predictions[validation] = model.predict(training.iloc[validation][FEATURES])
        fold_reports.append({'fold': fold, 'fit_tasks': len(fit), 'validation_tasks': len(validation),
                             'validation_projects': sorted(validation_projects)})
    report = {
        'schema': 'itemlet-development-error-analysis-v1', 'production_approved': False,
        'scope': 'Out-of-fold diagnosis on original training projects only; not independent test accuracy',
        'intake': intake, 'training_tasks': len(training),
        'excluded_calibration_tasks': len(calibration), 'excluded_test_tasks': len(test),
        'folds': fold_reports, 'cohorts': diagnose(training, predictions),
        'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limitations': ['Task hours are not whole-project effort',
                        'Planning-time snapshots and complete labels remain unverified',
                        'Outcome cohorts are retrospective diagnostics, never model inputs'],
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / 'diagnosis.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    training[['id', 'project', 'hours']].assign(prediction_hours=predictions).to_csv(
        output / 'private_development_predictions.csv', index=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    report = run(**vars(parser.parse_args()))
    print(json.dumps({'training_tasks': report['training_tasks'], 'production_approved': False}))
