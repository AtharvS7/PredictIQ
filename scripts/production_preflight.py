"""Offline production configuration checks; no network, model loading or secret output.

Run in the target environment: python scripts/production_preflight.py
Checks process environment only. Does not read local development .env files.
"""
import json
import os
import re
from urllib.parse import urlsplit


def https_origin(value):
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == 'https' and bool(parsed.hostname)
                and parsed.hostname not in {'localhost', '127.0.0.1', '::1'}
                and not parsed.username and not parsed.password
                and parsed.path in {'', '/'} and not parsed.query and not parsed.fragment
                and parsed.port in {None, 443})
    except ValueError:
        return False


def check_environment(env):
    """Return field-only failures, never include supplied values in errors."""
    failures = []
    if env.get('APP_ENV') not in {'production', 'staging'}:
        failures.append('APP_ENV: must be production or staging')
    if env.get('FIREBASE_AUTH_EMULATOR_HOST'):
        failures.append('FIREBASE_AUTH_EMULATOR_HOST: must be absent')
    try:
        database = urlsplit(env.get('DATABASE_URL', ''))
        valid_database = database.scheme in {'postgres', 'postgresql'} and database.hostname and database.path not in {'', '/'}
    except ValueError:
        valid_database = False
    if not valid_database:
        failures.append('DATABASE_URL: valid PostgreSQL connection string required')
    origins = env.get('ALLOWED_ORIGINS', '').split(',')
    if not origins or not all(https_origin(origin.strip()) for origin in origins):
        failures.append('ALLOWED_ORIGINS: explicit HTTPS frontend origins required')
    try:
        firebase = json.loads(env.get('FIREBASE_CREDENTIALS_JSON', ''))
        valid_firebase = (isinstance(firebase, dict) and firebase.get('type') == 'service_account'
                          and all(firebase.get(key) for key in ['project_id', 'client_email', 'private_key']))
    except (ValueError, TypeError):
        valid_firebase = False
    if not valid_firebase:
        failures.append('FIREBASE_CREDENTIALS_JSON: service-account configuration required for this hosting path')
    if env.get('STORAGE_BACKEND') != 's3' or not env.get('S3_BUCKET_NAME', '').strip():
        failures.append('STORAGE_BACKEND/S3_BUCKET_NAME: durable S3-compatible storage required for this hosting path')
    if bool(env.get('S3_ACCESS_KEY_ID')) != bool(env.get('S3_SECRET_ACCESS_KEY')):
        failures.append('S3 credentials: provide both fields or a provider-managed identity')
    if env.get('S3_ENDPOINT_URL') and not https_origin(env['S3_ENDPOINT_URL']):
        failures.append('S3_ENDPOINT_URL: HTTPS service origin required')
    if not env.get('ML_PIPELINE_MANIFEST') or not re.fullmatch(r'[a-fA-F0-9]{64}', env.get('ML_PIPELINE_MANIFEST_SHA256', '')):
        failures.append('ML_PIPELINE_MANIFEST/SHA256: reviewed bundle path and hash required')
    return failures


if __name__ == '__main__':
    failures = check_environment(os.environ)
    print(json.dumps({'configuration_passed': not failures, 'failures': failures,
                      'scope': 'Offline syntax only; credentials, artifacts, access, backups and readiness remain live gates.'}, indent=2))
    raise SystemExit(1 if failures else 0)
