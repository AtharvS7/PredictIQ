import numpy as np
import pytest
from ml.model_comparison import compare_predictions


def test_exact_candidate_beats_biased_baseline_across_independent_groups():
    y = np.arange(1, 11, dtype=float)
    result = compare_predictions(y, y, y * 2, np.arange(10), draws=100)
    assert result['clear_improvement_in_observed_cohort'] is True
    assert result['mae_delta_95pct_cluster_bootstrap'][1] < 0
    assert result['production_approved'] is False


def test_one_project_cannot_be_inflated_into_independent_task_evidence():
    result = compare_predictions([1] * 100, [1] * 100, [2] * 100, ['one'] * 100, draws=100)
    assert result['mae_delta_95pct_cluster_bootstrap'] is None
    assert result['clear_improvement_in_observed_cohort'] is False


def test_identical_predictions_are_not_an_improvement():
    result = compare_predictions([1] * 10, [2] * 10, [2] * 10, np.arange(10), draws=100)
    assert result['mae_delta_95pct_cluster_bootstrap'] == [0, 0]
    assert result['clear_improvement_in_observed_cohort'] is False


def test_missing_project_identity_cannot_support_clustered_uncertainty():
    with pytest.raises(ValueError, match='project identities'):
        compare_predictions([1, 2], [1, 2], [2, 3], ['a', None])


@pytest.mark.parametrize('candidate', [[0, 1], [float('nan'), 1], [1], [[1, 1]]])
def test_invalid_or_unpaired_predictions_fail(candidate):
    with pytest.raises(ValueError):
        compare_predictions([1, 2], candidate, [2, 3], ['a', 'b'])
