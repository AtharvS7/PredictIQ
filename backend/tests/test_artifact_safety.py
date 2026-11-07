import hashlib
from pathlib import Path

import pytest
from ml.artifact_safety import REVOKED_DATA_SHA256, require_unrevoked


def test_revocation_follows_content_even_after_renaming(tmp_path):
    path = tmp_path / "renamed.pkl"
    path.write_bytes(b"known-invalid-artifact")
    blocked = frozenset({hashlib.sha256(path.read_bytes()).hexdigest()})
    with pytest.raises(ValueError, match="revoked"):
        require_unrevoked(path, blocked)
    path.write_bytes(b"different-artifact")
    require_unrevoked(path, blocked)


def test_current_training_data_is_unrevoked():
    path = Path(__file__).resolve().parents[1] / "ml" / "data" / "projects_v2.csv"
    require_unrevoked(path, REVOKED_DATA_SHA256)


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_original_training_data_is_blocked(tmp_path, newline):
    backup = Path(__file__).resolve().parents[2] / ".tools" / "dev2-backup" / "backend" / "ml" / "predictiq_merged_dataset.csv"
    if backup.exists():
        raw_bytes = backup.read_bytes()
        blocked = REVOKED_DATA_SHA256
    else:
        raw_bytes = b"known-revoked-data-content"
        blocked = frozenset({hashlib.sha256(raw_bytes).hexdigest()})
    copy = tmp_path / "training.csv"
    copy.write_bytes(raw_bytes.replace(b"\r\n", b"\n").replace(b"\n", newline))
    with pytest.raises(ValueError, match="revoked"):
        require_unrevoked(copy, blocked)
