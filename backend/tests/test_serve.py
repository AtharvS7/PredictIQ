import pytest
from serve import port_from_environment


def test_provider_port_is_used(monkeypatch):
    monkeypatch.setenv('PORT', '9123')
    assert port_from_environment() == 9123


def test_default_port(monkeypatch):
    monkeypatch.delenv('PORT', raising=False)
    assert port_from_environment() == 8000


@pytest.mark.parametrize('value', ['0', '65536', 'not-a-port'])
def test_invalid_port_fails_before_startup(monkeypatch, value):
    monkeypatch.setenv('PORT', value)
    with pytest.raises(ValueError):
        port_from_environment()
