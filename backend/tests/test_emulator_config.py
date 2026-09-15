import pytest
from app.core.config import Settings


@pytest.mark.parametrize('environment', ['production', 'staging', 'development'])
def test_emulator_tokens_cannot_be_enabled_in_application_environments(monkeypatch, environment):
    monkeypatch.setenv('FIREBASE_AUTH_EMULATOR_HOST', '127.0.0.1:9099')
    with pytest.raises(ValueError, match='isolated test'):
        Settings(_env_file=None, DATABASE_URL='postgresql://localhost/test', APP_ENV=environment)


def test_emulator_allowed_for_isolated_tests(monkeypatch):
    monkeypatch.setenv('FIREBASE_AUTH_EMULATOR_HOST', '127.0.0.1:9099')
    assert Settings(_env_file=None, DATABASE_URL='postgresql://localhost/test', APP_ENV='test')
