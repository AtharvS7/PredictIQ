"""
Unit tests for PredictIQ v2 Unified Release Gate (scripts/release_gate.py)
========================================================================
Verifies module importability, CLI argument parsing, step selection rules,
output parsing, forbidden file detection, and remote branch protection.
"""

from __future__ import annotations

from unittest.mock import patch

import scripts.release_gate as rg
from scripts.release_gate import (
    MAX_FILE_SIZE_BYTES,
    PROTECTED_BRANCH_BASELINES,
    ReleaseGate,
    StepResult,
    audit_security_and_hygiene,
    check_remote_branch_protection,
    create_parser,
    parse_pytest_summary,
)


class TestReleaseGateImportAndBaselines:
    """Verify core imports, data structures, and baseline contracts."""

    def test_import_and_exports(self):
        """Release gate module must export all essential components."""
        assert hasattr(rg, "ReleaseGate")
        assert hasattr(rg, "StepResult")
        assert hasattr(rg, "PROTECTED_BRANCH_BASELINES")
        assert hasattr(rg, "MAX_FILE_SIZE_BYTES")
        assert hasattr(rg, "create_parser")

    def test_protected_branch_baselines(self):
        """Baselines must strictly match the CP00 / dev2_snapshot canonical hashes."""
        assert PROTECTED_BRANCH_BASELINES["origin/main"] == "894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43"
        assert PROTECTED_BRANCH_BASELINES["origin/dev2"] == "d7a66b4095b8ae84f818900c2199c243f9d46b5f"

    def test_file_size_threshold(self):
        """Threshold must be exactly 50 megabytes."""
        assert MAX_FILE_SIZE_BYTES == 50 * 1024 * 1024


class TestReleaseGateCLIParser:
    """Verify CLI argument parsing and flags."""

    def test_default_cli_arguments(self):
        parser = create_parser()
        args = parser.parse_args([])
        assert args.skip_slow is False
        assert args.backend_only is False
        assert args.frontend_only is False
        assert args.fail_fast is False
        assert args.allow_uncommitted is False
        assert args.json is False

    def test_explicit_cli_flags(self):
        parser = create_parser()
        args = parser.parse_args([
            "--skip-slow",
            "--backend-only",
            "--fail-fast",
            "--allow-uncommitted",
            "--json",
        ])
        assert args.skip_slow is True
        assert args.backend_only is True
        assert args.frontend_only is False
        assert args.fail_fast is True
        assert args.allow_uncommitted is True
        assert args.json is True

    def test_dirty_flag_alias(self):
        parser = create_parser()
        args = parser.parse_args(["--dirty"])
        assert args.allow_uncommitted is True

    def test_frontend_only_flag(self):
        parser = create_parser()
        args = parser.parse_args(["--frontend-only"])
        assert args.frontend_only is True
        assert args.backend_only is False


class TestReleaseGateStepFiltering:
    """Verify that --skip-slow, --backend-only, and --frontend-only filter steps properly."""

    def test_default_gate_runs_all_steps(self):
        gate = ReleaseGate()
        for step_id in range(1, 10):
            should_run, _ = gate.should_run_step(step_id)
            assert should_run is True

    def test_skip_slow_filters_heavy_steps(self):
        gate = ReleaseGate(skip_slow=True)
        # Slow steps: 3 (backend tests), 6 (frontend tests), 7 (frontend build)
        for slow_step in (3, 6, 7):
            should_run, reason = gate.should_run_step(slow_step)
            assert should_run is False
            assert "skip-slow" in reason.lower()

        # Fast steps: 1, 2, 4, 5, 8, 9 must still run
        for fast_step in (1, 2, 4, 5, 8, 9):
            should_run, _ = gate.should_run_step(fast_step)
            assert should_run is True

    def test_backend_only_filters_frontend_steps(self):
        gate = ReleaseGate(backend_only=True)
        # Frontend steps: 5, 6, 7
        for fe_step in (5, 6, 7):
            should_run, reason = gate.should_run_step(fe_step)
            assert should_run is False
            assert "backend-only" in reason.lower()

        # Backend & audit steps: 1, 2, 3, 4, 8, 9 must run
        for be_step in (1, 2, 3, 4, 8, 9):
            should_run, _ = gate.should_run_step(be_step)
            assert should_run is True

    def test_frontend_only_filters_backend_steps(self):
        gate = ReleaseGate(frontend_only=True)
        # Backend steps: 1, 2, 3, 4
        for be_step in (1, 2, 3, 4):
            should_run, reason = gate.should_run_step(be_step)
            assert should_run is False
            assert "frontend-only" in reason.lower()

        # Frontend & audit steps: 5, 6, 7, 8, 9 must run
        for fe_step in (5, 6, 7, 8, 9):
            should_run, _ = gate.should_run_step(fe_step)
            assert should_run is True


