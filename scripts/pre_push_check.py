#!/usr/bin/env python3
"""
Predictify — Pre-Push Security Validator
========================================
Scans the repository for hardcoded secrets, untracked .env files, and
.gitignore gaps before pushing to GitHub.

Usage:
    python scripts/pre_push_check.py          # from project root
    python -m scripts.pre_push_check          # module mode

Exit codes:
    0 — All checks passed
    1 — One or more critical issues found
"""

import os
import re
import sys
import subprocess

# ── Configuration ──────────────────────────────────────────────────

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCAN_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yml", ".yaml",
    ".toml", ".cfg", ".ini", ".md", ".html", ".css", ".env.example",
}

SKIP_DIRS = {
    "node_modules", ".git", "venv", ".venv", "__pycache__",
    "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "artifacts", ".code-review-graph",
}

SKIP_FILES = {
    "pre_push_check.py",  # Don't flag ourselves
    "package-lock.json",
    "requirements.lock.txt",
}

# Secret patterns — each tuple is (name, regex, is_critical)
SECRET_PATTERNS = [
    ("Supabase URL", r"https://[a-z0-9]+\.supabase\.co", True),
    ("Supabase Anon Key", r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]{20,}", True),
    ("Supabase Service Role Key", r"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[A-Za-z0-9_-]{80,}", True),
    ("Generic API Key Assignment", r"(?:api[_-]?key|apikey|secret[_-]?key)\s*[=:]\s*['\"][A-Za-z0-9_\-]{20,}['\"]", True),
    ("AWS Access Key", r"AKIA[0-9A-Z]{16}", True),
    ("Private Key Block", r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----", True),
    ("Hardcoded Password", r"(?:password|passwd|pwd)\s*[=:]\s*['\"][^'\"]{8,}['\"]", False),
    ("Database URL with credentials", r"(?:postgres|mysql|mongodb)://[^:]+:[^@]+@[^/]+/", True),
]

# .gitignore entries that MUST exist
REQUIRED_GITIGNORE = [
    ".env",
    "*.pyc",
    "__pycache__/",
    "venv/",
    "node_modules/",
    "backend/ml/*.pkl",
]


# ── Helpers ────────────────────────────────────────────────────────

class Colors:
    """ANSI color codes for terminal output."""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_pass(msg: str) -> None:
    print(f"  {Colors.GREEN}[PASS]{Colors.RESET} {msg}")


def log_fail(msg: str) -> None:
    print(f"  {Colors.RED}[FAIL]{Colors.RESET} {msg}")


def log_warn(msg: str) -> None:
    print(f"  {Colors.YELLOW}[WARN]{Colors.RESET} {msg}")


def log_info(msg: str) -> None:
    print(f"  {Colors.CYAN}[INFO]{Colors.RESET} {msg}")


# ── Checks ─────────────────────────────────────────────────────────

def check_secrets() -> list[str]:
    """Scan source files for hardcoded secrets."""
    issues: list[str] = []
    files_scanned = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if filename in SKIP_FILES:
                continue
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SCAN_EXTENSIONS:
                continue

            filepath = os.path.join(root, filename)
            rel_path = os.path.relpath(filepath, PROJECT_ROOT)

            # Skip .env files (they SHOULD have secrets, just not be committed)
            if filename.startswith(".env") and not filename.endswith(".example"):
                continue

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                files_scanned += 1
            except (OSError, UnicodeDecodeError):
                continue

            for name, pattern, is_critical in SECRET_PATTERNS:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    severity = "CRITICAL" if is_critical else "WARNING"
                    issue = f"{severity}: {name} found in {rel_path}"
                    issues.append(issue)
                    if is_critical:
                        log_fail(issue)
                    else:
                        log_warn(issue)

    log_info(f"Scanned {files_scanned} files for secrets")
    return issues


def check_env_not_tracked() -> list[str]:
    """Verify .env files are not tracked by git."""
    issues: list[str] = []

    try:
        result = subprocess.run(
            ["git", "ls-files", "--cached"],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        tracked = result.stdout.strip().split("\n") if result.stdout.strip() else []
    except FileNotFoundError:
        log_warn("git not found — skipping tracked-file check")
        return issues

    env_files = [f for f in tracked if os.path.basename(f).startswith(".env")
                 and not f.endswith(".example")]

    if env_files:
        for ef in env_files:
            issue = f"CRITICAL: .env file is tracked by git: {ef}"
            issues.append(issue)
            log_fail(issue)
    else:
        log_pass("No .env files tracked by git")

    return issues


def check_gitignore() -> list[str]:
    """Verify .gitignore contains required patterns."""
    issues: list[str] = []
    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")

    if not os.path.exists(gitignore_path):
        issues.append("CRITICAL: .gitignore file not found")
        log_fail(".gitignore file not found")
        return issues

    with open(gitignore_path, "r", encoding="utf-8") as f:
        content = f.read()

    for pattern in REQUIRED_GITIGNORE:
        if pattern not in content:
            issue = f"WARNING: Missing .gitignore pattern: {pattern}"
            issues.append(issue)
            log_warn(issue)
        else:
            log_pass(f".gitignore has: {pattern}")

    return issues


def check_env_examples() -> list[str]:
    """Verify .env.example files exist for each .env location."""
    issues: list[str] = []
    env_locations = [
        os.path.join(PROJECT_ROOT, "backend"),
        os.path.join(PROJECT_ROOT, "frontend"),
    ]

    for loc in env_locations:
        example = os.path.join(loc, ".env.example")
        if os.path.exists(example):
            log_pass(f".env.example exists: {os.path.relpath(example, PROJECT_ROOT)}")
        else:
            issue = f"WARNING: Missing .env.example in {os.path.relpath(loc, PROJECT_ROOT)}"
            issues.append(issue)
            log_warn(issue)

    return issues


# ── Main ───────────────────────────────────────────────────────────

def main() -> int:
    """Run all security checks. Returns exit code."""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print(f"  Predictify -- Pre-Push Security Validator")
    print(f"{'=' * 60}{Colors.RESET}\n")

    all_issues: list[str] = []

    print(f"{Colors.BOLD}1. Secret Scanning{Colors.RESET}")
    all_issues.extend(check_secrets())
    print()

    print(f"{Colors.BOLD}2. Git Tracking Check{Colors.RESET}")
    all_issues.extend(check_env_not_tracked())
    print()

    print(f"{Colors.BOLD}3. .gitignore Audit{Colors.RESET}")
    all_issues.extend(check_gitignore())
    print()

    print(f"{Colors.BOLD}4. Environment Templates{Colors.RESET}")
    all_issues.extend(check_env_examples())
    print()

    # Summary
    critical = [i for i in all_issues if i.startswith("CRITICAL")]
    warnings = [i for i in all_issues if i.startswith("WARNING")]

    print(f"{Colors.BOLD}{'-' * 60}")
    print(f"  Summary{Colors.RESET}")
    if critical:
        print(f"  {Colors.RED}X {len(critical)} critical issue(s) found{Colors.RESET}")
        print(f"  {Colors.RED}  Push BLOCKED until resolved.{Colors.RESET}")
    if warnings:
        print(f"  {Colors.YELLOW}! {len(warnings)} warning(s) found{Colors.RESET}")
    if not critical and not warnings:
        print(f"  {Colors.GREEN}OK All checks passed -- safe to push!{Colors.RESET}")
    print()

    return 1 if critical else 0


if __name__ == "__main__":
    sys.exit(main())
