"""Rehearse populated database/object recovery in fresh, isolated local databases.

Requires PREDICTIQ_TEST_DATABASE_URL on 127.0.0.1:15439. Never touches its
existing database: creates two uniquely named databases and retains evidence.
Run: python scripts/rehearse_recovery.py --output .tools/recovery-NEW
"""
import argparse
import asyncio
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TABLES = ('profiles', 'document_uploads', 'estimates', 'share_links', 'budgets')
HEAD = '006_manual_budgets'


def local_connection(dsn):
    parsed = urlsplit(dsn)
    if (parsed.scheme not in {'postgres', 'postgresql'} or parsed.hostname != '127.0.0.1'
            or parsed.port != 15439 or parsed.path != '/predictiq_integration' or parsed.query or parsed.fragment):
        raise ValueError('Recovery rehearsal requires the isolated local integration endpoint')
    return {'host': '127.0.0.1', 'port': 15439, 'user': unquote(parsed.username or ''),
            'password': unquote(parsed.password or '')}


async def fingerprints(connection):
    # Timestamptz JSON otherwise depends on each server's session timezone.
    await connection.execute("SET TIME ZONE 'UTC'")
    result = {}
    for table in TABLES:
        # Table identifiers are fixed above, never supplied by callers.
        rows = await connection.fetch(f'SELECT row_to_json(t)::text AS value FROM {table} t ORDER BY id')
        result[table] = {'rows': len(rows), 'sha256': hashlib.sha256(
            '\n'.join(row['value'] for row in rows).encode()).hexdigest()}
    return result


async def rehearse(dsn, output, pg_bin):
    import asyncpg

    params = local_connection(dsn)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    suffix = uuid.uuid4().hex[:12]
    source, target = f'predictiq_rehearsal_{suffix}', f'predictiq_restored_{suffix}'
    admin = await asyncpg.connect(**params, database='postgres')
    try:
        await admin.execute(f'CREATE DATABASE {source}')
        await admin.execute(f'CREATE DATABASE {target}')
    finally:
        await admin.close()
    env = os.environ | {'PGHOST': params['host'], 'PGPORT': str(params['port']),
                        'PGUSER': params['user'], 'PGPASSWORD': params['password'], 'APP_ENV': 'test',
                        'DATABASE_URL': dsn.rsplit('/', 1)[0] + '/' + source}
    started = time.monotonic()
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], cwd=ROOT / 'backend',
                   env=env, check=True, capture_output=True, timeout=120)
    connection = await asyncpg.connect(**params, database=source)
    payload = b'Recovery fixture: create accounts, manage tasks, search records and export reports.'
    key = f'documents/{uuid.uuid4().hex}.txt'
    original = output / 'objects-original' / key
    original.parent.mkdir(parents=True)
    original.write_bytes(payload)
    try:
        owner = 'recovery-' + suffix
        await connection.execute('INSERT INTO profiles(id,full_name) VALUES($1,$2)', owner, 'Recovery fixture')
        document = await connection.fetchval('INSERT INTO document_uploads(user_id,storage_path,original_filename,file_size_bytes,mime_type) VALUES($1,$2,$3,$4,$5) RETURNING id', owner, key, 'fixture.txt', len(payload), 'text/plain')
        estimate = await connection.fetchval('INSERT INTO estimates(user_id,document_id,project_name,inputs_json,outputs_json,model_version) VALUES($1,$2,$3,$4,$5,$6) RETURNING id', owner, document, 'Recovery fixture', json.dumps({'size_fp': 50}), json.dumps({'effort_likely_hours': 100}), 'recovery-fixture')
        await connection.execute('INSERT INTO share_links(estimate_id,token) VALUES($1,$2)', estimate, uuid.uuid4().hex)
        await connection.execute('INSERT INTO budgets(user_id,inputs_json) VALUES($1,$2)', owner,
                                 json.dumps({'project_name': 'Recovery budget', 'contingency_pct': '0',
                                             'tasks': [{'name': 'Review', 'low_hours': '1', 'likely_hours': '2',
                                                        'high_hours': '3', 'hourly_rate_usd': '75'}]}))
        before = await fingerprints(connection)
        if await connection.fetchval('SELECT version_num FROM alembic_version') != HEAD:
            raise ValueError('Unexpected migration head')
    finally:
        await connection.close()
    def pg(tool, *args):
        executable = Path(pg_bin) / (tool + ('.exe' if os.name == 'nt' else ''))
        subprocess.run([str(executable), *args], env=env, check=True, capture_output=True, timeout=120)
    pg('pg_dump', '-d', source, '-Fc', '-f', str(output / 'database.dump'))
    shutil.copytree(output / 'objects-original', output / 'objects-backup')
    restore_started = time.monotonic()
    pg('pg_restore', '-d', target, '--exit-on-error', str(output / 'database.dump'))
    shutil.copytree(output / 'objects-backup', output / 'objects-restored')
    restored = await asyncpg.connect(**params, database=target)
    try:
        after = await fingerprints(restored)
        if before != after or await restored.fetchval('SELECT version_num FROM alembic_version') != HEAD:
            raise ValueError('Restored database differs from populated source')
        restored_key = await restored.fetchval('SELECT storage_path FROM document_uploads WHERE id=$1', document)
        if restored_key != key or (output / 'objects-restored' / key).read_bytes() != payload:
            raise ValueError('Restored document bytes or reference differ')
    finally:
        await restored.close()
    report = {'status': 'passed', 'migration_head': HEAD, 'tables': before,
              'object_sha256': hashlib.sha256(payload).hexdigest(),
              'restore_seconds': round(time.monotonic() - restore_started, 3),
              'total_seconds': round(time.monotonic() - started, 3),
              'source_database': source, 'restored_database': target,
              'scope': 'Synthetic isolated PostgreSQL and local-object recovery; not live Neon/S3 disaster recovery'}
    (output / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--pg-bin', default='C:/Program Files/PostgreSQL/18/bin' if os.name == 'nt' else '/usr/bin')
    args = parser.parse_args()
    report = asyncio.run(rehearse(os.environ.get('PREDICTIQ_TEST_DATABASE_URL', ''), args.output, args.pg_bin))
    print(json.dumps(report, indent=2))
