import pandas as pd
import pytest
from ml.task_calibration import FEATURES, load_tasks, rolling_folds, temporal_split


def source_files(tmp_path, conflicting=False):
    row = {'TaskNumber': 1, 'ProjectCode': 'project', 'StatusCode': 'FINISHED',
           'HoursEstimate': 4, 'HoursActual': 6, 'Category': 'Development', 'SubCategory': 'Bug'}
    second = row | {'HoursActual': 7 if conflicting else 6}
    pd.DataFrame([row, second, row | {'TaskNumber': 2, 'StatusCode': 'CANCELLED'}]).to_csv(
        tmp_path / 'Sip-task-info.csv', index=False)
    pd.DataFrame([{'TaskNumber': n, 'EstimateOn': '01-Jan-10', 'CompletedOn': '02-Jan-10'}
                  for n in [1, 1, 2]]).to_csv(tmp_path / 'est-act-dates.csv', index=False)


def test_developer_rows_do_not_multiply_actual_task_effort(tmp_path):
    source_files(tmp_path)
    data, report, hashes = load_tasks(tmp_path)
    assert len(data) == 1
    assert data.HoursActual.sum() == 6
    assert report['excluded_noncompleted'] == 1
    assert len(hashes) == 2


def test_conflicting_task_totals_fail_instead_of_arbitrary_deduplication(tmp_path):
    source_files(tmp_path, conflicting=True)
    with pytest.raises(ValueError, match='Conflicting'):
        load_tasks(tmp_path)


def test_temporal_split_purges_outcomes_not_available_at_prediction_time():
    dates = pd.date_range('2010-01-01', periods=300, tz='UTC')
    data = pd.DataFrame({'EstimateOn': dates, 'CompletedOn': dates + pd.Timedelta(days=15)})
    train, calibration, test = temporal_split(data)
    assert train.CompletedOn.max() < calibration.EstimateOn.min()
    assert calibration.CompletedOn.max() < test.EstimateOn.min()
    assert len(train) + len(calibration) + len(test) < len(data)
    assert not set(train.index) & set(test.index)


def test_features_exclude_recorded_outcomes_and_post_completion_staffing():
    assert FEATURES == ['HoursEstimate', 'Category', 'SubCategory']


def test_rolling_validation_never_reuses_boundary_dates_or_future_outcomes():
    dates = pd.date_range('2010-01-01', periods=100, tz='UTC').repeat(2)
    data = pd.DataFrame({'EstimateOn': dates, 'CompletedOn': dates + pd.Timedelta(days=5)})
    seen = set()
    for fit, validation in rolling_folds(data):
        assert fit.CompletedOn.max() < validation.EstimateOn.min()
        assert not seen.intersection(validation.index)
        seen.update(validation.index)
    assert seen == set(data.index[data.EstimateOn >= dates[80]])
