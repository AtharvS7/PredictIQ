"""
Unit and Integration Tests for scripts/docs_audit.py (Checkpoint S08).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import tempfile
from unittest.mock import patch

import pytest
from scripts.docs_audit import (
    audit_banned_words,
    audit_internal_links,
    audit_narrative_hygiene,
    audit_status_headers,
    main,
    slugify_heading,
)


def test_slugify_heading():
    """Verify heading to GitHub-style anchor slug conversion."""
    assert slugify_heading("1. Executive Summary & Vision") == "1-executive-summary-vision"
    assert slugify_heading("P25–P75 Likely Band ($P_{25}$ to $P_{75}$)") == "p25p75-likely-band-p25-to-p75"
    assert slugify_heading("What is Function Point (FP)?") == "what-is-function-point-fp"


def test_status_header_audit_valid(tmp_path: Path):
    """Verify that valid status headers pass."""
    doc = tmp_path / "overview.md"
    doc.write_text(
        "Status: Approved | Applies to: 2.0.0-rc.3 | Verified against commit: cdca041 | Date: 2026-11-08\n\n# Overview\n",
        encoding="utf-8",
    )
    count, violations = audit_status_headers(tmp_path)
    assert count == 1
    assert len(violations) == 0


def test_status_header_audit_invalid(tmp_path: Path):
    """Verify that missing status headers are caught."""
    doc = tmp_path / "bad.md"
    doc.write_text("# Bad Document Without Header\nSome content here.\n", encoding="utf-8")
    count, violations = audit_status_headers(tmp_path)
    assert count == 1
    assert len(violations) == 1
    assert "Missing or invalid Status header" in violations[0]


def test_historical_warning_banner_check(tmp_path: Path):
    """Verify that historical files must have the warning banner."""
    hist_dir = tmp_path / "history"
    hist_dir.mkdir()
    valid_hist = hist_dir / "valid.md"
    valid_hist.write_text(
        "> [!WARNING]\n"
        "> **Historical - superseded; do not use as guidance.** This document reflects an earlier development phase and is preserved solely for auditability.\n\n"
        "# Old Report\n",
        encoding="utf-8",
    )
    invalid_hist = hist_dir / "invalid.md"
    invalid_hist.write_text("# Old Report Without Warning Banner\n", encoding="utf-8")

    count, violations = audit_status_headers(tmp_path)
    assert count == 2
    assert len(violations) == 1
    assert "Missing historical warning banner in history/invalid.md" in violations[0]


def test_banned_words_audit(tmp_path: Path):
    """Verify that banned words trigger violations unless exempted."""
    bad_doc = tmp_path / "bad.md"
    bad_doc.write_text("This platform provides guaranteed delivery times.", encoding="utf-8")
    count, violations = audit_banned_words(tmp_path)
    assert count == 1
    assert len(violations) == 1
    assert "guaranteed" in violations[0].lower()


def test_internal_links_audit(tmp_path: Path):
    """Verify that broken relative links trigger violations."""
    doc1 = tmp_path / "doc1.md"
    doc2 = tmp_path / "doc2.md"
    doc2.write_text("# Doc 2\n", encoding="utf-8")
    doc1.write_text("See [Doc 2](doc2.md) and [Missing](missing.md)\n", encoding="utf-8")

    count, violations = audit_internal_links(tmp_path)
    assert count == 2
    assert len(violations) == 1
    assert "missing.md" in violations[0]


def test_narrative_hygiene_audit(tmp_path: Path):
    """Verify that checkpoint references (CPxx, Rxx) are rejected in active specs."""
    spec_dir = tmp_path / "product"
    spec_dir.mkdir()
    spec = spec_dir / "overview.md"
    spec.write_text("This feature was added in CP08 and verified in R04.\n", encoding="utf-8")

    with patch("scripts.docs_audit.ACTIVE_SPEC_DIRS", [spec_dir]):
        count, violations = audit_narrative_hygiene(tmp_path)
        assert count == 1
        assert len(violations) == 1
        assert "CP08" in violations[0]


def test_main_docs_audit_live():
    """End-to-end integration test verifying that the actual docs directory passes cleanly."""
    exit_code = main([])
    assert exit_code == 0
