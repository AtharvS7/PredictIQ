"""Fetch reviewed research snapshots with bounded downloads and SHA-256 checks.

Run from backend: python -m ml.acquire_research
Data remain local; availability does not imply production approval.
"""
import argparse
import hashlib
import shutil
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
ITEMLET = ('itemlet/itemlet_dataset.csv',
           'https://zenodo.org/records/19411554/files/itemlet_dataset.csv?download=1',
           'f03d31866326a89690fa43c806bfc75b527e014de21c438e8d2bbe59dd3faf4a', 438479440)


def fetch_snapshot(destination, url, expected_hash, expected_bytes):
    destination = Path(destination)
    if destination.exists():
        with destination.open('rb') as existing:
            checksum = hashlib.file_digest(existing, 'sha256').hexdigest()
        if destination.stat().st_size != expected_bytes or checksum != expected_hash:
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
            with temporary.open('rb') as verified:
                shutil.copyfileobj(verified, final, length=65536)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--itemlet', action='store_true', help='Also fetch the 438 MB intake-only Itemlet snapshot')
    args = parser.parse_args()
    for name, url, checksum, size in SNAPSHOTS + ([ITEMLET] if args.itemlet else []):
        fetch_snapshot(ROOT / name, url, checksum, size)
        print(f'Verified {name}', flush=True)
