"""Serving contract for reviewed, hash-pinned prospective pipeline bundles.

Pickle is executable: only trusted local training output may be deployed.
Neither this module nor the training CLI approves its own output.
"""
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn

from ml.production_pipeline import CATEGORICAL, FEATURES, NUMERIC, SCHEMA


class ProductionBundle:
    def __init__(self, manifest_path, expected_hash):
        path = Path(manifest_path).resolve()
        content = path.read_bytes()
        if not expected_hash or hashlib.sha256(content).hexdigest() != expected_hash:
            raise ValueError('Deployment manifest checksum mismatch')
        report = json.loads(content)
        if (report.get('schema') != SCHEMA or report.get('features') != FEATURES
                or report.get('sklearn_version') != sklearn.__version__
                or report.get('production_approved') is not True
                or not report.get('reviewer') or not report.get('approval_evidence')
                or report.get('eligible_for_review') is not True
                or not report.get('gates') or not all(report['gates'].values())):
            raise ValueError('Unapproved or incompatible pipeline manifest')
        if not np.isfinite(report['log_radius']) or report['log_radius'] < 0:
            raise ValueError('Invalid calibration radius')
        if not 0 <= report['interval_coverage'] <= 1:
            raise ValueError('Invalid coverage')
        for feature in NUMERIC:
            low, high = report['ranges'][feature]
            if not np.isfinite([low, high]).all() or low > high:
                raise ValueError('Invalid feature range')
        model_bytes = (path.parent / 'pipeline.pkl').read_bytes()
        if hashlib.sha256(model_bytes).hexdigest() != report['model_sha256']:
            raise ValueError('Pipeline checksum mismatch')
        self.model = pickle.loads(model_bytes)
        self.report = report
        self.version = 'production-v3-' + expected_hash[:12]

    def predict(self, params):
        row = {}
        for feature in NUMERIC:
            value = params.get(feature)
            if value is None or isinstance(value, bool):
                raise ValueError(f'Missing numeric feature: {feature}')
            value = float(value)
            low, high = self.report['ranges'][feature]
            if not np.isfinite(value) or not low <= value <= high:
                raise ValueError(f'Feature outside validated range: {feature}')
            row[feature] = value
        for feature in CATEGORICAL:
            value = params.get(feature)
            if value not in self.report['categories'][feature]:
                raise ValueError(f'Unknown category: {feature}')
            row[feature] = value
        output = np.asarray(self.model.predict(pd.DataFrame([row], columns=FEATURES)))
        if output.shape != (1,) or not np.isfinite(output).all() or output[0] <= 0:
            raise RuntimeError('Invalid model output')
        likely = float(output[0])
        with np.errstate(over='raise', invalid='raise'):
            low = max(0.0, float(np.expm1(np.log1p(likely) - self.report['log_radius'])))
            high = float(np.expm1(np.log1p(likely) + self.report['log_radius']))
        return {'effort_hours_likely': likely, 'effort_hours_min': low, 'effort_hours_max': high,
                'confidence_pct': self.report['interval_coverage'] * 100,
                'confidence_method': 'external_interval_coverage_not_individual_accuracy',
                'interval_method': 'split_conformal_log_residual', 'model_mode': 'live',
                'model_name': self.version}

    def get_model_info(self):
        return {'model_loaded': True, 'model_mode': 'live', 'model_version': self.version,
                'best_model': self.version, 'n_features': len(FEATURES),
                'training_samples': self.report['counts']['train'],
                'confidence_method': 'external_interval_coverage_not_individual_accuracy',
                'interval_method': 'split_conformal_log_residual'}
