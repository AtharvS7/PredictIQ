"""Read-only original-record checks of a deterministic Itemlet sample.

Only reviewed public Jira hosts are queried. No credentials, descriptions or
user information are requested or saved. Sample agreement cannot approve a
dataset or demonstrate planning-time feature availability.
"""
import argparse
import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

import pandas as pd

from ml.acquire_research import ITEMLET

PROJECT_HOSTS = {
    'AAF': 'lf-onap.atlassian.net', 'AAI': 'lf-onap.atlassian.net',
    'APPC': 'lf-onap.atlassian.net', 'CCSDK': 'lf-onap.atlassian.net',
    'CRUC': 'jira.atlassian.com', 'FE': 'jira.atlassian.com',
    'BAM': 'jira.atlassian.com', 'BSERV': 'jira.atlassian.com',
}


class NoRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def compare_record(issue_key, expected_hours, payload):
    if not math.isfinite(expected_hours) or expected_hours <= 0:
        raise ValueError('Positive finite reference hours required')
    if not isinstance(payload, dict) or payload.get('key') != issue_key:
        raise ValueError('Original record identity mismatch')
    fields = payload.get('fields')
    if not isinstance(fields, dict):
        raise ValueError('Original fields missing')
    tracking = fields.get('timetracking') or {}
    if not isinstance(tracking, dict):
        raise ValueError('Malformed time tracking')
    values = [value for value in [fields.get('timespent'), tracking.get('timeSpentSeconds')] if value is not None]
    if not values:
        return {'status': 'missing_duration'}
    if any(type(value) not in (int, float) or not math.isfinite(value) or value < 0 for value in values):
        raise ValueError('Invalid original seconds')
    if len(set(values)) != 1:
        return {'status': 'conflicting_original_duration'}
    hours = values[0] / 3600
    # CSV decimal serialization can differ by a fraction of a second.
    return {'status': 'matched' if math.isclose(hours, expected_hours, rel_tol=0, abs_tol=1 / 3600) else 'different',
            'original_hours': hours, 'csv_hours': expected_hours}


def fetch_record(project, issue_key):
    if project not in PROJECT_HOSTS or not re.fullmatch(re.escape(project) + r'-[0-9]+', issue_key):
        raise ValueError('Unreviewed project or invalid issue identity')
    url = f'https://{PROJECT_HOSTS[project]}/rest/api/2/issue/{issue_key}?fields=timespent,timetracking'
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'PredictIQ-research-verification/1.0'})
    with build_opener(NoRedirects()).open(request, timeout=15) as response:
        if 'application/json' not in response.headers.get('Content-Type', '').lower():
            raise ValueError('Original endpoint did not return JSON')
        content = response.read(200001)
        if len(content) > 200000:
            raise ValueError('Original response exceeds limit')
        return json.loads(content)


def select_sample(frame, per_project=3):
    if not 1 <= per_project <= 5:
        raise ValueError('Use one to five checks per reviewed project')
    rows = []
    for project, group in frame.groupby('project_key'):
        if project not in PROJECT_HOSTS:
            continue
        group = group.loc[group['Total Time Logged (hours)'].gt(0)].copy()
        group['selection_hash'] = group.issue_key.map(lambda key: hashlib.sha256(str(key).encode()).hexdigest())
        rows.extend(group.sort_values('selection_hash').head(per_project).to_dict('records'))
    return rows


def run(source, output):
    output = Path(output)
    if output.exists():
        raise ValueError('Use a new evidence path')
    with Path(source).open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ITEMLET[2]:
            raise ValueError('Unreviewed dataset snapshot')
    frame = pd.read_csv(source, usecols=['issue_key', 'project_key', 'Total Time Logged (hours)'])
    rows = []
    for row in select_sample(frame):
        key, project = row['issue_key'], row['project_key']
        try:
            checked = compare_record(key, row['Total Time Logged (hours)'], fetch_record(project, key))
        except HTTPError as exc:
            checked = {'status': 'unavailable', 'http_status': exc.code}
        except (OSError, ValueError) as exc:
            checked = {'status': 'unavailable', 'error_type': type(exc).__name__}
        rows.append({'issue_key': key, 'project': project, 'host': PROJECT_HOSTS[project], **checked})
        print(f'{key}: {checked["status"]}', flush=True)
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'source_sha256': ITEMLET[2],
              'selection': 'first three positive-hour issues per reviewed project ordered by SHA-256(issue_key)',
              'records': rows, 'counts': pd.Series([row['status'] for row in rows]).value_counts().to_dict(),
              'production_approved': False,
              'limitations': ['Restricted sample covers only reachable reviewed hosts; not all 204 projects',
                              'Current time totals may have changed since dataset collection',
                              'Agreement does not establish complete worklogs or planning-time feature history']}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as destination:
        json.dump(report, destination, indent=2, allow_nan=False)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    report = run(**vars(parser.parse_args()))
    print(json.dumps(report['counts']))
