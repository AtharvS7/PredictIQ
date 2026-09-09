import hashlib

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


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_original_training_data_is_blocked(tmp_path, newline):
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "ml" / "predictiq_merged_dataset.csv"
    copy = tmp_path / "training.csv"
    copy.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", newline))
    with pytest.raises(ValueError, match="revoked"):
        require_unrevoked(copy, REVOKED_DATA_SHA256)
