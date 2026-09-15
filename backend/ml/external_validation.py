"""Import 104 real AT&T projects and evaluate frozen candidates on a new source.

Download aptness.dat.txt from https://jse.amstat.org/datasets/aptness.dat.txt
to ml/data/research/aptness.dat.txt. Run: python -m ml.external_validation.
No source rows or artifacts are approved for production redistribution.
"""
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from ml.train_research import ROOT, metrics


def read_att(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep=r'\s+', header=None)
    if frame.shape != (104, 5):
        raise ValueError('Expected 104 AT&T project rows and five source columns')
    frame.columns = ['size_fp', 'effort_hours', 'operating_system', 'database_system', 'language']
    if not np.isfinite(frame.to_numpy()).all() or (frame[['size_fp', 'effort_hours']] <= 0).any().any():
        raise ValueError('Invalid project size or effort')
    for column, allowed in [('operating_system', {0, 1}), ('database_system', {1, 2, 3, 4, 5}), ('language', {1, 2, 3, 4})]:
        if not set(frame[column]).issubset(allowed):
            raise ValueError(f'Unknown category in {column}')
    frame['source'] = 'att_matson'
    frame['project_id'] = frame.index.astype(str)
    return frame


def main():
    path = ROOT / 'data/research/aptness.dat.txt'
    external = read_att(path)
    development = pd.read_csv(ROOT / 'experiments/reconstructed-v1/projects.csv')
    # A matching size/effort pair is conservatively treated as potential overlap.
    previous = set(zip(development.size_fp, development.effort_hours))
    overlap = np.array([(s, e) in previous for s, e in zip(external.size_fp, external.effort_hours)])
    eligible = external.loc[~overlap]
    if eligible.empty:
        raise ValueError('No independent external records')
    results = {}
    for name, directory in [('baseline', 'reconstructed-v1'), ('tuned', 'tuned-v1')]:
        model_path = ROOT / 'experiments' / directory / 'candidate.pkl'
        # Only locally generated experiment artifacts, never downloaded pickle data.
        model = pickle.loads(model_path.read_bytes())
        results[name] = {'artifact_sha256': hashlib.sha256(model_path.read_bytes()).hexdigest(),
                         'metrics': metrics(eligible.effort_hours, model.predict(eligible[['size_fp']]))}
    development['partition'] = 'development_previously_evaluated'
    external['partition'] = np.where(overlap, 'overlap_excluded', 'external_evaluation')
    combined = pd.concat([development, external], ignore_index=True)
    destination = ROOT / 'experiments/expanded-v2'
    destination.mkdir(parents=True, exist_ok=True)
    combined.to_csv(destination / 'projects.csv', index=False)
    report = {'rows': len(combined), 'external_rows': len(external), 'excluded_overlap': int(overlap.sum()),
              'source_url': 'https://jse.amstat.org/datasets/aptness.dat.txt',
              'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
              'available_att_inputs': ['size_fp', 'operating_system', 'database_system', 'language'],
              'evaluated_model_inputs': ['size_fp'], 'target': 'effort_hours',
              'results': results, 'production_approved': False,
              'limitations': ['Historical 1986–1991 projects; not modern prospective validation',
                             'Additional categorical features missing in earlier sources',
                             'Source license and measurement harmonization not cleared',
                             'External outcomes are now observed; do not tune against them']}
    (destination / 'external_evaluation.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
