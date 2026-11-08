#!/usr/bin/env python3
"""
PredictIQ v2 — Unified Release Gate (Checkpoint R11)
===================================================
Single source of truth release validation gate ensuring strict parity
between local pre-commit checks and CI workflows.

Checks executed in order:
  1. Code formatting & linting:  ruff check backend/app backend/ml --select E,W,F,I --ignore E501,E402
  2. Static type safety:         mypy app/ (in backend/ with backend/mypy.ini)
  3. Backend test suite:         pytest backend/tests -q
  4. Scripts test suite:         pytest scripts/tests -q
  5. Frontend typecheck:         npm --prefix frontend run typecheck
  6. Frontend unit/component:    npx --prefix frontend vitest run --root frontend --pool=forks
  7. Frontend production build:  npm --prefix frontend run build
  8. Security & hygiene audit:   git status, uncommitted changes, forbidden files (.env, *.pem,
                                 serviceAccount*.json, node_modules, cache, files > 50MB)
  9. Remote branch protection:   verifies origin/main and origin/dev2 hashes have not been modified

CLI Options:
  --skip-slow          Skip long-running test and build steps (backend tests, frontend tests, build)
  --backend-only       Execute only backend & repository audit steps
  --frontend-only      Execute only frontend & repository audit steps
  --fail-fast          Abort immediately upon encountering the first failed step
  --allow-uncommitted  Allow uncommitted changes during security/hygiene audit (emits WARN)
  --dirty              Alias for --allow-uncommitted
  --json               Output structured JSON results summary
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

# ── Project Directory Configuration ──────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Canonical protected remote branch baseline commit SHAs (from CP00 / dev2_snapshot.md)
PROTECTED_BRANCH_BASELINES = {
    "origin/main": "894c3dabfc5aa71cdaf4c6071b94f1c5f7e56b43",
    "origin/dev2": "d7a66b4095b8ae84f818900c2199c243f9d46b5f",
}

MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB threshold


# ── ANSI Color Formatting ───────────────────────────────────────────────────

class Colors:
    """ANSI color codes with automatic terminal detection."""
    ENABLED = sys.stdout.isatty() or os.getenv("FORCE_COLOR") == "1"

    RESET = "\033[0m" if ENABLED else ""
    BOLD = "\033[1m" if ENABLED else ""
    DIM = "\033[2m" if ENABLED else ""
    RED = "\033[91m" if ENABLED else ""
    GREEN = "\033[92m" if ENABLED else ""
    YELLOW = "\033[93m" if ENABLED else ""
    BLUE = "\033[94m" if ENABLED else ""
    CYAN = "\033[96m" if ENABLED else ""
    WHITE = "\033[97m" if ENABLED else ""


# ── Data Models ─────────────────────────────────────────────────────────────

@dataclass
class StepResult:
    step_id: int
    name: str
    target: str
    status: str          # "PASS", "FAIL", "SKIPPED", "WARN"
    duration: float      # in seconds
    summary: str
    command: str = ""
    output: str = ""
    exit_code: int = 0


# ── Subprocess Runner ───────────────────────────────────────────────────────

def resolve_python_executable() -> str:
    """Resolve the active Python interpreter, preferring virtual environments."""
    venv_exe = PROJECT_ROOT / ".venv" / ("Scripts" if sys.platform == "win32" else "bin") / ("python.exe" if sys.platform == "win32" else "python")
    if venv_exe.exists():
        return str(venv_exe)
    return sys.executable


def resolve_binary(bin_name: str) -> str:
    """Resolve binary across platforms (handling .cmd on Windows)."""
    which = shutil.which(bin_name)
    if which:
        return which
    return bin_name


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
) -> Tuple[int, str, float]:
    """Execute command, measuring duration and capturing combined output."""
    start_time = time.perf_counter()
    run_env = os.environ.copy()
    if env:
        run_env.update(env)

    # Resolve binary name on Windows
    resolved_cmd = list(cmd)
    if sys.platform == "win32" and resolved_cmd:
        resolved_cmd[0] = resolve_binary(resolved_cmd[0])

    try:
        proc = subprocess.run(
            resolved_cmd,
            cwd=str(cwd) if cwd else str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            env=run_env,
            encoding="utf-8",
            errors="replace",
        )
        duration = time.perf_counter() - start_time
        combined = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, combined, duration
    except FileNotFoundError as err:
        duration = time.perf_counter() - start_time
        return 127, f"Binary not found: {err}", duration
    except Exception as ex:
        duration = time.perf_counter() - start_time
        return 1, f"Execution failed: {ex}", duration


# ── Release Gate Check Definitions ──────────────────────────────────────────

def check_ruff_lint(python_bin: str) -> StepResult:
    """Step 1: Code formatting & linting with Ruff."""
    cmd = [
        python_bin, "-m", "ruff", "check",
        "backend/app", "backend/ml",
        "--select", "E,W,F,I",
        "--ignore", "E501,E402",
    ]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)
    if code == 0:
        summary = "0 lint/style errors (backend/app, backend/ml clean)"
        status = "PASS"
    else:
        err_lines = [line.strip() for line in output.splitlines() if line.strip() and not line.startswith("Found")]
        summary = f"Ruff lint errors found ({len(err_lines)} issues)"
        status = "FAIL"

    return StepResult(
        step_id=1,
        name="Code Formatting & Linting",
        target="backend/app, backend/ml",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def check_mypy_typecheck(python_bin: str) -> StepResult:
    """Step 2: Static type safety with mypy."""
    cmd = [python_bin, "-m", "mypy", "app/"]
    code, output, duration = run_command(cmd, cwd=BACKEND_DIR)
    if code == 0:
        match = re.search(r"no issues found in (\d+) source files", output)
        files_count = match.group(1) if match else "48"
        summary = f"0 type errors ({files_count} source files clean)"
        status = "PASS"
    else:
        err_match = re.search(r"Found (\d+) error", output)
        count = err_match.group(1) if err_match else "multiple"
        summary = f"Mypy found {count} type errors"
        status = "FAIL"

    return StepResult(
        step_id=2,
        name="Static Type Safety",
        target="backend/app (48 files)",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def parse_pytest_summary(output: str) -> Tuple[str, bool]:
    """Parse pytest output line to extract counts."""
    pass_m = re.search(r"(\d+)\s+passed", output)
    skip_m = re.search(r"(\d+)\s+skipped", output)
    fail_m = re.search(r"(\d+)\s+failed", output)
    err_m = re.search(r"(\d+)\s+error", output)

    passed = int(pass_m.group(1)) if pass_m else 0
    skipped = int(skip_m.group(1)) if skip_m else 0
    failed = int(fail_m.group(1)) if fail_m else 0
    errors = int(err_m.group(1)) if err_m else 0

    parts = []
    if passed:
        parts.append(f"{passed} passed")
    if skipped:
        parts.append(f"{skipped} skipped")
    if failed:
        parts.append(f"{failed} failed")
    if errors:
        parts.append(f"{errors} errors")

    summary_str = ", ".join(parts) if parts else "Test run complete"
    has_failures = (failed > 0 or errors > 0)
    return summary_str, not has_failures


def check_backend_tests(python_bin: str) -> StepResult:
    """Step 3: Backend test suite."""
    cmd = [python_bin, "-m", "pytest", "backend/tests", "-q"]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)
    summary_counts, is_clean = parse_pytest_summary(output)

    status = "PASS" if (code == 0 and is_clean) else "FAIL"
    summary = f"Backend suite: {summary_counts}"

    return StepResult(
        step_id=3,
        name="Backend Test Suite",
        target="backend/tests",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def check_scripts_tests(python_bin: str) -> StepResult:
    """Step 4: Scripts test suite."""
    cmd = [python_bin, "-m", "pytest", "scripts/tests", "-q"]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)
    summary_counts, is_clean = parse_pytest_summary(output)

    status = "PASS" if (code == 0 and is_clean) else "FAIL"
    summary = f"Scripts suite: {summary_counts}"

    return StepResult(
        step_id=4,
        name="Scripts Test Suite",
        target="scripts/tests",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def check_frontend_typecheck() -> StepResult:
    """Step 5: Frontend TypeScript strict typecheck."""
    npm_bin = resolve_binary("npm")
    cmd = [npm_bin, "--prefix", "frontend", "run", "typecheck"]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)

    if code == 0:
        summary = "0 type errors (tsc and tsconfig.test clean)"
        status = "PASS"
    else:
        summary = "TypeScript typecheck errors detected"
        status = "FAIL"

    return StepResult(
        step_id=5,
        name="Frontend Typecheck",
        target="frontend/ (strict tsc)",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def check_frontend_tests() -> StepResult:
    """Step 6: Frontend Vitest unit & component test suite."""
    npx_bin = resolve_binary("npx")
    cmd = [npx_bin, "--prefix", "frontend", "vitest", "run", "--root", "frontend", "--pool=forks"]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)

    files_match = re.search(r"Test Files\s+(\d+)\s+passed", output)
    tests_match = re.search(r"Tests\s+(\d+)\s+passed", output)
    files_passed = files_match.group(1) if files_match else None
    tests_passed = tests_match.group(1) if tests_match else None

    if code == 0 and "FAIL" not in output:
        if files_passed and tests_passed:
            summary = f"{files_passed} test files, {tests_passed} unit tests passed"
        else:
            summary = "All unit & component tests passed"
        status = "PASS"
    else:
        summary = "Vitest unit tests failed"
        status = "FAIL"

    return StepResult(
        step_id=6,
        name="Frontend Unit/Component Tests",
        target="frontend/src (vitest)",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def check_frontend_build() -> StepResult:
    """Step 7: Frontend production build."""
    npm_bin = resolve_binary("npm")
    cmd = [npm_bin, "--prefix", "frontend", "run", "build"]
    code, output, duration = run_command(cmd, cwd=PROJECT_ROOT)

    if code == 0 and (FRONTEND_DIR / "dist" / "index.html").exists():
        summary = "Production bundle built successfully (dist/ verified)"
        status = "PASS"
    else:
        summary = "Frontend production build failed"
        status = "FAIL"

    return StepResult(
        step_id=7,
        name="Frontend Production Build",
        target="frontend/dist",
        status=status,
        duration=duration,
        summary=summary,
        command=" ".join(cmd),
        output=output,
        exit_code=code,
    )


def audit_security_and_hygiene(allow_uncommitted: bool = False) -> StepResult:
    """Step 8: Security & hygiene audit (git status, forbidden files, file size limits)."""
    start_time = time.perf_counter()
    violations: List[str] = []
    warnings: List[str] = []

    # 1. Check git status for uncommitted changes
    git_bin = resolve_binary("git")
    code, git_status_out, _ = run_command([git_bin, "status", "--porcelain"], cwd=PROJECT_ROOT)
    uncommitted = [line.strip() for line in git_status_out.splitlines() if line.strip()]

    if uncommitted:
        if allow_uncommitted:
            warnings.append(f"{len(uncommitted)} uncommitted file(s) present (permitted by --allow-uncommitted)")
        else:
            violations.append(f"Working tree has {len(uncommitted)} uncommitted file(s); clean tree required for release")

    # 2. Check tracked files via git ls-files
    code, ls_out, _ = run_command([git_bin, "ls-files"], cwd=PROJECT_ROOT)
    tracked_files = [line.strip() for line in ls_out.splitlines() if line.strip()]

    # 3. Forbidden file checks
    for rel_path in tracked_files:
        norm_path = rel_path.replace("\\", "/").lower()
        base_name = os.path.basename(norm_path)

        # Check for forbidden .env files
        if (base_name.startswith(".env") or norm_path.endswith(".env")) and not base_name.endswith(".example"):
            violations.append(f"Tracked forbidden .env file: {rel_path}")

        # Check for .pem certificates / keys
        if norm_path.endswith(".pem"):
            violations.append(f"Tracked forbidden PEM private key/cert: {rel_path}")

        # Check for service account credentials
        if ("serviceaccount" in norm_path or "firebase-adminsdk" in norm_path) and norm_path.endswith(".json"):
            violations.append(f"Tracked forbidden credential file: {rel_path}")

        # Check for node_modules in repository
        if "node_modules/" in norm_path or norm_path.startswith("node_modules"):
            violations.append(f"Tracked forbidden node_modules file: {rel_path}")

        # Check for python/pytest/mypy caches
        if any(cache_tag in norm_path for cache_tag in ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]):
            violations.append(f"Tracked forbidden cache file: {rel_path}")

        # 4. Check file size limits (> 50MB)
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists() and not full_path.is_dir():
            size = full_path.stat().st_size
            if size > MAX_FILE_SIZE_BYTES:
                size_mb = size / (1024 * 1024)
                violations.append(f"Tracked file exceeds 50MB limit ({size_mb:.2f}MB): {rel_path}")

    duration = time.perf_counter() - start_time

    if violations:
        status = "FAIL"
        summary = f"Security audit failed: {len(violations)} violation(s)"
        output = "\n".join(violations)
        exit_code = 1
    elif warnings:
        status = "PASS"
        summary = f"Audit passed with {len(warnings)} warning(s) (no secrets, no forbidden files)"
        output = "\n".join(warnings)
        exit_code = 0
    else:
        status = "PASS"
        summary = "Clean working tree, zero secrets, zero forbidden files, all < 50MB"
        output = "Audit passed: 0 forbidden files, 0 files > 50MB, git status clean."
        exit_code = 0

    return StepResult(
        step_id=8,
        name="Security & Hygiene Audit",
        target="repository hygiene & secrets",
        status=status,
        duration=duration,
        summary=summary,
        command="git status + forbidden file scan",
        output=output,
        exit_code=exit_code,
    )


def check_remote_branch_protection() -> StepResult:
    """Step 9: Remote branch protection check (verifies origin/main & origin/dev2 unaltered)."""
    start_time = time.perf_counter()
    git_bin = resolve_binary("git")
    failures: List[str] = []
    attestations: List[str] = []

    # 1. Verify current branch is not main or dev2
    code, branch_out, _ = run_command([git_bin, "branch", "--show-current"], cwd=PROJECT_ROOT)
    curr_branch = branch_out.strip()
    if curr_branch in ("main", "dev2"):
        failures.append(f"Release gate must run on feature or release branch, not protected branch: '{curr_branch}'")
    else:
        attestations.append(f"Active branch is '{curr_branch}' (non-protected)")

    # 2. Check local tracking references for origin/main and origin/dev2
    for remote_ref, baseline_sha in PROTECTED_BRANCH_BASELINES.items():
        code, sha_out, _ = run_command([git_bin, "rev-parse", remote_ref], cwd=PROJECT_ROOT)
        actual_sha = sha_out.strip()
        if code != 0:
            # Fallback: attempt fetch if tracking ref is absent (e.g., CI shallow clone)
            branch_short = remote_ref.replace("origin/", "")
            run_command([git_bin, "fetch", "origin", f"{branch_short}:{remote_ref}"], cwd=PROJECT_ROOT)
            code, sha_out, _ = run_command([git_bin, "rev-parse", remote_ref], cwd=PROJECT_ROOT)
            actual_sha = sha_out.strip()

        if code != 0:
            failures.append(f"Unable to resolve remote reference '{remote_ref}': {actual_sha}")
        elif actual_sha != baseline_sha:
            failures.append(
                f"PROTECTION VIOLATION: {remote_ref} SHA changed! Expected {baseline_sha}, found {actual_sha}"
            )
        else:
            attestations.append(f"{remote_ref} matches locked baseline ({actual_sha[:10]}...)")

    # 3. If git remote is reachable, verify against upstream remote heads
    code, ls_remote_out, _ = run_command(
        [git_bin, "ls-remote", "--heads", "origin", "main", "dev2"], cwd=PROJECT_ROOT
    )
    if code == 0 and ls_remote_out.strip():
        for line in ls_remote_out.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                remote_sha, ref_name = parts[0], parts[1]
                short_ref = "origin/" + ref_name.replace("refs/heads/", "")
                expected = PROTECTED_BRANCH_BASELINES.get(short_ref)
                if expected and remote_sha != expected:
                    failures.append(
                        f"REMOTE VIOLATION: upstream {ref_name} has SHA {remote_sha}, expected baseline {expected}"
                    )
                elif expected:
                    attestations.append(f"Upstream {ref_name} verified against remote ({remote_sha[:10]}...)")

    duration = time.perf_counter() - start_time

    if failures:
        status = "FAIL"
        summary = f"Branch protection check failed: {len(failures)} issue(s)"
        output = "\n".join(failures)
        exit_code = 1
    else:
        status = "PASS"
        summary = "origin/main and origin/dev2 strictly locked to baseline SHAs"
        output = "\n".join(attestations)
        exit_code = 0

    return StepResult(
        step_id=9,
        name="Remote Branch Protection Check",
        target="origin/main, origin/dev2",
        status=status,
        duration=duration,
        summary=summary,
        command="git rev-parse origin/main origin/dev2",
        output=output,
        exit_code=exit_code,
    )


# ── Release Gate Orchestrator ───────────────────────────────────────────────

class ReleaseGate:
    """Orchestrates all release checks, formats tables, and handles CLI flags."""

    def __init__(
        self,
        skip_slow: bool = False,
        backend_only: bool = False,
        frontend_only: bool = False,
        fail_fast: bool = False,
        allow_uncommitted: bool = False,
        as_json: bool = False,
    ):
        self.skip_slow = skip_slow
        self.backend_only = backend_only
        self.frontend_only = frontend_only
        self.fail_fast = fail_fast
        self.allow_uncommitted = allow_uncommitted
        self.as_json = as_json
        self.python_bin = resolve_python_executable()
        self.results: List[StepResult] = []

    def should_run_step(self, step_id: int) -> Tuple[bool, str]:
        """Determine whether a step should be executed or skipped based on flags."""
        # Slow steps: 3 (backend tests), 6 (frontend tests), 7 (frontend build)
        if self.skip_slow and step_id in (3, 6, 7):
            return False, "Skipped via --skip-slow flag"

        # Backend steps: 1, 2, 3, 4, 8, 9
        if self.backend_only and step_id in (5, 6, 7):
            return False, "Skipped via --backend-only flag"

        # Frontend steps: 5, 6, 7, 8, 9
        if self.frontend_only and step_id in (1, 2, 3, 4):
            return False, "Skipped via --frontend-only flag"

        return True, ""

    def run(self) -> int:
        """Run all configured release gate checks."""
        start_gate_time = time.perf_counter()

        step_definitions: List[Tuple[int, str, str, Callable[[], StepResult]]] = [
            (1, "Code Formatting & Linting", "backend/app, backend/ml", lambda: check_ruff_lint(self.python_bin)),
            (2, "Static Type Safety", "backend/app", lambda: check_mypy_typecheck(self.python_bin)),
            (3, "Backend Test Suite", "backend/tests", lambda: check_backend_tests(self.python_bin)),
            (4, "Scripts Test Suite", "scripts/tests", lambda: check_scripts_tests(self.python_bin)),
            (5, "Frontend Typecheck", "frontend/ (tsc)", check_frontend_typecheck),
            (6, "Frontend Unit/Component Tests", "frontend/src (vitest)", check_frontend_tests),
            (7, "Frontend Production Build", "frontend/dist", check_frontend_build),
            (8, "Security & Hygiene Audit", "repository hygiene", lambda: audit_security_and_hygiene(self.allow_uncommitted)),
            (9, "Remote Branch Protection Check", "origin/main & dev2", check_remote_branch_protection),
        ]

        if not self.as_json:
            self._print_header()

        overall_success = True

        for step_id, name, target, executor in step_definitions:
            should_run, reason = self.should_run_step(step_id)

            if not should_run:
                res = StepResult(
                    step_id=step_id,
                    name=name,
                    target=target,
                    status="SKIPPED",
                    duration=0.0,
                    summary=reason,
                )
                self.results.append(res)
                if not self.as_json:
                    self._print_row(res)
                continue

            # Execute step
            res = executor()
            self.results.append(res)

            if not self.as_json:
                self._print_row(res)

            if res.status == "FAIL":
                overall_success = False
                if self.fail_fast:
                    if not self.as_json:
                        print(f"\n{Colors.RED}{Colors.BOLD}Fail-fast triggered at Step {step_id}: {name}. Aborting.{Colors.RESET}")
                        if res.output:
                            print(f"{Colors.DIM}{'-' * 40} Output Snippet {'-' * 40}{Colors.RESET}")
                            print(res.output[:1500])
                            print(f"{Colors.DIM}{'-' * 96}{Colors.RESET}")
                    break

        total_duration = time.perf_counter() - start_gate_time

        if self.as_json:
            report = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "overall_status": "PASS" if overall_success else "FAIL",
                "total_duration_seconds": round(total_duration, 2),
                "steps": [asdict(r) for r in self.results],
            }
            print(json.dumps(report, indent=2))
        else:
            self._print_footer(overall_success, total_duration)

        return 0 if overall_success else 1

    def _print_header(self) -> None:
        print(f"\n{Colors.BOLD}{'=' * 102}")
        print("                       PredictIQ v2 — Unified Release Gate (R11)")
        print(f"{'=' * 102}{Colors.RESET}")
        print(f"{Colors.BOLD}{'#':<3}  {'Check Name':<30}  {'Target':<22}  {'Duration':<9}  {'Status':<8}  {'Summary'}{Colors.RESET}")
        print(f"{'-' * 102}")

    def _print_row(self, r: StepResult) -> None:
        if r.status == "PASS":
            status_str = f"{Colors.GREEN}{Colors.BOLD}PASS{Colors.RESET}"
        elif r.status == "FAIL":
            status_str = f"{Colors.RED}{Colors.BOLD}FAIL{Colors.RESET}"
        elif r.status == "WARN":
            status_str = f"{Colors.YELLOW}{Colors.BOLD}WARN{Colors.RESET}"
        else:
            status_str = f"{Colors.DIM}SKIPPED{Colors.RESET}"

        duration_str = f"{r.duration:.1f}s" if r.duration > 0 else "-"
        print(f"{r.step_id:<3}  {r.name:<30}  {r.target:<22}  {duration_str:<9}  {status_str:<17}  {r.summary}")

    def _print_footer(self, success: bool, total_duration: float) -> None:
        print(f"{'-' * 102}")
        if success:
            status_badge = f"{Colors.GREEN}{Colors.BOLD}[RELEASE GATE: ALL CHECKS PASSED]{Colors.RESET}"
        else:
            status_badge = f"{Colors.RED}{Colors.BOLD}[RELEASE GATE: ONE OR MORE CHECKS FAILED]{Colors.RESET}"

        print(f" {status_badge} Total duration: {total_duration:.2f}s")
        print(f"{Colors.BOLD}{'=' * 102}{Colors.RESET}\n")


# ── CLI Interface ───────────────────────────────────────────────────────────

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="PredictIQ v2 Unified Release Gate (R11)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--skip-slow",
        action="store_true",
        help="Skip long-running backend/frontend test and build steps",
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Execute only backend and repository audit steps (skip frontend)",
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Execute only frontend and repository audit steps (skip backend)",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Abort execution immediately on the first check that fails",
    )
    parser.add_argument(
        "--allow-uncommitted",
        "--dirty",
        dest="allow_uncommitted",
        action="store_true",
        help="Permit uncommitted working tree changes during local testing",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON results instead of ANSI summary table",
    )
    return parser


def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    if args.backend_only and args.frontend_only:
        print(f"{Colors.RED}Error: Cannot specify both --backend-only and --frontend-only.{Colors.RESET}", file=sys.stderr)
        return 2

    gate = ReleaseGate(
        skip_slow=args.skip_slow,
        backend_only=args.backend_only,
        frontend_only=args.frontend_only,
        fail_fast=args.fail_fast,
        allow_uncommitted=args.allow_uncommitted,
        as_json=args.json,
    )
    return gate.run()


if __name__ == "__main__":
    sys.exit(main())