class TestPytestSummaryParser:
    """Verify regex-based parsing of pytest outputs."""

    def test_clean_pass_and_skip(self):
        output = "655 passed, 6 skipped in 136.21s"
        summary, is_clean = parse_pytest_summary(output)
        assert is_clean is True
        assert "655 passed" in summary
        assert "6 skipped" in summary

    def test_failures_detected(self):
        output = "2 failed, 650 passed in 98.40s"
        summary, is_clean = parse_pytest_summary(output)
        assert is_clean is False
        assert "2 failed" in summary
        assert "650 passed" in summary

    def test_errors_detected(self):
        output = "1 error in 4.10s"
        summary, is_clean = parse_pytest_summary(output)
        assert is_clean is False
        assert "1 errors" in summary

    def test_empty_or_malformed_output(self):
        summary, is_clean = parse_pytest_summary("")
        assert is_clean is True
        assert summary == "Test run complete"


class TestSecurityAndHygieneAudit:
    """Verify detection of forbidden files, dirty git trees, and file size thresholds."""

    @patch("scripts.release_gate.run_command")
    def test_clean_tree_and_permitted_files(self, mock_run):
        # mock git status (clean) and git ls-files
        mock_run.side_effect = [
            (0, "", 0.1),                                   # git status --porcelain
            (0, "backend/app/main.py\nfrontend/src/App.tsx\nbackend/.env.example", 0.1),  # git ls-files
        ]
        result = audit_security_and_hygiene(allow_uncommitted=False)
        assert result.status == "PASS"
        assert result.exit_code == 0
        assert "Clean working tree" in result.summary

    @patch("scripts.release_gate.run_command")
    def test_uncommitted_files_blocked_by_default(self, mock_run):
        mock_run.side_effect = [
            (0, " M README.md\n?? new_script.py", 0.1),    # git status --porcelain
            (0, "backend/app/main.py", 0.1),               # git ls-files
        ]
        result = audit_security_and_hygiene(allow_uncommitted=False)
        assert result.status == "FAIL"
        assert result.exit_code == 1
        assert "uncommitted file(s)" in result.output

    @patch("scripts.release_gate.run_command")
    def test_uncommitted_files_allowed_with_flag(self, mock_run):
        mock_run.side_effect = [
            (0, " M README.md\n?? new_script.py", 0.1),    # git status --porcelain
            (0, "backend/app/main.py", 0.1),               # git ls-files
        ]
        result = audit_security_and_hygiene(allow_uncommitted=True)
        assert result.status == "PASS"
        assert result.exit_code == 0
        assert "warning" in result.summary.lower()

    @patch("scripts.release_gate.run_command")
    def test_forbidden_env_files_flagged(self, mock_run):
        mock_run.side_effect = [
            (0, "", 0.1),
            (0, "backend/.env\nfrontend/.env.production", 0.1),
        ]
        result = audit_security_and_hygiene(allow_uncommitted=False)
        assert result.status == "FAIL"
        assert "Tracked forbidden .env file: backend/.env" in result.output
        assert "Tracked forbidden .env file: frontend/.env.production" in result.output

    @patch("scripts.release_gate.run_command")
    def test_forbidden_pem_and_credentials_flagged(self, mock_run):
        mock_run.side_effect = [
            (0, "", 0.1),
            (0, "secrets/server.pem\nconfig/serviceAccountKey.json\npredictiq-firebase-adminsdk-live.json", 0.1),
        ]
        result = audit_security_and_hygiene(allow_uncommitted=False)
        assert result.status == "FAIL"
        assert "Tracked forbidden PEM" in result.output
        assert "Tracked forbidden credential file: config/serviceAccountKey.json" in result.output
        assert "Tracked forbidden credential file: predictiq-firebase-adminsdk-live.json" in result.output

    @patch("scripts.release_gate.run_command")
    def test_forbidden_cache_and_node_modules_flagged(self, mock_run):
        mock_run.side_effect = [
            (0, "", 0.1),
            (0, "node_modules/vite/index.js\nbackend/__pycache__/app.pyc\n.pytest_cache/v/cache", 0.1),
        ]
        result = audit_security_and_hygiene(allow_uncommitted=False)
        assert result.status == "FAIL"
        assert "Tracked forbidden node_modules" in result.output
        assert "Tracked forbidden cache file: backend/__pycache__/app.pyc" in result.output
        assert "Tracked forbidden cache file: .pytest_cache/v/cache" in result.output


