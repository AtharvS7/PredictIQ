import sqlite3

import pandas as pd
from ml.text_effort import load_josse, split_projects


def test_josse_units_deduplication_and_missing_expert_estimates(tmp_path):
    path = tmp_path / 'fixture.sqlite3'
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE "case" (id TEXT, corpus TEXT, expert_estimated_effort REAL, actual_effort REAL)')
        conn.executemany('INSERT INTO "case" VALUES (?, ?, ?, ?)', [
            ('A-1', 'unique task description', 0, 7200),
            ('B-1', 'duplicated task description', 3600, 7200),
            ('C-1', 'Duplicated  task description', 3600, 7200),
            ('D-1', 'unfinished work item', 3600, 0),
        ])
    data, report = load_josse(path)
    assert len(data) == 1
    assert data.iloc[0].hours == 2
    assert data.iloc[0].expert_hours == 0
    assert report['excluded_repeated_text'] == 2
    assert report['excluded_invalid'] == 1


def test_whole_projects_are_separated_in_all_three_partitions():
    data = pd.DataFrame({'project': [f'project-{i // 10}' for i in range(200)]})
    train, calibration, test = split_projects(data)
    sets = [set(part.project) for part in [train, calibration, test]]
    assert not sets[0] & sets[1]
    assert not sets[0] & sets[2]
    assert not sets[1] & sets[2]
    assert sum(map(len, [train, calibration, test])) == len(data)
