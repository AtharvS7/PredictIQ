"""Revocations backed by the source-label audit in docs/ml_rebuild_2026-09-09.md."""
import hashlib
from pathlib import Path

REVOKED_MODEL_SHA256 = frozenset({
    "9a37c92211b59bdc38af68fc22974ced9fba2e0f329805d425d29cb9f9650738",
})
REVOKED_DATA_SHA256 = frozenset({
    "fb3f923e5cd3ab7ed1567a2cf9a343dc0b900ada3460aec33a696f46ff695e01",
    # Git autocrlf checkouts preserve the same invalid labels.
    "3a0ebd89e2855a347521549e79546b1c51509aecc56ac3a72b72cfe2cfad066f",
})


def require_unrevoked(path: Path, revoked: frozenset[str]) -> None:
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest in revoked:
        raise ValueError("Artifact revoked: confirmed corrupted training labels. See ML rebuild report.")
