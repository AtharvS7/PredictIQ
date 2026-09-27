"""Production ML contracts using synthetic fixtures, never accuracy evidence."""
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


@pytest.mark.parametrize('gates', [
    {'mdape': True}, {'invented_gate': True},
    dict.fromkeys(['baseline_improvement', 'mdape', 'pred25', 'coverage',
                   'useful_intervals', 'organization_slices'], 'false'),
    dict.fromkeys(['baseline_improvement', 'mdape', 'pred25', 'coverage',
                   'useful_intervals', 'organization_slices'], 1),
])
def test_serving_requires_every_named_gate_as_boolean_true(tmp_path, monkeypatch, gates):
    import sklearn

    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({
        'schema': SCHEMA, 'features': FEATURES, 'sklearn_version': sklearn.__version__,
        'production_approved': True, 'reviewer': 'test reviewer', 'approval_evidence': 'test only',
        'eligible_for_review': True, 'gates': gates,
    }))
    def must_not_unpickle(*args):
        pytest.fail('Malformed approval gates reached deserialization')
    monkeypatch.setattr('ml.production_serving.pickle.loads', must_not_unpickle)
    with pytest.raises(ValueError, match='Unapproved'):
        ProductionBundle(manifest, digest(manifest))


def test_training_writes_unapproved_bundle_with_real_preprocessing(source_manifest, tmp_path, monkeypatch):
    """Exercise fitting/export without mistaking fixture rows for real projects."""
    import pickle

    import numpy as np
    from ml import production_pipeline
    from sklearn.linear_model import Ridge
    from sklearn.model_selection import GridSearchCV

    manifest, source, payload = source_manifest
    rows = []
    rng = np.random.default_rng(17)
    for i in range(1000):
        size = float(rng.uniform(10, 500))
        partition = 'train' if i < 600 else 'calibration' if i < 750 else 'external_test'
        row = dict(zip(FEATURES, [size, 5, 10, 2, 3, 2, 'Web App', 'Medium', 'Agile']))
        row.update(project_id=f'fixture-{i}', organization_id=f'{partition}-{i % (5 if partition == "train" else 2)}',
                   effort_hours=float(np.expm1(2 + .004 * size)), partition=partition,
                   planning_date='2022-01-01' if partition == 'external_test' else '2020-01-01',
                   completion_date='2022-06-01' if partition == 'external_test' else '2020-06-01')
        rows.append(row)
    pd.DataFrame(rows).to_csv(source, index=False)
    payload['sources'][0]['sha256'] = digest(source)
    manifest.write_text(json.dumps(payload), encoding='utf-8')

    def focused_search(estimator, grid, **kwargs):
        # Keep actual grouped CV/preprocessing; bound this regression to one model.
        return GridSearchCV(estimator, {'regressor__model': [Ridge()], 'regressor__model__alpha': [.1]}, **kwargs)

    monkeypatch.setattr(production_pipeline, 'GridSearchCV', focused_search)
    destination = tmp_path / 'candidate'
    report = train(manifest, destination)
    assert report['production_approved'] is False
    assert report['counts'] == {'train': 600, 'external_test': 250, 'calibration': 150}
    assert report['features'] == FEATURES
    assert report['model_sha256'] == digest(destination / 'pipeline.pkl')
    # This pickle was produced in this test, never read from an untrusted source.
    model = pickle.loads((destination / 'pipeline.pkl').read_bytes())
    prediction = model.predict(pd.DataFrame(rows[:2])[FEATURES])
    assert np.isfinite(prediction).all() and (prediction > 0).all()
    with pytest.raises(ValueError, match='Unapproved'):
        ProductionBundle(destination / 'manifest.json', digest(destination / 'manifest.json'))


def test_valid_boolean_gate_manifest_can_load_trusted_fixture(tmp_path):
    """Strict approval typing must not disable legitimate serving contracts."""
    import pickle

    import sklearn
    from ml.production_pipeline import CATEGORICAL, NUMERIC, REQUIRED_GATES
    from sklearn.dummy import DummyRegressor

    params = dict(zip(FEATURES, [100, 5, 10, 2, 3, 2, 'Web App', 'Medium', 'Agile']))
    frame = pd.DataFrame([params], columns=FEATURES)
    model = DummyRegressor(strategy='constant', constant=100).fit(frame, [100])
    artifact = tmp_path / 'pipeline.pkl'
    artifact.write_bytes(pickle.dumps(model))
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({
        'schema': SCHEMA, 'features': FEATURES, 'sklearn_version': sklearn.__version__,
        'production_approved': True, 'reviewer': 'synthetic contract test',
        'approval_evidence': 'not real accuracy evidence', 'eligible_for_review': True,
        'gates': dict.fromkeys(REQUIRED_GATES, True), 'log_radius': .1,
        'interval_coverage': .9, 'model_sha256': digest(artifact),
        'ranges': {k: [0, 1000] for k in NUMERIC},
        'categories': {k: [params[k]] for k in CATEGORICAL},
    }))
    result = ProductionBundle(manifest, digest(manifest)).predict(params)
    assert result['effort_hours_min'] < result['effort_hours_likely'] == 100
    assert result['effort_hours_max'] > 100
