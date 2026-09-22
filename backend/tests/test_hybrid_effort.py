import pickle

import numpy as np
import pandas as pd
import pytest
from ml.hybrid_effort import EstimateCalibrator
from sklearn.base import clone


def fixture():
    return pd.DataFrame({'expert_hours': [1., 2., 4., 8.] * 5,
                         'text': ['database interface task', 'frontend interface task'] * 10})


@pytest.mark.parametrize('use_text', [False, True])
def test_correction_learns_and_roundtrips_without_outcome_or_identity_features(use_text):
    frame = fixture()
    model = clone(EstimateCalibrator(use_text=use_text)).fit(frame, frame.expert_hours * 2)
    prediction = model.predict(frame)
    np.testing.assert_allclose(prediction, frame.expert_hours * 2)
    frame['hours'] = -999
    frame['project'] = 'never_seen'
    np.testing.assert_allclose(pickle.loads(pickle.dumps(model)).predict(frame), prediction)


def test_zero_correction_preserves_human_baseline_and_extreme_fit_is_bounded():
    frame = fixture()
    model = EstimateCalibrator(correction_weight=0).fit(frame, frame.expert_hours * 100)
    np.testing.assert_allclose(model.predict(frame), frame.expert_hours)
    model = EstimateCalibrator().fit(frame, frame.expert_hours * 100)
    np.testing.assert_allclose(model.predict(frame), frame.expert_hours * 4)


@pytest.mark.parametrize('bad', [0., -1., np.nan, np.inf])
def test_invalid_planning_estimates_fail_closed(bad):
    frame = fixture()
    model = EstimateCalibrator().fit(frame, frame.expert_hours)
    frame.loc[0, 'expert_hours'] = bad
    with pytest.raises(ValueError, match='planning estimates'):
        model.predict(frame)
