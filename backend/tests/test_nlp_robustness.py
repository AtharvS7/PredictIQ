"""
PredictIQ Checkpoint S05 — NLP Adversarial Robustness & Performance Test Suite
=============================================================================
Verifies:
1. Regex Backtracking Safety (ReDoS Protection against catastrophic backtracking).
2. Huge text scaling (50-page scaling under 3.0s p95 latency constraint).
3. DocumentParser PDF/DOCX edge cases (corrupt bytes, missing headers, resource limits).
4. Multi-encoding resilience (UTF-8 with BOM, UTF-16 LE/BE, Latin-1, CP1252, mixed CJK/emojis).
5. Real-world SRS benchmark invariant defense (zero crashes, strictly finite monotonic quantiles).
"""

from __future__ import annotations

import io
import time
import zipfile
from pathlib import Path

import numpy as np
import pytest

from backend.app.services.document_parser import DocumentParser
from backend.app.services.nlp_extractor import (
    FunctionalSizeSizingConfig,
    NLPExtractor,
    nlp_extractor,
)
from backend.ml.eval.run_real_srs_eval import evaluate_real_srs_extractor, load_real_srs_manifest


# ══════════════════════════════════════════════════════════════════════
# 1. Regex Backtracking Safety (ReDoS Defense)
# ══════════════════════════════════════════════════════════════════════

class TestRegexBacktrackingSafety:
    """Verifies that adversarial patterns do not trigger catastrophic regex backtracking."""

    def test_redos_excessive_whitespace_padding(self):
        """Adversarial input with 20,000 trailing spaces before label delimiter."""
        payload = (
            "# Project Specification\n"
            + "Project Name" + " " * 20000 + ": " + "High-Scale FinTech Gateway\n"
            + "System Features:\n"
            + ("- Feature item: " + "A" * 100 + "\n") * 50
        )
        t0 = time.perf_counter()
        res = nlp_extractor.extract(payload)
        elapsed = time.perf_counter() - t0

        assert elapsed < 2.0, f"Extraction took too long (possible ReDoS): {elapsed:.2f}s"
        assert isinstance(res, dict)
        assert res["size_fp"]["value"] > 0

    def test_redos_deeply_nested_parentheses_and_brackets(self):
        """Pathological nesting of brackets and punctuation."""
        nested_junk = "(" * 1000 + "user story authentication module " * 100 + ")" * 1000
        payload = f"# Architecture Spec\n\n{nested_junk}\n\nFeatures include OAuth2 and JWT."
        
        t0 = time.perf_counter()
        res = nlp_extractor.extract(payload)
        elapsed = time.perf_counter() - t0

        assert elapsed < 2.0, f"Extraction timed out on nested brackets: {elapsed:.2f}s"
        assert isinstance(res, dict)
        assert np.isfinite(res["size_fp"]["value"])

    def test_redos_huge_single_token_run(self):
        """Unbroken 50,000 character token without linebreaks or delimiters."""
        unbroken_token = "A" * 50000
        payload = f"# System Overview\n\n{unbroken_token}\n\n# Features\n- Normal requirement 1\n- Normal requirement 2"

        t0 = time.perf_counter()
        res = nlp_extractor.extract(payload)
        elapsed = time.perf_counter() - t0

        assert elapsed < 2.0, f"Single-token extraction exceeded limit: {elapsed:.2f}s"
        assert res["feature_count"]["value"] >= 1

    def test_redos_repetitive_user_story_prefix_pump(self):
        """Repeated user story prefix pump designed to trigger greedy backtracks."""
        pump = ("As a user I want to " + "very "*200 + "quickly login so that I can see data.\n") * 20
        payload = f"# Requirements\n\n{pump}"

        t0 = time.perf_counter()
        res = nlp_extractor.extract(payload)
        elapsed = time.perf_counter() - t0

        assert elapsed < 2.5, f"User story pump exceeded limit: {elapsed:.2f}s"
        assert isinstance(res["size_fp"]["value"], (int, float))


