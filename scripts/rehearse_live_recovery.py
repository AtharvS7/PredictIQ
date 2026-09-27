"""Read-only Neon backup and isolated local restore with live S3 object checks.

Configuration is read only from the explicitly supplied ignored environment file.
Production is never a restore target. Cloud writes use a unique probe key only.
Private dumps and manifests must remain under the ignored .tools directory.
"""
import argparse
import asyncio
import hashlib
import json
import os
import ssl
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import unquote, urlsplit

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.rehearse_recovery import HEAD, ROOT, fingerprints, local_connection


def source_parameters(dsn):
    parsed = urlsplit(dsn)
    if (parsed.scheme not in {'postgres', 'postgresql'} or not parsed.hostname
            or not parsed.hostname.endswith('.neon.tech') or parsed.fragment):
        raise ValueError('Expected an explicit Neon source')
    return dict(host=parsed.hostname.replace('-pooler.', '.'), port=parsed.port or 5432,
                user=unquote(parsed.username or ''), password=unquote(parsed.password or ''),
                database=unquote(parsed.path.lstrip('/')))


def evidence_directory(path):
    path = Path(path).resolve()
    if not path.is_relative_to((ROOT / '.tools').resolve()):
        raise ValueError('Private recovery evidence must stay inside .tools')
    path.mkdir(parents=True, exist_ok=False)
    return path


def pg_env(params, live=False):
    # Do not inherit connection/service overrides from the operator's shell.
    env = {k: v for k, v in os.environ.items() if not k.startswith('PG')}
    env.update(PGHOST=params['host'], PGPORT=str(params['port']), PGUSER=params['user'],
               PGPASSWORD=params['password'], PGDATABASE=params['database'], PGCONNECT_TIMEOUT='15')
    if live:
        import certifi

        # libpq on Windows does not share Python's Windows trust-store support.
        env.update(PGSSLMODE='verify-full', PGSSLROOTCERT=certifi.where(),
                   PGOPTIONS='-c default_transaction_read_only=on')
    return env


def classify_missing(missing, known_missing):
    unexpected = set(missing) - set(known_missing)
    return ('blocked' if unexpected else 'passed_with_legacy_gaps' if missing else 'passed', len(unexpected))


