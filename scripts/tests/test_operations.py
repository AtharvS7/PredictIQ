import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest.mock import patch

from scripts.check_operations import api_base, check
from scripts.rehearse_live_recovery import (
    classify_missing,
    evidence_directory,
    source_parameters,
)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.server.redirect:
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:1/private')
            self.end_headers()
            return
        live = self.path.endswith('/live')
        self.send_response(200 if live or self.server.ready else 503)
        self.end_headers()
        body = {'status': 'alive' if live else 'healthy', 'services': {
            'database': 'connected', 'ml_model': 'ready', 'firebase': 'initialized'}}
        self.wfile.write(json.dumps(body).encode())


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.ready = True
        self.server.redirect = False
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()

    def test_concurrent_healthy_probes(self):
        report = check(self.url, requests=12, concurrency=4)
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(report['checks']['ready']['requests'], 6)

    def test_live_cannot_mask_failed_readiness(self):
        self.server.ready = False
        report = check(self.url)
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(report['checks']['live']['failures'], 0)
        self.assertEqual(report['checks']['ready']['failures'], 1)

    def test_redirect_is_not_followed(self):
        self.server.redirect = True
        report = check(self.url)
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(report['samples'][0]['status'], 302)

    def test_latency_gate(self):
        with patch('scripts.check_operations.probe', side_effect=lambda base, route, timeout: {
                'route': route, 'healthy': True, 'latency_ms': 100}):
            self.assertEqual(check(self.url, max_p95_ms=50)['status'], 'failed')

    def test_guards_reject_credentials_and_excessive_load(self):
        for url in ['http://example.com', 'https://user:secret@example.com',
                    'https://example.com?token=secret', 'https://example.com/private']:
            with self.assertRaises(ValueError):
                api_base(url)
        with self.assertRaises(ValueError):
            check(self.url, requests=101)
        with self.assertRaises(ValueError):
            check(self.url, concurrency=5)

    def test_recovery_destination_and_source_guards(self):
        with self.assertRaises(ValueError):
            evidence_directory('docs/recovery-secret')
        for dsn in ['postgresql://user@localhost/database', 'postgresql://user@x.neon.tech.attacker.test/db']:
            with self.assertRaises(ValueError):
                source_parameters(dsn)
        self.assertEqual(source_parameters('postgresql://test@ep-example-pooler.neon.tech/db')['host'], 'ep-example.neon.tech')

    def test_known_legacy_gaps_never_hide_new_data_loss(self):
        self.assertEqual(classify_missing(['old'], ['old']), ('passed_with_legacy_gaps', 0))
        self.assertEqual(classify_missing(['old', 'new'], ['old']), ('blocked', 1))
        self.assertEqual(classify_missing([], ['old']), ('passed', 0))
