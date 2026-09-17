import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('production_preflight', Path(__file__).parents[1] / 'production_preflight.py')
preflight = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preflight)


class ProductionPreflightTests(unittest.TestCase):
    def valid(self):
        return {'APP_ENV': 'staging', 'DATABASE_URL': 'postgresql://user:test-secret@db.example.test/app',
                'ALLOWED_ORIGINS': 'https://app.example.test',
                'FIREBASE_CREDENTIALS_JSON': json.dumps({'type': 'service_account', 'project_id': 'fixture',
                                                        'client_email': 'fixture@example.test', 'private_key': 'test-secret'}),
                'STORAGE_BACKEND': 's3', 'S3_BUCKET_NAME': 'private-fixture',
                'ML_PIPELINE_MANIFEST': '/models/manifest.json', 'ML_PIPELINE_MANIFEST_SHA256': 'a' * 64}

    def test_complete_configuration_shape(self):
        self.assertEqual(preflight.check_environment(self.valid()), [])

    def test_rejects_emulator_and_local_storage(self):
        env = self.valid() | {'FIREBASE_AUTH_EMULATOR_HOST': 'localhost:9099', 'STORAGE_BACKEND': 'local'}
        self.assertEqual(len(preflight.check_environment(env)), 2)

    def test_error_does_not_echo_secrets(self):
        env = self.valid() | {'DATABASE_URL': 'test-secret', 'FIREBASE_CREDENTIALS_JSON': 'test-secret'}
        result = json.dumps(preflight.check_environment(env))
        self.assertNotIn('test-secret', result)

    def test_supabase_storage_path_is_valid_but_not_a_cors_origin(self):
        endpoint = 'https://project.storage.supabase.co/storage/v1/s3'
        env = self.valid() | {'S3_ENDPOINT_URL': endpoint}
        self.assertEqual(preflight.check_environment(env), [])
        self.assertFalse(preflight.https_origin(endpoint))

    def test_storage_endpoint_rejects_embedded_credentials_and_query(self):
        for endpoint in ['https://user:password@storage.example.test/s3',
                         'https://storage.example.test/s3?token=private',
                         'http://storage.example.test/s3']:
            env = self.valid() | {'S3_ENDPOINT_URL': endpoint}
            self.assertTrue(preflight.check_environment(env))

    def test_rejects_unsafe_origins(self):
        for origin in ['*', 'http://app.example.test', 'https://localhost', 'https://user:secret@app.example.test',
                       'https://app.example.test/path', 'https://app.example.test?secret=value']:
            with self.subTest(origin=origin):
                self.assertFalse(preflight.https_origin(origin))


if __name__ == '__main__':
    unittest.main()
