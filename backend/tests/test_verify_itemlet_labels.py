import pandas as pd
import pytest
from ml.verify_itemlet_labels import compare_record, fetch_record, select_sample


def test_seconds_are_converted_and_worklog_count_is_never_duration():
    row = {'key': 'AAF-1', 'fields': {'timespent': 540, 'timetracking': {'timeSpentSeconds': 540},
                                    'worklog': {'total': 1}}}
    assert compare_record('AAF-1', .15, row)['status'] == 'matched'
    assert compare_record('AAF-1', 1, row)['status'] == 'different'
    assert compare_record('AAF-1', 1, {'key': 'AAF-1', 'fields': {'worklog': {'total': 3600}}})['status'] == 'missing_duration'


def test_conflicting_seconds_are_not_arbitrarily_selected():
    assert compare_record('AAF-1', 1, {'key': 'AAF-1', 'fields': {
        'timespent': 3600, 'timetracking': {'timeSpentSeconds': 7200}}})['status'] == 'conflicting_original_duration'


@pytest.mark.parametrize('seconds', [True, '3600', -1, float('nan'), float('inf')])
def test_invalid_original_durations_are_rejected(seconds):
    with pytest.raises(ValueError):
        compare_record('AAF-1', 1, {'key': 'AAF-1', 'fields': {'timespent': seconds}})


def test_identity_and_endpoint_are_checked_before_network():
    with pytest.raises(ValueError, match='identity'):
        compare_record('AAF-1', 1, {'key': 'AAF-2'})
    for project, issue in [('PRIVATE', 'PRIVATE-1'), ('AAF', '../../admin'), ('AAF', 'CRUC-1')]:
        with pytest.raises(ValueError):
            fetch_record(project, issue)


def test_sample_is_deterministic_independent_of_row_order_and_limited():
    frame = pd.DataFrame({'issue_key': [f'AAF-{i}' for i in range(10)],
                          'project_key': ['AAF'] * 10, 'Total Time Logged (hours)': list(range(10))})
    assert select_sample(frame) == select_sample(frame.iloc[::-1])
    assert len(select_sample(frame)) == 3
    assert all(row['Total Time Logged (hours)'] > 0 for row in select_sample(frame))
