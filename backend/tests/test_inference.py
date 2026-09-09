"""Inference regressions: invalid predictions must never become estimates."""
import json
import pickle
from unittest.mock import Mock

import numpy as np
import pytest
from ml.inference import EXPECTED_FEATURES, MLUnavailableError, PredictifyInference


class IdentityScaler:
    n_features_in_ = 27
    feature_names_in_ = EXPECTED_FEATURES
    def transform(self, vector):
        return vector

class ConstantModel:
    n_features_in_ = 27
    def predict(self, vector):
        return np.array([np.log1p(1000.0)])

@pytest.fixture
def engine():
    model = PredictifyInference()
    model.model = ConstantModel()
    model.scaler = IdentityScaler()
    model.feature_names = EXPECTED_FEATURES.copy()
    model.n_features = 27
    model.is_ready = True
    return model

@pytest.fixture
def artifacts(tmp_path):
    for name, value in [('model.pkl', ConstantModel()), ('scaler.pkl', IdentityScaler())]:
        (tmp_path / name).write_bytes(pickle.dumps(value))
    (tmp_path / 'features.json').write_text(json.dumps(EXPECTED_FEATURES))
    return [tmp_path / name for name in ('model.pkl', 'scaler.pkl', 'features.json')]

def test_live_inverse_transform_and_exact_feature_order(engine, sample_feature_vector):
    engine.scaler = Mock(wraps=IdentityScaler())
    result = engine.predict(dict(reversed(list(sample_feature_vector.items()))))
    assert result['model_mode'] == 'live'
    assert result['confidence_method'] == 'heuristic_not_calibrated_probability'
    assert engine.get_model_info()['interval_method'] == 'heuristic_0.8x_1.4x_with_clamps'
    assert result['effort_hours_likely'] == 1000
    assert result['effort_hours_min'] == 800
    assert result['effort_hours_max'] == 1400
    actual = engine.scaler.transform.call_args.args[0]
    np.testing.assert_array_equal(actual, [[sample_feature_vector[key] for key in EXPECTED_FEATURES]])

def test_unloaded_model_fails_closed():
    model = PredictifyInference()
    with pytest.raises(MLUnavailableError):
        model.predict({})
    assert model.get_model_info()['model_mode'] == 'unavailable'

@pytest.mark.parametrize('value', [float('nan'), float('inf'), float('-inf'), None, 'invalid'])
def test_invalid_features_fail_closed(engine, sample_feature_vector, value):
    sample_feature_vector['size_fp'] = value
    with pytest.raises(MLUnavailableError):
        engine.predict(sample_feature_vector)

def test_missing_features_are_not_silently_zero_filled(engine, sample_feature_vector):
    del sample_feature_vector['T01']
    with pytest.raises(MLUnavailableError):
        engine.predict(sample_feature_vector)

@pytest.mark.parametrize('output', [[float('nan')], [float('inf')], [1000.0], [-1.0], [], [[1.0]]])
def test_invalid_prediction_fails_closed(engine, sample_feature_vector, output):
    engine.model = Mock()
    engine.model.predict.return_value = output
    with pytest.raises(MLUnavailableError):
        engine.predict(sample_feature_vector)

def test_scaler_failure_fails_closed(engine, sample_feature_vector):
    engine.scaler = Mock()
    engine.scaler.transform.side_effect = ValueError('internal detail')
    with pytest.raises(MLUnavailableError, match='Prediction service is unavailable'):
        engine.predict(sample_feature_vector)

def test_compatible_artifacts_load(artifacts):
    model = PredictifyInference()
    assert model.load(*artifacts)
    assert model.is_ready

def test_reordered_metadata_rejected(artifacts):
    artifacts[2].write_text(json.dumps(list(reversed(EXPECTED_FEATURES))))
    assert not PredictifyInference().load(*artifacts)

def test_mismatched_artifact_count_rejected(artifacts):
    scaler = IdentityScaler()
    scaler.n_features_in_ = 26
    artifacts[1].write_bytes(pickle.dumps(scaler))
    assert not PredictifyInference().load(*artifacts)

def test_failed_reload_clears_ready_state(artifacts):
    model = PredictifyInference()
    assert model.load(*artifacts)
    artifacts[0].write_bytes(b'invalid pickle')
    assert not model.load(*artifacts)
    with pytest.raises(MLUnavailableError):
        model.predict(dict.fromkeys(EXPECTED_FEATURES, 1))

def test_packaged_artifacts_with_corrupted_labels_are_revoked(sample_feature_vector):
    model = PredictifyInference()
    assert not model.load(), 'Known invalid model must never serve estimates'
    assert not model.is_ready
    with pytest.raises(MLUnavailableError):
        model.predict(sample_feature_vector)

def test_failed_inference_disables_readiness(engine, sample_feature_vector):
    engine.model = Mock(predict=Mock(side_effect=ValueError('failed')))
    with pytest.raises(MLUnavailableError):
        engine.predict(sample_feature_vector)
    assert not engine.is_ready

def test_nonfinite_scaled_vector_rejected(engine, sample_feature_vector):
    engine.scaler = Mock(transform=Mock(return_value=np.full((1, 27), np.nan)))
    with pytest.raises(MLUnavailableError):
        engine.predict(sample_feature_vector)
