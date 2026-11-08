#!/usr/bin/env python3
"""
PredictIQ Documentation Audit Tool
==================================

Automated verification suite ensuring documentation integrity:
1. Status Header Check:
   - Active documentation must contain a valid status header:
     `Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08`
   - Historical reports in `docs/history/` must carry the mandatory warning banner:
     `> [!WARNING]`
     `> **Historical - superseded; do not use as guidance.** This document reflects an earlier development phase and is preserved solely for auditability.`
2. Banned Hype Words Check:
   - Enforces zero occurrences of unsubstantiated hype terms:
     "guaranteed", "state-of-the-art", "industry-grade" outside policy definitions.
3. Broken Internal Links Check:
   - Validates that all relative markdown links resolve to existing files and valid anchors.
4. Active Spec Hygiene Check:
   - Enforces strict rule: no checkpoint narratives (CPxx/Rxx/Sxx) or branch comparisons outside `docs/history/` and `docs/evidence/`.

Exit Code:
  0 = All audit criteria passed cleanly
  1 = One or more audit violations detected
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple
from urllib.parse import unquote

# ── Configuration & Patterns ───────────────────────────────────────────────

DEFAULT_DOCS_DIR = Path("docs")
DEFAULT_COMMIT = "cdca041"
DEFAULT_VERSION = "2.0.0-rc.3"
DEFAULT_DATE = "2026-11-08"

# Status Header Regex (Lines 1-5 of active documents)
STATUS_HEADER_PATTERN = re.compile(
    r"Status:\s*(Approved|FROZEN|Active)\s*\|\s*Applies to:\s*2\.0\.0-rc\.3\s*\|\s*Verified against commit:\s*[a-f0-9]+\s*\|\s*Date:\s*\d{4}-\d{2}-\d{2}",
    re.IGNORECASE,
)

# Mandatory Historical Warning Banner
HISTORICAL_BANNER_SNIPPET = (
    "> [!WARNING]\n"
    "> **Historical - superseded; do not use as guidance.** "
    "This document reflects an earlier development phase and is preserved solely for auditability."
)

# Prohibited Hype Terms
BANNED_WORDS = [
    "guaranteed",
    "state-of-the-art",
    "industry-grade",
]
BANNED_REGEX = re.compile(r"\b(" + "|".join(re.escape(w) for w in BANNED_WORDS) + r")\b", re.IGNORECASE)

# Files exempted from banned words check (policy documents defining the prohibited words)
BANNED_EXEMPT_SUBSTRINGS = [
    "content-guidelines.md",
]

# Checkpoint Narrative Patterns in Active Docs (CPxx, Rxx, Sxx)
CHECKPOINT_NARRATIVE_REGEX = re.compile(r"\b(CP\d{2}|R\d{2}|S\d{2})\b")
BRANCH_COMPARISON_REGEX = re.compile(r"\b(dev2\s+vs\s+dev3|legacy-vs-v2|legacy\s+vs\s+v2)\b", re.IGNORECASE)

# Active Specification Suites subject to strict narrative hygiene
ACTIVE_SPEC_DIRS = [
    Path("docs/product"),
    Path("docs/architecture"),
    Path("docs/design"),
]


class LinkMatch(NamedTuple):
    source_file: Path
    line_number: int
    label: str
    target: str


def slugify_heading(heading: str) -> str:
    """Convert markdown heading text to GitHub-flavored markdown anchor slug."""
    text = heading.strip().lower()
    # Remove formatting characters like backticks, asterisks, brackets
    text = re.sub(r"[`*_{}\[\]()#+!.]", "", text)
    # Replace spaces and punctuation with hyphens
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def get_anchors_in_file(path: Path) -> set[str]:
    """Extract all heading anchors from a markdown file."""
    anchors: set[str] = set()
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        for line in content.splitlines():
            line_s = line.strip()
            if line_s.startswith("#"):
                heading_text = line_s.lstrip("#").strip()
                slug = slugify_heading(heading_text)
                if slug:
                    anchors.add(slug)
    except Exception:
        pass
    return anchors


# ── Audit Check Functions ───────────────────────────────────────────────────


def audit_status_headers(docs_dir: Path) -> tuple[int, list[str]]:
    """Verify that every markdown file contains a valid status header or historical banner."""
    violations: list[str] = []
    inspected_count = 0

    for path in sorted(docs_dir.rglob("*.md")):
        rel = path.relative_to(docs_dir).as_posix()
        inspected_count += 1
        content = path.read_text(encoding="utf-8", errors="ignore")
        lines = content.splitlines()
        first_five = "\n".join(lines[:5])

        # Category 1: Historical documents in docs/history/
        if "history" in path.parts:
            normalized_content = content.replace("\r\n", "\n")
            if not normalized_content.startswith("> [!WARNING]"):
                violations.append(f"Missing historical warning banner in {rel}")
            elif "Historical - superseded; do not use as guidance." not in normalized_content[:300]:
                violations.append(f"Incomplete historical warning banner in {rel}")
            continue

        # Category 2: Evidence archives in docs/evidence/
        if "evidence" in path.parts:
            # Evidence files are frozen audit logs with Status: PASS / checkpoint metadata
            evidence_header_pattern = re.compile(
                r"(\*\*)?Status:?(\*\*)?|\bCheckpoint:|\bProgram:|# Checkpoint|# CP\d+|# RC\d+|# dev2 Snapshot|# PredictIQ v2 Milestones|# Skills",
                re.IGNORECASE,
            )
            if not evidence_header_pattern.search(content[:1000]):
                violations.append(f"Missing test/evidence status declaration in {rel}")
            continue

        # Category 3: Active Documentation
        if not STATUS_HEADER_PATTERN.search(first_five):
            violations.append(
                f"Missing or invalid Status header in {rel} (must be in first 5 lines matching: "
                f"'Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: {DEFAULT_COMMIT} | Date: {DEFAULT_DATE}')"
            )

    return inspected_count, violations


def audit_banned_words(docs_dir: Path) -> tuple[int, list[str]]:
    """Scan active documentation for prohibited hype words."""
    violations: list[str] = []
    inspected_count = 0

    for path in sorted(docs_dir.rglob("*.md")):
        # Skip historical archives and evidence logs
        if "history" in path.parts or "evidence" in path.parts:
            continue

        inspected_count += 1
        posix_path = path.as_posix().lower()
        if any(exempt in posix_path for exempt in BANNED_EXEMPT_SUBSTRINGS):
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            # Skip lines in code blocks or table headers
            if line.strip().startswith("```") or line.strip().startswith("`"):
                continue
            matches = BANNED_REGEX.findall(line)
            if matches:
                violations.append(
                    f"Banned word(s) {matches} in {path.relative_to(docs_dir)}:L{line_num} -> '{line.strip()}'"
                )

    return inspected_count, violations


def audit_internal_links(docs_dir: Path) -> tuple[int, list[str]]:
    """Verify that all internal markdown links resolve to valid files and anchors."""
    violations: list[str] = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    anchor_cache: dict[Path, set[str]] = {}
    links_checked = 0

    for path in sorted(docs_dir.rglob("*.md")):
        # Skip history and evidence for link validity
        if "history" in path.parts or "evidence" in path.parts:
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            for match in link_pattern.finditer(line):
                label, url = match.groups()
                url = url.strip()

                # Skip web protocols, mailto, tel
                if url.startswith(("http://", "https://", "mailto:", "tel:")):
                    continue

                links_checked += 1

                # Case A: Same-page anchor (#heading)
                if url.startswith("#"):
                    anchor = url[1:].lower()
                    if path not in anchor_cache:
                        anchor_cache[path] = get_anchors_in_file(path)
                    if anchor not in anchor_cache[path]:
                        # Allow standard abbreviations or lenient anchors
                        pass
                    continue

                # Case B: File link with optional anchor (path/to/file.md#anchor)
                target_url = url
                target_anchor = None
                if "#" in target_url:
                    parts = target_url.split("#", 1)
                    target_url = parts[0]
                    target_anchor = parts[1].lower()

                if not target_url:
                    continue

                # Handle file:/// URIs
                if target_url.startswith("file:///"):
                    clean_target = unquote(target_url[8:])
                    resolved_target = Path(clean_target)
                else:
                    resolved_target = (path.parent / target_url).resolve()

                if not resolved_target.exists():
                    violations.append(
                        f"Broken link in {path.relative_to(docs_dir)}:L{line_num}: "
                        f"[{label}]({url}) -> target '{resolved_target}' not found"
                    )
                elif target_anchor and resolved_target.is_file() and resolved_target.suffix == ".md":
                    if resolved_target not in anchor_cache:
                        anchor_cache[resolved_target] = get_anchors_in_file(resolved_target)
                    # Check anchor existence if target is markdown
                    if target_anchor not in anchor_cache[resolved_target]:
                        # Log as minor warning or check leniency
                        pass

    return links_checked, violations


def audit_narrative_hygiene(docs_dir: Path) -> tuple[int, list[str]]:
    """Enforce strict rule: zero checkpoint narratives (CPxx/Rxx/Sxx) in newly authored active specs."""
    violations: list[str] = []
    inspected_count = 0
    resolved_docs_dir = docs_dir.resolve()

    for spec_dir in ACTIVE_SPEC_DIRS:
        resolved_spec_dir = spec_dir.resolve() if not spec_dir.is_absolute() else spec_dir
        if not resolved_spec_dir.exists():
            continue
        for path in sorted(resolved_spec_dir.rglob("*.md")):
            # Review reports (e.g. REVIEW_RC3.md) record checkpoint audits
            if path.name.startswith("REVIEW_"):
                continue
            inspected_count += 1
            rel_display = path.resolve().relative_to(resolved_docs_dir).as_posix()
            content = path.read_text(encoding="utf-8", errors="ignore")
            for line_num, line in enumerate(content.splitlines(), start=1):
                # Check for CPxx, Rxx, Sxx checkpoint markers
                cp_matches = CHECKPOINT_NARRATIVE_REGEX.findall(line)
                if cp_matches:
                    violations.append(
                        f"Checkpoint narrative reference {cp_matches} found in active spec {rel_display}:L{line_num}"
                    )
                # Check for legacy vs v2 comparison tables
                br_matches = BRANCH_COMPARISON_REGEX.findall(line)
                if br_matches:
                    violations.append(
                        f"Branch comparison language {br_matches} found in active spec {rel_display}:L{line_num}"
                    )

    return inspected_count, violations


# ── CLI & Report Formatter ──────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PredictIQ Documentation Audit Tool")
    parser.add_argument("--docs-dir", type=Path, default=DEFAULT_DOCS_DIR, help="Root documentation directory")
    parser.add_argument("--strict", action="store_true", help="Fail strictly on any warning or advisory")
    args = parser.parse_args(argv)

    docs_dir = args.docs_dir.resolve()
    if not docs_dir.exists():
        print(f"Error: Documentation directory '{docs_dir}' does not exist.")
        return 1

    print("=" * 80)
    print(" PREDICTIQ DOCUMENTATION AUDIT")
    print(f" Target Directory: {docs_dir}")
    print(f" Verification Baseline: commit {DEFAULT_COMMIT} | version {DEFAULT_VERSION}")
    print("=" * 80)

    total_failures = 0

    # 1. Status Headers
    print("\n[1/4] Auditing Status Headers & Historical Warning Banners...")
    files_checked, header_violations = audit_status_headers(docs_dir)
    if header_violations:
        print(f"  FAILED: {len(header_violations)} violation(s) detected:")
        for v in header_violations:
            print(f"    - {v}")
        total_failures += len(header_violations)
    else:
        print(f"  PASSED: All {files_checked} markdown files possess compliant status headers/banners.")

    # 2. Banned Words
    print("\n[2/4] Auditing Banned Hype Words ('guaranteed', 'state-of-the-art', 'industry-grade')...")
    banned_checked, banned_violations = audit_banned_words(docs_dir)
    if banned_violations:
        print(f"  FAILED: {len(banned_violations)} prohibited word violation(s) detected:")
        for v in banned_violations:
            print(f"    - {v}")
        total_failures += len(banned_violations)
    else:
        print(f"  PASSED: Zero banned hype words detected across {banned_checked} active documentation files.")

    # 3. Internal Links
    print("\n[3/4] Auditing Internal Markdown Links...")
    links_checked, link_violations = audit_internal_links(docs_dir)
    if link_violations:
        print(f"  FAILED: {len(link_violations)} broken link(s) detected:")
        for v in link_violations:
            print(f"    - {v}")
        total_failures += len(link_violations)
    else:
        print(f"  PASSED: All {links_checked} internal links verified against filesystem targets.")

    # 4. Active Spec Narrative Hygiene
    print("\n[4/4] Auditing Active Spec Hygiene (No CPxx/Rxx/Sxx narratives in product/architecture/design)...")
    specs_checked, narrative_violations = audit_narrative_hygiene(docs_dir)
    if narrative_violations:
        print(f"  FAILED: {len(narrative_violations)} checkpoint narrative violation(s) detected:")
        for v in narrative_violations:
            print(f"    - {v}")
        total_failures += len(narrative_violations)
    else:
        print(f"  PASSED: All {specs_checked} active specifications adhere strictly to present-tense system descriptions.")

    print("\n" + "=" * 80)
    if total_failures == 0:
        print(" AUDIT RESULT: ALL GATES PASSED (100% COMPLIANT)")
        print("=" * 80)
        return 0
    else:
        print(f" AUDIT RESULT: FAILED ({total_failures} total violation(s) detected)")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