# ══════════════════════════════════════════════════════════════════════
# 2. Huge Text / 50-Page Scaling Tests
# ══════════════════════════════════════════════════════════════════════

class TestHugeTextScaling:
    """Verifies that large 50-page enterprise specifications scale under 3.0s p95."""

    def _generate_50_page_document(self) -> str:
        """Construct synthetic 50-page enterprise document (~17,500 words)."""
        sections = [
            "# Global Enterprise Telematics & Logistics Platform Specification\n",
            "**System Type:** Enterprise Cloud & Edge Telematics Platform\n",
            "**Target Team:** 15 senior distributed software engineers\n",
            "**Project Duration:** 18 calendar months\n\n",
            "## 1. Architectural Scope & Tech Stack\n",
            "The backend platform is built with FastAPI, PostgreSQL, Redis, Apache Kafka, and Docker.\n",
            "The edge telemetry client is developed in Rust and Python on Embedded Linux.\n",
            "External interface integrations include Stripe, AWS S3, Twilio, Datadog, and Salesforce.\n\n",
        ]

        # Generate 50 substantial sections (~350 words each)
        for sec_idx in range(1, 51):
            sections.append(f"## Section {sec_idx}: Logistics Management Subsystem {sec_idx}\n")
            sections.append(
                f"This functional section details subsystem component #{sec_idx} for fleet route optimization, "
                "telemetry signal processing, vehicle maintenance scheduling, and real-time alerts.\n\n"
            )
            sections.append("| Parameter | Specification Requirement | Verification Method |\n")
            sections.append("| :--- | :--- | :--- |\n")
            sections.append(f"| Latency Target | Below 250 milliseconds at 99th percentile | Automated Load Test |\n")
            sections.append(f"| High Availability | 99.95% uptime across geographic regions | Multi-AZ Failover |\n\n")

            sections.append(f"### Functional User Stories for Subsystem {sec_idx}:\n")
            for feat_idx in range(1, 4):
                sections.append(
                    f"- Feature {sec_idx}.{feat_idx}: As a fleet operations manager, I want to track "
                    f"telemetry sensor #{sec_idx}_{feat_idx} so that operational safety is guaranteed.\n"
                )
            sections.append("\n" + ("Prose requirements text describing edge communication protocols. " * 25) + "\n\n")

        return "".join(sections)

    def test_50_page_document_scaling_under_3_seconds(self):
        """A full 50-page (~17,500 words) specification must parse in under 3.0 seconds."""
        doc = self._generate_50_page_document()
        word_count = len(doc.split())
        assert word_count >= 15000, f"Expected >= 15,000 words, got {word_count}"

        # Warmup pass
        _ = nlp_extractor.extract(doc[:2000])

        # Benchmark pass
        t0 = time.perf_counter()
        result = nlp_extractor.extract(doc)
        elapsed = time.perf_counter() - t0

        assert elapsed < 3.0, f"50-page document took {elapsed:.3f}s (must be < 3.0s)"
        
        # Verify finite, monotonic quantile outputs
        size_data = result["size_fp"]
        fp_val = size_data["value"]
        unc = size_data["uncertainty"]
        p10, p50, p90 = unc["p10"], unc["p50"], unc["p90"]

        assert np.isfinite(fp_val) and fp_val > 0
        assert 0 < p10 <= p50 <= p90, f"Quantile ordering violated: p10={p10}, p50={p50}, p90={p90}"
        assert result["feature_count"]["value"] >= 50
        assert len(result["tech_stack"]["value"]) >= 3


# ══════════════════════════════════════════════════════════════════════
# 3. DocumentParser PDF/DOCX Edge Cases
# ══════════════════════════════════════════════════════════════════════

