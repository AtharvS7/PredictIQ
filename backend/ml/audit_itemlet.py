"""Memory-bounded intake audit; Itemlet logged-hour provenance is unresolved."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS = ['issue_key', 'project_key', 'created', 'resolutiondate', 'worklog_total',
           'Worklog Count', 'Total Time Logged (hours)', 'story_points']


def audit(path):
    result = dict.fromkeys(['rows', 'positive_logged_hours', 'positive_story_points',
                           'valid_completed_dates', 'hours_equal_worklog_total_div_3600',
                           'worklog_total_equals_count', 'positive_hours_below_one_minute'], 0)
    projects = set()
    for frame in pd.read_csv(path, usecols=COLUMNS, chunksize=25000):
        hours = pd.to_numeric(frame['Total Time Logged (hours)'], errors='coerce')
        raw = pd.to_numeric(frame.worklog_total, errors='coerce')
        count = pd.to_numeric(frame['Worklog Count'], errors='coerce')
        points = pd.to_numeric(frame.story_points, errors='coerce')
        start = pd.to_datetime(frame.created, errors='coerce', utc=True, format='mixed')
        end = pd.to_datetime(frame.resolutiondate, errors='coerce', utc=True, format='mixed')
        result['rows'] += len(frame)
        projects.update(frame.project_key.dropna().astype(str))
        result['positive_logged_hours'] += int((np.isfinite(hours) & hours.gt(0)).sum())
        result['positive_story_points'] += int((np.isfinite(points) & points.gt(0)).sum())
        result['valid_completed_dates'] += int((start.notna() & end.notna() & end.ge(start)).sum())
        result['hours_equal_worklog_total_div_3600'] += int(np.isclose(hours, raw / 3600, rtol=1e-8, atol=1e-10).sum())
        result['worklog_total_equals_count'] += int(np.isclose(raw, count, rtol=0, atol=1e-10).sum())
        result['positive_hours_below_one_minute'] += int((hours.gt(0) & hours.lt(1 / 60)).sum())
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
    return result | {'projects': len(projects), 'source_sha256': digest.hexdigest(),
                     'source_url': 'https://zenodo.org/records/19411554',
                     'production_approved': False,
                     'target_status': 'Unresolved: dictionary derives hours from worklog_total, but extraction reads an entry count; CSV may use another duration field',
                     'required_resolution': 'Verify or reacquire actual timeSpentSeconds from original issue/worklog records'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    print(json.dumps(audit(parser.parse_args().source), indent=2, allow_nan=False))
