"""Paired model comparisons with project-clustered uncertainty.

Intervals quantify uncertainty within the observed cohort, not deployment drift.
"""
import numpy as np


def compare_predictions(actual, candidate, baseline, projects, *, draws=2000, seed=20260918):
    actual, candidate, baseline = [np.asarray(values, dtype=float) for values in (actual, candidate, baseline)]
    project_values = np.asarray(projects, dtype=object)
    if project_values.ndim != 1 or any(value is None or str(value).strip().lower() in {'', 'nan', 'none'}
                                     for value in project_values):
        raise ValueError('Observed project identities required for clustered uncertainty')
    projects = project_values.astype(str)
    if actual.ndim != 1 or not len(actual) or any(v.shape != actual.shape for v in [candidate, baseline, projects]):
        raise ValueError('Paired nonempty vectors required')
    if any(not np.isfinite(v).all() or (v <= 0).any() for v in [actual, candidate, baseline]):
        raise ValueError('Positive finite actuals and predictions required')
    if draws < 100:
        raise ValueError('At least 100 bootstrap draws required')
    groups = np.unique(projects)
    candidate_error, baseline_error = np.abs(actual - candidate), np.abs(actual - baseline)
    sums = np.array([[candidate_error[projects == group].sum(), baseline_error[projects == group].sum(),
                      (projects == group).sum()] for group in groups])
    rng = np.random.default_rng(seed)
    # Resample projects, retaining all tasks and the candidate/baseline pairing.
    sampled = sums[rng.integers(0, len(groups), size=(draws, len(groups)))].sum(axis=1)
    deltas = (sampled[:, 0] - sampled[:, 1]) / sampled[:, 2]
    candidate_relative, baseline_relative = candidate_error / actual, baseline_error / actual
    interval = np.quantile(deltas, [.025, .975]).tolist() if len(groups) >= 5 else None
    return {
        'tasks': len(actual), 'projects': len(groups),
        'mae_delta_hours': float(candidate_error.mean() - baseline_error.mean()),
        'mae_delta_95pct_cluster_bootstrap': interval,
        'mdape_delta': float(np.median(candidate_relative) - np.median(baseline_relative)),
        'pred25_delta': float(np.mean(candidate_relative <= .25) - np.mean(baseline_relative <= .25)),
        'clear_improvement_in_observed_cohort': bool(interval is not None and interval[1] < 0
            and np.median(candidate_relative) <= np.median(baseline_relative)
            and np.mean(candidate_relative <= .25) >= np.mean(baseline_relative <= .25)),
        'production_approved': False,
    }
