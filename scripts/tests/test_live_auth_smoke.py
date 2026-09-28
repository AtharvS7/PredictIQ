import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.live_auth_smoke import run


class LiveAuthSmokeTests(unittest.TestCase):
    def exercise(self, unavailable_detail='Prediction service is unavailable', cross_status=404, manual_release=False):
        root = Path(__file__).resolve().parents[2] / '.tools'
        root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as directory:
            folder = Path(directory)
            users = [{'uid': f'predictiq-ops-{i}', 'email': f'test{i}@example.invalid',
                      'password': 'private-password'} for i in range(2)]
            identity = folder / 'identities.json'
            identity.write_text(json.dumps({'project_id': 'demo', 'users': users}))
            def response(status=200, **data):
                return Mock(status_code=status, json=lambda: data,
                            headers={'X-Content-Type-Options': 'nosniff'})
            replies = [response(user_id=u['uid']) for u in users] + [
                response(401), response(403), response(), response(), response(id='fixture'),
                response(id='fixture'), response(cross_status), response(word_count=50),
                response(503, detail=unavailable_detail),
                response(200 if manual_release else 503, release_mode='manual_budget' if manual_release else 'prediction',
                         capabilities={'manual_budget': manual_release, 'automatic_prediction': False},
                         services={'database': 'connected', 'ml_model': 'not_loaded', 'firebase': 'initialized'})]
            with patch('dotenv.dotenv_values', return_value={
                'VITE_FIREBASE_PROJECT_ID': 'demo', 'VITE_FIREBASE_API_KEY': 'private-key'}), \
                 patch('requests.post', side_effect=[response(localId=u['uid'], idToken='private-token')
                                                     for u in users]), \
                 patch('requests.request', side_effect=replies) as request:
                report = run('https://example.invalid', identity, folder / 'env', folder)
            for call in request.call_args_list:
                self.assertFalse(call.kwargs['allow_redirects'])
                self.assertEqual(call.kwargs['timeout'], 45)
            evidence = (folder / 'result.json').read_text()
            for secret in ['private-password', 'private-key', 'private-token']:
                self.assertNotIn(secret, evidence)
            return report

    def test_model_unavailable_is_partial_not_pass(self):
        self.assertEqual(self.exercise()['status'], 'partial_model_unavailable')

    def test_manual_readiness_does_not_pass_ml_acceptance(self):
        self.assertEqual(self.exercise(manual_release=True)['status'], 'partial_model_unavailable')

    def test_generic_outage_is_not_mislabeled_as_model_failure(self):
        self.assertEqual(self.exercise(unavailable_detail='Database unavailable')['status'], 'failed')

    def test_cross_user_access_fails_acceptance(self):
        self.assertEqual(self.exercise(cross_status=200)['status'], 'failed')

    def test_remote_http_is_rejected_before_credentials_are_read(self):
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            run('http://example.invalid', 'missing', 'missing', '.tools')

    def test_evidence_outside_private_directory_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'inside .tools'):
            run('https://example.invalid', 'missing', 'missing', '.')
