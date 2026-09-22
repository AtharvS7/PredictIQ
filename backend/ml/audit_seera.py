"""Audit SEERA's derived effort target without training or promoting a model."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ARCHIVE_SHA256 = '4eb4ccd32d3c6d86f0ef6a8feec6ad823a0feae56556aa54b622ff94119dcc75'
MEMBER = ('The SEERA Dataset/INFSOF Article May 2024 Files/'
          'SEERA cost estimation dataset for prediction.csv')


def audit_frame(frame):
    columns = ['Actual duration', 'Actual effort', 'Team size',
               'Dedicated team members', 'Daily working hours']
    values = frame[columns].apply(pd.to_numeric, errors='raise')
    if values.empty or not np.isfinite(values).all().all() or (values < 0).any().any():
        raise ValueError('Invalid effort evidence')
    if (values['Dedicated team members'] > values['Team size']).any():
        raise ValueError('Dedicated members exceed total team size')
    derived = (values['Actual duration'] * (values['Dedicated team members']
               + .5 * (values['Team size'] - values['Dedicated team members']))
               * values['Daily working hours'] * 22)
    return {
        'rows': len(values),
        'formula_matches': int(np.isclose(derived, values['Actual effort'], rtol=0, atol=.01).sum()),
        'max_absolute_difference_hours': float(abs(derived - values['Actual effort']).max()),
        'formula': 'actual_duration * (dedicated + 0.5 * (team - dedicated)) * daily_hours * 22',
        'target_provenance': 'Formula documented by dataset authors; not independently logged effort',
        'production_approved': False,
        'source_url': 'https://zenodo.org/records/4312777',
    }


def audit_archive(path):
    path = Path(path)
    if path.stat().st_size != 3311539:
        raise ValueError('Unreviewed SEERA archive size')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != ARCHIVE_SHA256:
        raise ValueError('Unreviewed SEERA archive checksum')
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        frame = pd.read_csv(io.BytesIO(archive.read(MEMBER)))
    return audit_frame(frame) | {'archive_sha256': ARCHIVE_SHA256}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    print(json.dumps(audit_archive(parser.parse_args().archive), indent=2, allow_nan=False))
