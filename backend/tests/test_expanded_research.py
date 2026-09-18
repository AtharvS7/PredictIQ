import pandas as pd
import pytest
from ml.expanded_research import exclude_pairs, read_albrecht, validate_projects


def test_albrecht_converts_thousands_of_hours_by_named_column(tmp_path):
    path = tmp_path / 'sample.arff'
    path.write_text('@relation fixture\n@attribute Effort numeric\n@attribute AdjFP numeric\n@data\n2.5,120\n')
    result = read_albrecht(path)
    assert result.iloc[0].effort_hours == 2500
    assert result.iloc[0].size_fp == 120


def test_overlap_removed_even_with_different_source_identity():
    fit = pd.DataFrame({'size_fp': [10, 20], 'effort_hours': [100, 200]})
    validation = pd.DataFrame({'size_fp': [10], 'effort_hours': [100]})
    assert exclude_pairs(fit, validation).size_fp.tolist() == [20]


@pytest.mark.parametrize('effort', [0, -1, float('nan'), float('inf')])
def test_invalid_effort_rejected(effort):
    with pytest.raises(ValueError):
        validate_projects(pd.DataFrame({'source': ['fixture'], 'project_id': ['1'],
                                        'size_fp': [10], 'effort_hours': [effort]}))
