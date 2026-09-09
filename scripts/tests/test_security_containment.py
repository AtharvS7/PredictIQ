"""Offline security regression checks: python -m unittest discover -s scripts/tests."""
import asyncio
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.driver = types.ModuleType("asyncpg")
        self.driver.connect = AsyncMock()
        spec = importlib.util.spec_from_file_location(
            "migration_under_test", ROOT / "backend/scripts/run_migration.py"
        )
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"asyncpg": self.driver}):
            spec.loader.exec_module(self.module)

    def test_missing_configuration_never_connects(self):
        for value in ("", "   "):
            with self.subTest(value=value), patch.dict(os.environ, {"DATABASE_URL": value}):
                self.assertEqual(asyncio.run(self.module.main()), 1)
                self.driver.connect.assert_not_called()

    def test_connection_failure_does_not_log_credentials(self):
        import contextlib
        import io
        output = io.StringIO()
        self.driver.connect.side_effect = RuntimeError("private-token")
        with patch.dict(os.environ, {"DATABASE_URL": "private-token"}):
            with contextlib.redirect_stderr(output):
                self.assertEqual(asyncio.run(self.module.main()), 1)
        self.assertNotIn("private-token", output.getvalue())


class WorkflowTests(unittest.TestCase):
    def test_scanner_exit_codes_are_not_suppressed(self):
        ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8-sig")
        weekly = (ROOT / ".github/workflows/security-weekly.yml").read_text(encoding="utf-8-sig")
        gate = ci.split('name: "Bandit SAST')[1].split('name: "Check .env')[0]
        self.assertIn("-lll", gate)
        for block in (gate, weekly):
            self.assertNotIn("|| true", block)
            self.assertNotIn("except: pass", block)
            self.assertIn("if: always()", block)
        self.assertIn("npm audit --audit-level=high --json", weekly)

    @unittest.skipUnless(importlib.util.find_spec("bandit"), "Bandit not installed")
    def test_real_bandit_fails_for_seeded_high_finding(self):
        with tempfile.TemporaryDirectory() as directory:
            sample = Path(directory) / "unsafe.py"
            sample.write_text("import subprocess\nsubprocess.call('echo ' + input(), shell=True)\n")
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", directory, "-lll", "-f", "json"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertIn('"issue_severity": "HIGH"', result.stdout)


if __name__ == "__main__":
    unittest.main()
