import pandas as pd
import pytest
from ml.audit_seera import audit_archive, audit_frame


def sample():
    return pd.DataFrame({'Actual duration': [3., 6.], 'Actual effort': [3168., 5280.],
                         'Team size': [6, 6], 'Dedicated team members': [6, 4],
                         'Daily working hours': [8, 8]})


def test_detects_formula_target_and_reports_nonmatches_without_approval():
    data = sample()
    assert audit_frame(data)['formula_matches'] == 2
    data.loc[0, 'Actual effort'] += 10
    result = audit_frame(data)
    assert result['formula_matches'] == 1
    assert result['max_absolute_difference_hours'] == 10
    assert result['production_approved'] is False


def test_invalid_evidence_is_rejected():
    data = sample()
    data.loc[0, 'Actual effort'] = float('nan')
    with pytest.raises(ValueError, match='Invalid'):
        audit_frame(data)


def test_unreviewed_archive_is_rejected_before_parsing(tmp_path):
    path = tmp_path / 'untrusted.zip'
    path.write_bytes(b'not an archive')
    with pytest.raises(ValueError, match='Unreviewed'):
        audit_archive(path)
