import pandas as pd
from ml.audit_itemlet import audit


def test_counts_are_not_accepted_as_actual_work_hours(tmp_path):
    path = tmp_path / 'itemlet.csv'
    pd.DataFrame({'issue_key': ['A-1', 'A-2'], 'project_key': ['A', 'A'],
                  'created': ['2020-01-01', None], 'resolutiondate': ['2020-01-02', None],
                  'worklog_total': [3, 0], 'Worklog Count': [3, 0],
                  'Total Time Logged (hours)': [3 / 3600, 0], 'story_points': [2, None]}).to_csv(path, index=False)
    report = audit(path)
    assert report['rows'] == 2
    assert report['projects'] == 1
    assert report['positive_logged_hours'] == 1
    assert report['valid_completed_dates'] == 1
    assert report['hours_equal_worklog_total_div_3600'] == 2
    assert report['positive_hours_below_one_minute'] == 1
    assert report['production_approved'] is False
