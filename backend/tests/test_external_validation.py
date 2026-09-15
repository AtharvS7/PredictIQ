import pytest
from ml.external_validation import read_att
from ml.tune_research import tuning_candidates


def test_att_column_mapping_preserves_actual_hours(tmp_path):
    path = tmp_path / 'att.txt'
    path.write_text('1059 15000 1 5 1\n' * 104)
    frame = read_att(path)
    assert frame.iloc[0].effort_hours == 15000
    assert frame.iloc[0].size_fp == 1059
    assert frame.iloc[0].database_system == 5
    assert frame.project_id.nunique() == 104


@pytest.mark.parametrize('row', ['1 0 0 1 1', '1 50 8 1 1', 'nan 50 0 1 1'])
def test_att_rejects_invalid_units_or_categories(tmp_path, row):
    path = tmp_path / 'att.txt'
    path.write_text((row + '\n') * 104)
    with pytest.raises(ValueError):
        read_att(path)


def test_tuning_candidates_clone_and_predict_finite():
    import numpy as np
    from sklearn.base import clone

    x = np.arange(1, 25).reshape(-1, 1)
    for candidate in tuning_candidates().values():
        prediction = clone(candidate).fit(x, x.ravel() * 10).predict([[10]])
        assert np.isfinite(prediction).all()
        assert prediction[0] > 0