class TestRemoteBranchProtection:
    """Verify remote branch integrity checks against known baselines."""

    @patch("scripts.release_gate.run_command")
    def test_valid_branch_and_matching_shas(self, mock_run):
        mock_run.side_effect = [
            (0, "dev3", 0.05),                                             # branch --show-current
            (0, "894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43", 0.05),        # rev-parse origin/main
            (0, "d7a66b4095b8ae84f818900c2199c243f9d46b5f", 0.05),        # rev-parse origin/dev2
            (1, "", 0.05),                                                 # ls-remote offline fallback
        ]
        result = check_remote_branch_protection()
        assert result.status == "PASS"
        assert result.exit_code == 0
        assert "origin/main and origin/dev2 strictly locked" in result.summary

    @patch("scripts.release_gate.run_command")
    def test_running_on_protected_branch_fails(self, mock_run):
        mock_run.side_effect = [
            (0, "main", 0.05),                                             # branch is main
            (0, "894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43", 0.05),
            (0, "d7a66b4095b8ae84f818900c2199c243f9d46b5f", 0.05),
            (1, "", 0.05),
        ]
        result = check_remote_branch_protection()
        assert result.status == "FAIL"
        assert result.exit_code == 1
        assert "must run on feature or release branch" in result.output

    @patch("scripts.release_gate.run_command")
    def test_tampered_remote_sha_fails(self, mock_run):
        mock_run.side_effect = [
            (0, "dev3", 0.05),
            (0, "1111111111111111111111111111111111111111", 0.05),        # tampered origin/main
            (0, "d7a66b4095b8ae84f818900c2199c243f9d46b5f", 0.05),
            (1, "", 0.05),
        ]
        result = check_remote_branch_protection()
        assert result.status == "FAIL"
        assert result.exit_code == 1
        assert "PROTECTION VIOLATION: origin/main SHA changed" in result.output


class TestFailFastBehavior:
    """Verify that fail-fast flag aborts on first failure."""

    @patch("scripts.release_gate.check_ruff_lint")
    @patch("scripts.release_gate.check_mypy_typecheck")
    def test_fail_fast_aborts_immediately(self, mock_mypy, mock_ruff):
        # Step 1 fails
        mock_ruff.return_value = StepResult(
            step_id=1,
            name="Code Formatting & Linting",
            target="backend",
            status="FAIL",
            duration=0.2,
            summary="Lint failure",
            exit_code=1,
        )

        gate = ReleaseGate(fail_fast=True, as_json=True)
        code = gate.run()

        assert code == 1
        assert len(gate.results) == 1
        assert gate.results[0].name == "Code Formatting & Linting"
        # Step 2 (mypy) was never called
        mock_mypy.assert_not_called()
