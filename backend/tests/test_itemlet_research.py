import hashlib

import numpy as np
import pandas as pd
from ml.itemlet_research import FEATURES, candidates, load_tasks


def test_candidates_handle_missing_points_and_new_categories_without_outcome_features():
    frame = pd.DataFrame({'text': ['database integration work', 'frontend integration work'] * 6,
                          'story_points': [1., np.nan, 3.] * 4,
                          'issuetype_name': ['Task'] * 12, 'priority_name': ['Normal'] * 12})
    for model in candidates().values():
        model.fit(frame, np.arange(1, 13))
        frame['priority_name'] = 'unseen'
        predicted = model.predict(frame)
        assert np.isfinite(predicted).all() and (predicted > 0).all()
    assert set(FEATURES) == {'text', 'story_points', 'issuetype_name', 'priority_name'}


def test_intake_excludes_open_invalid_and_repeated_tasks(tmp_path, monkeypatch):
    row = {'issue_key': 'A-1', 'project_key': 'A', 'issue_summary': 'implement database integration',
           'story_points': 3, 'issuetype_name': 'Task', 'priority_name': 'Normal',
           'created': '2020-01-01', 'resolutiondate': '2020-01-02',
           'status_statusCategory_name': 'Done', 'Total Time Logged (hours)': 5}
    rows = [row, row | {'issue_key': 'A-2', 'issue_summary': 'unfinished task description',
                       'status_statusCategory_name': 'In Progress'},
            row | {'issue_key': 'A-3', 'issue_summary': 'negative effort task', 'Total Time Logged (hours)': -1},
            row | {'issue_key': 'B-1', 'project_key': 'B', 'issue_summary': 'repeated description'},
            row | {'issue_key': 'C-1', 'project_key': 'C', 'issue_summary': 'Repeated  description'}]
    path = tmp_path / 'tasks.csv'
    pd.DataFrame(rows).to_csv(path, index=False)
    monkeypatch.setattr('ml.itemlet_research.ITEMLET', ('', '', hashlib.sha256(path.read_bytes()).hexdigest(), 0))
    tasks, intake = load_tasks(path)
    assert tasks.id.tolist() == ['A-1']
    assert tasks.hours.tolist() == [5]
    assert intake['excluded_duplicate_rows'] == 2
