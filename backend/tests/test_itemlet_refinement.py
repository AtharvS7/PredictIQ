import numpy as np
import pandas as pd
from ml.itemlet_refinement import candidates


def test_nonlinear_candidates_fit_with_missing_points_and_unknown_categories():
    frame = pd.DataFrame({'text': [' '.join(f'term{j + i}' for j in range(60)) for i in range(80)],
                          'story_points': [np.nan, 1, 2, 3] * 20,
                          'issuetype_name': ['Task'] * 80, 'priority_name': ['Normal'] * 80})
    for name, model in candidates().items():
        if name == 'ridge_reference':
            continue
        model.fit(frame, np.arange(1., 81.))
        prediction = model.predict(frame.assign(priority_name='new priority'))
        assert np.isfinite(prediction).all() and (prediction > 0).all()
        assert model.regressor_.named_steps['histgradientboostingregressor'].early_stopping is False
