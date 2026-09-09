"""Opt-in smoke checks against the real built frontend image and Nginx config.

Set PREDICTIQ_TEST_FRONTEND_IMAGE to a locally built image with test-only Firebase
configuration. Creates and removes only its own container; no cloud calls.
"""
import os
import re
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@unittest.skipUnless(os.getenv("PREDICTIQ_TEST_FRONTEND_IMAGE"), "Requires a local test frontend image")
class FrontendContainerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="predictiq-nginx-test-")
        cls.addClassCleanup(cls.temp.cleanup)
        upstream = Path(cls.temp.name) / "upstream.conf"
        upstream.write_text("server { listen 8000; client_max_body_size 20m; location / { return 204; } }", encoding="utf-8")
        cls.container = subprocess.check_output([
            "docker", "run", "--detach", "--publish", "127.0.0.1::80",
            "--add-host", "backend:127.0.0.1",
            "--mount", f"type=bind,source={upstream},target=/etc/nginx/conf.d/test-upstream.conf,readonly",
            os.environ["PREDICTIQ_TEST_FRONTEND_IMAGE"],
        ], text=True).strip()
        cls.addClassCleanup(lambda: subprocess.run(["docker", "rm", "--force", cls.container], check=True, capture_output=True))
        address = subprocess.check_output(["docker", "port", cls.container, "80/tcp"], text=True).strip()
        cls.url = f"http://{address}"
        for _ in range(50):
            try:
                with urlopen(cls.url, timeout=2) as response:
                    if response.status == 200:
                        break
            except (URLError, ConnectionError):
                time.sleep(0.2)
        else:
            raise RuntimeError("Local frontend container did not become ready")

    def request(self, path, data=None):
        try:
            response = urlopen(Request(self.url + path, data=data), timeout=20)
        except HTTPError as error:
            response = error
        with response:
            return response.status, response.headers, response.read()

    def assert_security_headers(self, headers):
        self.assertEqual(headers["X-Frame-Options"], "DENY")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Referrer-Policy"], "no-referrer")

    def test_shell_assets_and_errors_keep_security_headers(self):
        for path in ("/", "/index.html", "/share/test-token", "/share/test-token.svg"):
            with self.subTest(path=path):
                status, headers, body = self.request(path)
                self.assertEqual(status, 200)
                self.assert_security_headers(headers)
                self.assertIn("no-store", headers["Cache-Control"])
        asset = re.search(rb'src="(/assets/[^" ]+\.js)"', body).group(1).decode()
        status, headers, _ = self.request(asset)
        self.assertEqual(status, 200)
        self.assert_security_headers(headers)
        self.assertIn("immutable", headers["Cache-Control"])
        status, headers, _ = self.request("/assets/nonexistent.js")
        self.assertEqual(status, 404)
        self.assert_security_headers(headers)

    def test_upload_budget_reaches_upstream_and_oversized_body_is_rejected(self):
        status, _, _ = self.request("/api/v1/documents/upload-file", b"x" * (10 * 1024 * 1024))
        self.assertEqual(status, 204)
        status, headers, _ = self.request("/api/v1/documents/upload-file", b"x" * (11 * 1024 * 1024 + 1))
        self.assertEqual(status, 413)
        self.assert_security_headers(headers)

    def test_spa_redirect_does_not_log_share_tokens_or_queries(self):
        self.request("/share/private-test-share-token?password=private-test-query")
        logs = subprocess.check_output(["docker", "logs", self.container], stderr=subprocess.STDOUT)
        self.assertNotIn(b"private-test-share-token", logs)
        self.assertNotIn(b"private-test-query", logs)


if __name__ == "__main__":
    unittest.main()
