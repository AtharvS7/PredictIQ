"""Fetch reviewed research snapshots with bounded downloads and SHA-256 checks.

Run from backend: python -m ml.acquire_research
Data remain local; availability does not imply production approval.
"""
import hashlib
import tempfile
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent / 'data/research'
SNAPSHOTS = [
    ('sip/Sip-task-info.csv', 'https://raw.githubusercontent.com/Derek-Jones/SiP_dataset/master/Sip-task-info.csv',
     '28621aa8b0ce05c270085a78e96a4d37f1bb39c1a5d260059ff3c197de961a4a', 1699689),
    ('sip/est-act-dates.csv', 'https://raw.githubusercontent.com/Derek-Jones/SiP_dataset/master/est-act-dates.csv',
     '4d5a5ea633969dd782ab3d6b2b0c6cf2fcc65d9bb1c22f332ac7d9abf5ead1e9', 409164),
    ('josse/JOSSE_18092020.sqlite3', 'https://raw.githubusercontent.com/ml-see/josse/main/JOSSE_18092020.sqlite3',
     '38f9ed6021889d99a322a62f878d202eed8dad278144807a4cd74ff58943a30f', 26566656),
    ('josse/LICENSE.md', 'https://raw.githubusercontent.com/ml-see/josse/main/LICENSE.md',
     'e245e22cc4ac72353781c345657077c5c0306131859e9cfd38174e27f41eb443', 1109),
]


def fetch_snapshot(destination, url, expected_hash, expected_bytes):
    destination = Path(destination)
    if destination.exists():
        if destination.stat().st_size != expected_bytes or hashlib.sha256(destination.read_bytes()).hexdigest() != expected_hash:
            raise ValueError('Existing snapshot differs; preserve it and review manually')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.partial', delete=False) as out:
            temporary = Path(out.name)
            digest, size = hashlib.sha256(), 0
            with urlopen(url, timeout=60) as response:
                while chunk := response.read(65536):
                    size += len(chunk)
                    if size > expected_bytes:
                        raise ValueError('Download exceeds reviewed snapshot size')
                    digest.update(chunk)
                    out.write(chunk)
        if size != expected_bytes or digest.hexdigest() != expected_hash:
            raise ValueError('Downloaded snapshot checksum or size mismatch')
        # Exclusive target creation avoids silently replacing another writer's file.
        with destination.open('xb') as final:
            final.write(temporary.read_bytes())
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    for name, url, checksum, size in SNAPSHOTS:
        fetch_snapshot(ROOT / name, url, checksum, size)
        print(f'Verified {name}', flush=True)
