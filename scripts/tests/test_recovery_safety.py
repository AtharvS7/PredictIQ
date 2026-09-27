import unittest

from scripts.rehearse_recovery import local_connection


class RecoverySafetyTests(unittest.TestCase):
    def test_only_explicit_isolated_endpoint_is_accepted(self):
        params = local_connection('postgresql://test:local%40password@127.0.0.1:15439/predictiq_integration')
        self.assertEqual(params['password'], 'local@password')
        for dsn in ['postgresql://test@production.example:15439/predictiq_integration',
                    'postgresql://test@127.0.0.1:5432/predictiq_integration',
                    'postgresql://test@127.0.0.1:15439/production',
                    'postgresql://test@127.0.0.1:15439/predictiq_integration?host=production.example', '']:
            with self.assertRaises(ValueError):
                local_connection(dsn)
