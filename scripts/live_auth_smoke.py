"""Explicit live-provider smoke using two pre-provisioned synthetic test identities.

Keeps one reusable synthetic document for recovery/estimation acceptance. Tokens
never leave memory or appear in output. Does not provision accounts, send email,
delete records, train a model, or treat unavailable estimation as a passed release.
"""
import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_operations import api_base


def run(base_url, identities_file, frontend_env, evidence_path):
    import requests
    from dotenv import dotenv_values

    base = api_base(base_url)
    if not base.startswith('https://'):
        raise ValueError('Live provider smoke requires HTTPS')
    output = Path(evidence_path).resolve()
    private_root = (Path(__file__).resolve().parents[1] / '.tools').resolve()
    if not output.is_relative_to(private_root):
        raise ValueError('Evidence must remain inside .tools')
    output.mkdir(parents=True, exist_ok=True)
    identities = json.loads(Path(identities_file).read_text())
    frontend = dotenv_values(frontend_env)
    if identities['project_id'] != frontend['VITE_FIREBASE_PROJECT_ID'] or len(identities['users']) != 2:
        raise ValueError('Expected two test identities for the configured Firebase project')
    checks = {}
    estimation_status = None

    def require(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise RuntimeError('Live check failed: ' + name)

    def call(method, path, headers=None, **kwargs):
        return requests.request(method, base + path, headers=headers, timeout=45,
                                allow_redirects=False, **kwargs)

    try:
        tokens = []
        for index, user in enumerate(identities['users']):
            if not user['uid'].startswith('predictiq-ops-') or not user['email'].endswith('@example.invalid'):
                raise ValueError('Only explicit synthetic operational identities are permitted')
            login = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword',
                                  params={'key': frontend['VITE_FIREBASE_API_KEY']},
                                  json={'email': user['email'], 'password': user['password'], 'returnSecureToken': True},
                                  timeout=30, allow_redirects=False)
            require(f'firebase_signin_{index}', login.status_code == 200)
            data = login.json()
            require(f'firebase_identity_{index}', data.get('localId') == user['uid'])
            headers = {'Authorization': 'Bearer ' + data['idToken']}
            tokens.append(headers)
            synced = call('POST', '/auth/firebase', headers, json={})
            require(f'backend_verified_identity_{index}', synced.status_code == 200 and synced.json().get('user_id') == user['uid'])

        owner, other = tokens
        require('anonymous_denied', call('GET', '/profile').status_code == 401)
        require('admin_denied', call('GET', '/admin/users', owner).status_code == 403)
        profile = call('POST', '/profile', owner, json={'full_name': 'PredictIQ operational test'})
        require('profile_persisted', profile.status_code == 200)
        require('profile_read', call('GET', '/profile', owner).status_code == 200)
        marker = output / 'document.json'
        if marker.exists():
            document = json.loads(marker.read_text())
            require('document_fixture_owner', document['owner_uid'] == identities['users'][0]['uid'])
            document_id = document['id']
        else:
            payload = (b'Project: Operational Recovery Test. Build a web application with React and Python. '
                       b'A team of 3 developers will work for 4 months using Agile. Users register accounts, '
                       b'manage project records, search tasks, export reports and view dashboards. '
                       b'Integrate email and payment APIs. This is a synthetic operational fixture, not ML training data.')
            uploaded = call('POST', '/documents/upload-file', owner,
                            files={'file': ('operational-recovery-test.txt', payload, 'text/plain')})
            require('upload_persisted', uploaded.status_code == 200)
            document_id = uploaded.json()['id']
            marker.write_text(json.dumps({'id': document_id, 'owner_uid': identities['users'][0]['uid']}))
        retrieved = call('GET', '/documents/' + document_id, owner)
        require('document_reloaded', retrieved.status_code == 200 and retrieved.json()['id'] == document_id)
        require('cross_user_document_denied', call('GET', '/documents/' + document_id, other).status_code == 404)
        extracted = call('POST', '/documents/' + document_id + '/extract', owner)
        require('real_storage_parser_nlp', extracted.status_code == 200 and extracted.json().get('word_count', 0) >= 20)
        require('security_headers', extracted.headers.get('X-Content-Type-Options') == 'nosniff')
        estimate = call('POST', '/estimates/analyze', owner, json={
            'document_id': document_id, 'overrides': {'project_name': 'Operational Recovery Test'}})
        estimation_status = estimate.status_code
        if estimate.status_code == 503:
            require('prediction_unavailable_response',
                    estimate.json().get('detail') == 'Prediction service is unavailable')
            readiness = call('GET', '/ready')
            readiness_body = readiness.json()
            manual_release = (readiness.status_code == 200 and readiness_body.get('release_mode') == 'manual_budget'
                              and readiness_body.get('capabilities') == {'manual_budget': True, 'automatic_prediction': False})
            require('model_unavailable_confirmed', (readiness.status_code == 503 or manual_release)
                    and readiness_body.get('services') == {
                        'database': 'connected', 'ml_model': 'not_loaded', 'firebase': 'initialized'})
            status = 'partial_model_unavailable'
        else:
            require('estimation_response', estimate.status_code == 200)
            # A response alone does not prove independent ML acceptance.
            status = 'api_flow_passed_requires_model_acceptance'
        report = {'status': status, 'checks': checks, 'estimation_http_status': estimate.status_code,
                  'scope': 'Live Firebase password sign-in, hosted API, Neon persistence, S3 and extraction; not browser E2E or model accuracy'}
    except (requests.RequestException, OSError, ValueError, KeyError, RuntimeError) as error:
        report = {'status': 'failed', 'checks': checks, 'error_type': type(error).__name__,
                  'estimation_http_status': estimation_status}
    (output / 'result.json').write_text(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--identities', type=Path, required=True)
    parser.add_argument('--frontend-env', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.base_url, args.identities, args.frontend_env, args.evidence)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'api_flow_passed_requires_model_acceptance' else 1)