async def rehearse(config_file, output, pg_bin, known_missing_file=None):
    import asyncpg
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
    from dotenv import dotenv_values

    config = dotenv_values(config_file)
    known_missing = [] if known_missing_file is None else json.loads(Path(known_missing_file).read_text())
    if not isinstance(known_missing, list) or not all(isinstance(value, str) for value in known_missing):
        raise ValueError('Known missing manifest must list reviewed document IDs')
    source = source_parameters(config.get('DATABASE_URL', ''))
    target = local_connection(os.environ.get('PREDICTIQ_TEST_DATABASE_URL', ''))
    output = evidence_directory(output)
    nonce = uuid.uuid4().hex
    target['database'] = 'predictiq_live_restore_' + nonce[:12]

    async def pg(tool, params, *args, live=False):
        executable = Path(pg_bin) / (tool + ('.exe' if os.name == 'nt' else ''))
        result = await asyncio.to_thread(subprocess.run, [str(executable), *args],
                                         env=pg_env(params, live), capture_output=True, timeout=120)
        if result.returncode:
            # pg errors may contain private hostnames, role names or record data.
            (output / (tool + '-private-error.log')).write_bytes(result.stderr)
            raise RuntimeError(f'{tool} failed; exit={result.returncode}')

    connection = await asyncpg.connect(**source, ssl=ssl.create_default_context(), timeout=20)
    try:
        async with connection.transaction(isolation='repeatable_read', readonly=True):
            before = await fingerprints(connection)
            head = await connection.fetchval('SELECT version_num FROM alembic_version')
            if head != HEAD:
                raise ValueError('Unexpected migration head')
            snapshot = await connection.fetchval('SELECT pg_export_snapshot()')
            await pg('pg_dump', source, '--format=custom', '--no-owner', '--no-acl',
                     '--schema=public', '--snapshot=' + snapshot,
                     '--file=' + str(output / 'database.dump'), live=True)
    finally:
        await connection.close()

    admin = await asyncpg.connect(**{**target, 'database': 'postgres'})
    try:
        # Identifier is generated internally; never accept a production restore DSN.
        await admin.execute('CREATE DATABASE ' + target['database'])
    finally:
        await admin.close()
    empty_target = await asyncpg.connect(**target)
    try:
        # This database was created immediately above with a unique generated name.
        # Drop only its empty default schema, without CASCADE, so the dump can create it.
        await empty_target.execute('DROP SCHEMA public')
    finally:
        await empty_target.close()
    await pg('pg_restore', target, '--dbname=' + target['database'], '--no-owner', '--no-acl',
             '--exit-on-error', str(output / 'database.dump'))
    restored = await asyncpg.connect(**target)
    try:
        after = await fingerprints(restored)
        if before != after or await restored.fetchval('SELECT version_num FROM alembic_version') != head:
            raise ValueError('Restored database differs from production snapshot')
        documents = await restored.fetch('SELECT id, storage_path FROM document_uploads ORDER BY id')
    finally:
        await restored.close()

    client = boto3.client('s3', endpoint_url=config['S3_ENDPOINT_URL'], region_name=config['S3_REGION'],
                         aws_access_key_id=config['S3_ACCESS_KEY_ID'],
                         aws_secret_access_key=config['S3_SECRET_ACCESS_KEY'],
                         config=Config(connect_timeout=10, read_timeout=20, retries={'max_attempts': 1},
                                       s3={'addressing_style': 'path'}))
    bucket = config['S3_BUCKET_NAME']
    missing, objects = [], []
    for document in documents:
        try:
            response = client.get_object(Bucket=bucket, Key=document['storage_path'])
            try:
                payload = response['Body'].read(10 * 1024 * 1024 + 1)
            finally:
                response['Body'].close()
            if len(payload) > 10 * 1024 * 1024:
                raise ValueError('Stored document exceeds backup size budget')
            digest = hashlib.sha256(payload).hexdigest()
            backup = output / (str(document['id']) + '.object')
            backup.write_bytes(payload)
            restored_key = 'recovery-rehearsal/' + nonce + '/' + str(document['id'])
            try:
                client.put_object(Bucket=bucket, Key=restored_key, Body=backup.read_bytes())
                restored_object = client.get_object(Bucket=bucket, Key=restored_key)
                try:
                    recovered = restored_object['Body'].read(10 * 1024 * 1024 + 1)
                    if hashlib.sha256(recovered).hexdigest() != digest:
                        raise ValueError('Restored object differs from backup')
                finally:
                    restored_object['Body'].close()
            finally:
                client.delete_object(Bucket=bucket, Key=restored_key)
            objects.append({'id': str(document['id']), 'sha256': digest})
        except ClientError as error:
            if error.response['Error']['Code'] not in {'NoSuchKey', '404'}:
                raise
            missing.append(str(document['id']))

    probe_key = 'recovery-rehearsal/' + nonce + '/probe'
    probe = ('PredictIQ recovery probe ' + nonce).encode()
    try:
        client.put_object(Bucket=bucket, Key=probe_key, Body=probe, ContentType='text/plain')
        response = client.get_object(Bucket=bucket, Key=probe_key)
        try:
            if response['Body'].read(len(probe) + 1) != probe:
                raise ValueError('Live storage probe differs')
        finally:
            response['Body'].close()
    finally:
        # Only this invocation's generated synthetic key is eligible for cleanup.
        client.delete_object(Bucket=bucket, Key=probe_key)
    status, unexpected = classify_missing(missing, known_missing)
    report = {'status': status, 'database_restore': 'passed',
              'migration_head': head, 'tables': before, 'storage_roundtrip': 'passed',
              'documents_backed_up': len(objects), 'missing_document_count': len(missing),
              'unexpected_missing_count': unexpected,
              'restore_database': target['database'],
              'scope': 'Live Neon snapshot restored locally; live S3 referenced-object backup/isolated restore and synthetic round-trip'}
    (output / 'private-manifest.json').write_text(json.dumps({'missing_document_ids': missing,
                                                           'objects': objects}, indent=2))
    (output / 'result.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--known-missing-file', type=Path, help='Explicitly reviewed legacy test document IDs; never auto-accept new losses')
    parser.add_argument('--pg-bin', default='C:/Program Files/PostgreSQL/18/bin' if os.name == 'nt' else '/usr/bin')
    args = parser.parse_args()
    try:
        result = asyncio.run(rehearse(args.config, args.output, args.pg_bin, args.known_missing_file))
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['status'] in {'passed', 'passed_with_legacy_gaps'} else 1)
    except Exception as error:
        print(json.dumps({'status': 'failed', 'error_type': type(error).__name__}))
        raise SystemExit(1) from None