class TestParserEdgeCases:
    """Verifies that DocumentParser gracefully defends against corrupted/malformed binaries."""

    def test_corrupt_pdf_signature(self):
        """PDF without valid %PDF- magic signature raises ValueError."""
        corrupt_bytes = b"NOT_A_PDF_HEADER_DATA"
        with pytest.raises(ValueError, match="Invalid PDF signature"):
            DocumentParser.validate_content(corrupt_bytes, "application/pdf")

    def test_corrupt_pdf_truncated_body(self):
        """PDF with valid header but corrupted/truncated binary raises ValueError."""
        truncated_pdf = b"%PDF-1.4\n%%EOF\nTRUNCATED_BINARY_GARBAGE"
        with pytest.raises(ValueError, match="Could not parse PDF|Ensure it's a text-based PDF"):
            DocumentParser.parse(truncated_pdf, "application/pdf")

    def test_empty_content_rejected(self):
        """Zero-byte document raises ValueError."""
        with pytest.raises(ValueError, match="Document is empty"):
            DocumentParser.validate_content(b"", "text/plain")

    def test_oversized_document_rejected(self):
        """Content exceeding 10 MB resource limit raises ValueError."""
        oversized = b"A" * (10 * 1024 * 1024 + 10)
        with pytest.raises(ValueError, match="exceeds 10 MB"):
            DocumentParser.validate_content(oversized, "text/plain")

    def test_malformed_docx_zip_archive(self):
        """Corrupted DOCX bytes that do not form a valid zip archive raise ValueError."""
        corrupted_docx = b"PK\x03\x04CORRUPTED_ZIP_ENTRY_DATA"
        with pytest.raises(ValueError, match="Invalid DOCX archive"):
            DocumentParser.validate_content(
                corrupted_docx,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    def test_docx_missing_required_xml_entries(self):
        """DOCX archive missing word/document.xml raises ValueError."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("[Content_Types].xml", "<Types/>")
            # Intentionally omit word/document.xml
        
        with pytest.raises(ValueError, match="Invalid DOCX archive"):
            DocumentParser.validate_content(
                buf.getvalue(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )


# ══════════════════════════════════════════════════════════════════════
# 4. Multi-Encoding Resilience
# ══════════════════════════════════════════════════════════════════════

class TestEncodingResilience:
    """Verifies text parsing across UTF-8, UTF-16, Latin-1, and Windows-1252 encodings."""

    def test_utf8_with_bom(self):
        """UTF-8 text containing Byte Order Mark (\xef\xbb\xbf) decodes and extracts cleanly."""
        text = "# Financial Ledger Platform\nFeatures include double-entry ledger and reconciliation.\n" * 5
        content = b"\xef\xbb\xbf" + text.encode("utf-8")
        parsed = DocumentParser.parse(content, "text/plain")
        
        assert "raw_text" in parsed
        res = nlp_extractor.extract(parsed["raw_text"])
        assert res["size_fp"]["value"] > 0

    def test_utf16_le_and_be_bom(self):
        """UTF-16 LE and BE with BOM decode correctly."""
        text = "# Outbreak Reporting System\nSystem features epidemiological contact tracing.\n" * 5
        
        # UTF-16 LE
        le_content = text.encode("utf-16-le")
        le_content = b"\xff\xfe" + le_content
        parsed_le = DocumentParser.parse(le_content, "text/plain")
        assert len(parsed_le["raw_text"]) > 50

        # UTF-16 BE
        be_content = text.encode("utf-16-be")
        be_content = b"\xfe\xff" + be_content
        parsed_be = DocumentParser.parse(be_content, "text/plain")
        assert len(parsed_be["raw_text"]) > 50

    def test_latin1_and_cp1252_special_characters(self):
        """Windows-1252 smart quotes, em-dashes, and currency symbols decode cleanly."""
        text = (
            "# Global Trading Platform — Enterprise Edition\n"
            "“Special Features”: Currency support for € and £, with naïve naïve résumé.\n"
            "- Feature: Real-time settlement engine\n"
            "- Feature: Automated foreign exchange rate converter\n"
        )
        content = text.encode("cp1252", errors="ignore")
        parsed = DocumentParser.parse(content, "text/plain")
        res = nlp_extractor.extract(parsed["raw_text"])
        assert res["feature_count"]["value"] >= 2

    def test_multilingual_and_emoji_text(self):
        """Mixed English, CJK, and emoji text processes without exceptions."""
        text = (
            "# NextGen Mobile Wallet 🚀\n"
            "Features include multi-currency wallet (USD, EUR, 円, ₩) and biometric login 🔐.\n"
            "- Feature 1: Send money to contacts\n"
            "- Feature 2: Scan QR code for point-of-sale payment\n"
            "- Feature 3: Export transaction statement to CSV\n"
        )
        res = nlp_extractor.extract(text)
        assert res["size_fp"]["value"] > 0
        assert np.isfinite(res["size_fp"]["value"])


# ══════════════════════════════════════════════════════════════════════
# 5. Real-World SRS Benchmark Corpus Invariants
# ══════════════════════════════════════════════════════════════════════

class TestRealSRSBenchmarkCorpus:
    """Verifies that all 18 real public documents execute with zero crashes and finite outputs."""

    @pytest.fixture(scope="class")
    def real_srs_data(self):
        return load_real_srs_manifest()

    def test_real_srs_corpus_exists_and_populated(self, real_srs_data):
        """Ensure >= 15 real public requirements documents are present with manifest."""
        real_dir, manifest = real_srs_data
        assert len(manifest) >= 15, f"Expected >= 15 real documents, got {len(manifest)}"

        for doc_id, meta in manifest.items():
            file_path = real_dir / meta["filename"]
            assert file_path.exists(), f"Missing real SRS document: {file_path}"
            assert file_path.stat().st_size > 400, f"Document suspiciously small: {file_path}"

    def test_real_srs_zero_crashes_and_finite_outputs(self):
        """Execute full evaluation harness on all real documents and verify zero crashes."""
        results = evaluate_real_srs_extractor()
        rob = results["robustness_invariants"]

        assert rob["zero_crashes"] is True, f"Detected crashes: {results['crashes']}"
        assert rob["zero_non_finite"] is True, f"Detected non-finite issues: {results['non_finite_issues']}"
        assert rob["all_invariants_pass"] is True

    def test_real_srs_p95_latency_under_3_seconds(self):
        """Profile runtime performance and verify overall p95 latency is strictly under 3.0s."""
        results = evaluate_real_srs_extractor()
        p95 = results["performance_profile"]["p95_seconds"]
        
        assert p95 < 3.0, f"Real SRS p95 latency {p95:.3f}s exceeds 3.0s target"

    def test_configurable_sizing_assumptions_applied(self):
        """Verify custom FunctionalSizeSizingConfig modulates derived sizing and preserves monotonicity."""
        custom_config = FunctionalSizeSizingConfig(
            fp_per_story=12.0,
            fp_per_story_p10=6.0,
            fp_per_story_p90=20.0,
            fp_per_integration=8.0,
            fp_per_integration_p10=4.0,
            fp_per_integration_p90=16.0,
            uncertainty_p10_ratio=0.70,
            uncertainty_p90_ratio=1.40,
        )
        custom_extractor = NLPExtractor(sizing_config=custom_config)
        sample_doc = (
            "# Task Tracker Tool\n"
            "- Feature: Task assignment\n"
            "- Feature: Real-time comments\n"
            "- Integration: Slack notification webhook\n"
            "- Integration: GitHub issues sync\n"
        )
        res = custom_extractor.extract(sample_doc)
        size_data = res["size_fp"]
        
        assert size_data["is_assumption"] is True
        assert "assumption_parameters" in size_data
        assert size_data["assumption_parameters"]["fp_per_story_nominal"] == 12.0
        
        p10 = size_data["uncertainty"]["p10"]
        p50 = size_data["uncertainty"]["p50"]
        p90 = size_data["uncertainty"]["p90"]
        assert 0 < p10 <= p50 <= p90
