import numpy as np
import pandas as pd
import pytest
from ml.itemlet_error_analysis import diagnose, run


@pytest.fixture
def observations():
    return pd.DataFrame({'hours': [1., 2., 20., 100.], 'story_points': [1., np.nan, 5., 0.],
                         'issuetype_name': ['Task', 'Bug', 'Task', 'Bug'],
                         'project': ['a', 'a', 'b', 'b']})


def test_cohorts_preserve_observations_and_missing_points(observations):
    result = diagnose(observations, [1, 2, 10, 50], minimum_cohort=2)
    for family in result.values():
        assert sum(cohort['tasks'] for cohort in family.values()) == 4
    assert result['planning_points']['missing_or_zero']['tasks'] == 2
    assert result['project']['b']['underestimated_fraction'] == 1
    assert result['project']['a']['mae_hours'] == 0


def test_small_cohorts_do_not_claim_metrics(observations):
    result = diagnose(observations, [1, 2, 20, 100])
    assert all(c['metrics_suppressed'] and 'mae_hours' not in c
               for family in result.values() for c in family.values())


@pytest.mark.parametrize('prediction', [[1], [1, 2, np.nan, 4], [1, 2, 0, 4], [[1, 2, 3, 4]]])
def test_invalid_predictions_are_rejected(observations, prediction):
    with pytest.raises(ValueError, match='aligned positive finite'):
        diagnose(observations, prediction)


def test_existing_evidence_is_never_overwritten(tmp_path):
    with pytest.raises(ValueError, match='cannot be overwritten'):
        run(tmp_path / 'missing.csv', tmp_path)
