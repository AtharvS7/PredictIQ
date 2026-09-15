"""Production ML regression specifications; execution is deferred by owner instruction.

These tests exercise intake and pre-unpickle checks, never fit a model.
"""
import json

import pandas as pd
import pytest
from ml.production_pipeline import FEATURES, SCHEMA, digest, load_projects, train
from ml.production_serving import ProductionBundle


@pytest.fixture
def source_manifest(tmp_path):
    row = dict(zip(FEATURES, [100, 5, 10, 2, 3, 2, 'Web App', 'Medium', 'Agile']))
    row.update(project_id='project-1', organization_id='org-1', effort_hours=1000,
               partition='train', planning_date='2021-01-01', completion_date='2021-06-01')
    source = tmp_path / 'projects.csv'
    pd.DataFrame([row]).to_csv(source, index=False)
    manifest = tmp_path / 'sources.json'
    payload = {'sources': [{'name': 'synthetic-test-only', 'path': source.name,
                           'sha256': digest(source), 'schema': SCHEMA,
                           'grain': 'completed_project', 'effort_unit': 'person_hours',
                           'rights_approved': True, 'license_evidence': 'test fixture',
                           'feature_parity_evidence': 'test fixture', 'features_recorded_at': 'planning'}]}
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    return manifest, source, payload


def test_intake_rejects_unapproved_rights(source_manifest):
    manifest, _, payload = source_manifest
    payload['sources'][0]['rights_approved'] = False
    manifest.write_text(json.dumps(payload), encoding='utf-8')
    with pytest.raises(ValueError, match='licensed'):
        load_projects(manifest)


def test_intake_detects_source_tampering(source_manifest):
    manifest, source, _ = source_manifest
    source.write_text('modified', encoding='utf-8')
    with pytest.raises(ValueError, match='checksum'):
        load_projects(manifest)


def test_small_dataset_cannot_start_training(source_manifest, tmp_path):
    manifest, _, _ = source_manifest
    with pytest.raises(ValueError, match='1000 genuine projects'):
        train(manifest, tmp_path / 'candidate')
    assert not (tmp_path / 'candidate').exists()


def test_serving_rejects_unapproved_manifest_before_deserialization(tmp_path, monkeypatch):
    manifest = tmp_path / 'manifest.json'
    manifest.write_text('{}', encoding='utf-8')

    def must_not_unpickle(*args):
        pytest.fail('Unapproved bundle reached pickle deserialization')

    monkeypatch.setattr('ml.production_serving.pickle.loads', must_not_unpickle)
    with pytest.raises(ValueError, match='Unapproved'):
        ProductionBundle(manifest, digest(manifest))
