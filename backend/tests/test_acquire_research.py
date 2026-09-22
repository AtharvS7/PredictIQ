import hashlib
import io

import pytest
from ml.acquire_research import fetch_snapshot


def test_checksum_failure_does_not_publish_or_leave_partial_download(tmp_path, monkeypatch):
    monkeypatch.setattr('ml.acquire_research.urlopen', lambda *a, **k: io.BytesIO(b'bad'))
    with pytest.raises(ValueError, match='checksum'):
        fetch_snapshot(tmp_path / 'source.csv', 'https://example.test/data', '0' * 64, 3)
    assert list(tmp_path.iterdir()) == []


def test_existing_different_file_is_never_overwritten(tmp_path):
    path = tmp_path / 'source.csv'
    path.write_bytes(b'preserve')
    with pytest.raises(ValueError, match='Existing'):
        fetch_snapshot(path, 'https://example.test/data', '0' * 64, 3)
    assert path.read_bytes() == b'preserve'


def test_verified_download_can_be_reused_offline(tmp_path, monkeypatch):
    monkeypatch.setattr('ml.acquire_research.urlopen', lambda *a, **k: io.BytesIO(b'data'))
    path = tmp_path / 'source.csv'
    checksum = hashlib.sha256(b'data').hexdigest()
    fetch_snapshot(path, 'https://example.test/data', checksum, 4)
    monkeypatch.setattr('ml.acquire_research.urlopen', lambda *a, **k: pytest.fail('unexpected network'))
    fetch_snapshot(path, 'https://example.test/data', checksum, 4)
    assert path.read_bytes() == b'data'
