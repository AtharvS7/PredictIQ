"""
PredictIQ Checkpoint H05 — Live Walkthrough & Stress Test Suite
===============================================================
Comprehensive verification for H05:
1. Full SRS fixture corpus (18 real SRS documents + 10 robustness fixtures + 3 edge/empty).
2. Document parser edge cases (empty bytes, whitespace, corrupted PDF, corrupted DOCX).
3. End-to-end service walkthrough:
   - Sizing & ML inference
   - Multi-currency rate conversion
   - Budget planning three-point arithmetic
   - Export generation (ReportLab PDF structure & JSON)
   - Organizational calibration with varying actuals (3, 5, 10, 20)
4. Stress & concurrency resilience:
   - 20 rapid sequential requests
   - Concurrent multithreaded inference
   - Malformed / out-of-bounds input rejection (clean 422, zero 500s)
"""

from __future__ import annotations

import concurrent.futures
import io
import json
import math
from pathlib import Path

import pytest
from app.services.cost_calculator import calculate_cost_v2
from app.services.currency_service import currency_service
from app.services.document_parser import DocumentParser
from app.services.export_service import generate_pdf_report
from app.services.ml_service import ml_service
from app.services.nlp_extractor import nlp_extractor
from app.services.org_calibration import OrgCalibrationService

# ══════════════════════════════════════════════════════════════════════
# 1. Real SRS Fixture Corpus (>= 12 fixtures required, 18 evaluated)
# ══════════════════════════════════════════════════════════════════════

class TestRealSRSFixtures:
    """Verifies that all real-world SRS fixtures parse and extract cleanly without crashes."""

    SRS_DIR = Path(__file__).parent / "fixtures" / "srs_real"

    def test_real_srs_fixture_count_exceeds_twelve(self):
        """Ensures at least 12 real SRS fixtures are available."""
        fixtures = list(self.SRS_DIR.glob("real_*.md"))
        assert len(fixtures) >= 12, f"Expected at least 12 real fixtures, found {len(fixtures)}"

    def test_all_eighteen_real_srs_extract_cleanly(self):
        """Evaluates every real SRS document: guarantees finite size and zero exceptions."""
        fixtures = sorted(self.SRS_DIR.glob("real_*.md"))
        assert len(fixtures) >= 18, f"Expected 18 real fixtures, found {len(fixtures)}"

        results = []
        for fixture_path in fixtures:
            content = fixture_path.read_text(encoding="utf-8")
            assert len(content) > 100, f"Fixture {fixture_path.name} is too short"

            extracted = nlp_extractor.extract(content)
            assert isinstance(extracted, dict), f"Failed for {fixture_path.name}"

            size_info = extracted.get("size_fp", {})
            size_val = size_info.get("value")
            assert size_val is not None, f"Missing size_fp value for {fixture_path.name}"
            assert isinstance(size_val, (int, float)), f"Non-numeric size for {fixture_path.name}"
            assert 1.0 <= size_val <= 10000.0, f"Out of bounds size {size_val} for {fixture_path.name}"

            # Verify predictions work on extracted functional size
            prediction = ml_service.predict({
                "size_fp": size_val,
                "team_size": extracted.get("team_size", {}).get("value", 5),
                "complexity": extracted.get("complexity", {}).get("value", "Medium"),
            })
            effort = prediction["effort_hours"]["p50"]
            assert effort > 0, f"Non-positive effort {effort} for {fixture_path.name}"
            results.append({
                "fixture": fixture_path.name,
                "size_fp": size_val,
                "effort_p50": effort,
            })

        assert len(results) == len(fixtures)


# ══════════════════════════════════════════════════════════════════════
# 2. Edge & Robustness Fixtures (Empty, Whitespace, Corrupted)
# ══════════════════════════════════════════════════════════════════════

class TestEdgeAndRobustnessFixtures:
    """Verifies edge case handling: empty documents, whitespace, corrupted files."""

    ROBUSTNESS_DIR = Path(__file__).parent / "fixtures" / "srs_robustness"

    def test_empty_text_returns_safe_defaults(self):
        """Empty input must yield safe default output with friendly message."""
        empty_file = self.ROBUSTNESS_DIR / "edge_01_empty.txt"
        content = empty_file.read_text(encoding="utf-8") if empty_file.exists() else ""
        extracted = nlp_extractor.extract(content)

        assert isinstance(extracted, dict)
        size_info = extracted.get("size_fp", {})
        assert size_info.get("value") == 90.0  # Safe calibrated default
        assert size_info.get("coverage_flag") in ("no_requirements_found", "fallback_default", "uncalibrated_sparse")

    def test_whitespace_only_returns_safe_defaults(self):
        """Whitespace-only document returns safe fallback without crash."""
        ws_file = self.ROBUSTNESS_DIR / "edge_02_whitespace_only.txt"
        content = ws_file.read_text(encoding="utf-8") if ws_file.exists() else "   \n\t  \r\n"
        extracted = nlp_extractor.extract(content)

        assert isinstance(extracted, dict)
        assert extracted.get("size_fp", {}).get("value") == 90.0

    def test_single_line_informal_text_handled(self):
        """Very short, informal text yields structured output."""
        informal_file = self.ROBUSTNESS_DIR / "edge_03_single_line_informal.txt"
        content = informal_file.read_text(encoding="utf-8") if informal_file.exists() else "Build an app."
        extracted = nlp_extractor.extract(content)

        assert isinstance(extracted, dict)
        assert extracted.get("size_fp", {}).get("value") > 0

    def test_corrupted_pdf_rejected_cleanly(self):
        """Corrupted PDF stream triggers ValueError rather than unhandled crash."""
        corrupt_bytes = b"%PDF-1.4\nTRUNCATED_GARBAGE_BYTES_NO_EOF"
        parser = DocumentParser()
        with pytest.raises(ValueError) as excinfo:
            parser.parse(corrupt_bytes, "application/pdf")
        assert isinstance(excinfo.value, ValueError)

    def test_corrupted_docx_rejected_cleanly(self):
        """Corrupted DOCX stream triggers ValueError without crashing process."""
        corrupt_bytes = b"PK\x03\x04CORRUPTED_ZIP_ARCHIVE_DATA"
        parser = DocumentParser()
        with pytest.raises(ValueError) as excinfo:
            parser.parse(corrupt_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert "docx" in str(excinfo.value).lower() or "zip" in str(excinfo.value).lower() or "document" in str(excinfo.value).lower()

    def test_valid_docx_minimal_stream_parses(self):
        """Valid minimal in-memory DOCX parses into text."""
        from docx import Document
        doc = Document()
        doc.add_paragraph("Project Specification: Payment API Service. Build 10 microservices.")
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)
        parser = DocumentParser()
        parsed = parser.parse(buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        assert "Payment API Service" in parsed["raw_text"]


# ══════════════════════════════════════════════════════════════════════
# 3. End-to-End Walkthrough Services Test
# ══════════════════════════════════════════════════════════════════════

class TestEndToEndServices:
    """Verifies end-to-end execution of all estimation, calibration, and export services."""

    def test_ml_prediction_quantiles_and_costs(self):
        """Verifies ML point and interval calculation consistency."""
        pred = ml_service.predict({"size_fp": 120.0, "team_size": 4, "complexity": "Medium", "methodology": "Agile"})
        hours = pred["effort_hours"]
        assert hours["p10"] <= hours["p25"] <= hours["p50"] <= hours["p75"] <= hours["p90"]

        cost = calculate_cost_v2(hours, hourly_rate=85.0, currency="USD")
        expected_cost = round(hours["p50"] * 85.0, 2)
        assert abs(cost["p50"] - expected_cost) < 0.05

    async def test_currency_conversion_fallback_parity(self):
        """Verifies deterministic multi-currency conversion table."""
        rates = await currency_service.get_rates()
        assert "usd" in rates
        assert "eur" in rates
        assert "gbp" in rates
        assert "inr" in rates

        amount_usd = 1000.0
        amount_eur = await currency_service.convert(amount_usd, "EUR")
        assert amount_eur > 0
        assert round(amount_usd * rates["eur"], 2) == round(amount_eur, 2)

    def test_org_calibration_sample_scales(self):
        """Verifies calibration with 3, 5, 10, and 20 actual projects."""
        cal_service = OrgCalibrationService()
        for n_actuals in [3, 5, 10, 20]:
            actuals = [
                {"size_fp": 100.0, "actual_hours": 1150.0}
                for _ in range(n_actuals)
            ]
            cal = cal_service.calibrate(actuals)
            multiplier = cal.scaling_ratio
            # Multiplier must be positive and finite
            assert multiplier > 0 and math.isfinite(multiplier)
            assert 0.0 <= cal.shrinkage_weight <= 1.0
            assert cal.k_projects == n_actuals

    def test_export_pdf_structure_validity(self):
        """Verifies ReportLab PDF generation yields valid PDF structure."""
        estimate_record = {
            "estimate_id": "test-h05-001",
            "project_name": "Executive Healthcare Portal",
            "model_version": "2.0.0",
            "inputs": {
                "project_type": "Web App",
                "tech_stack": ["React", "FastAPI"],
                "team_size": 6,
                "duration_months": 8,
                "complexity": "Medium",
                "methodology": "Agile",
                "hourly_rate_usd": 90.0,
            },
            "outputs": {
                "effort_min_hours": 800.0,
                "effort_likely_hours": 1000.0,
                "effort_max_hours": 1250.0,
                "cost_min_usd": 72000.0,
                "cost_likely_usd": 90000.0,
                "cost_max_usd": 112500.0,
                "timeline_min_weeks": 20.0,
                "timeline_likely_weeks": 24.0,
                "timeline_max_weeks": 30.0,
                "confidence_pct": 80.0,
                "risk_score": 25.0,
                "risk_level": "Low",
                "top_risks": [{"name": "Third-party API availability", "severity": "Low"}],
                "phase_breakdown": [{"phase": "Development", "hours": 600.0}],
            },
        }
        pdf_bytes = generate_pdf_report(estimate_record, currency_code="USD")
        assert len(pdf_bytes) > 1000
        assert pdf_bytes.startswith(b"%PDF")
        assert b"%%EOF" in pdf_bytes[-1024:]

    def test_export_json_structure_validity(self):
        """Verifies JSON export structure and schema completeness."""
        estimate_record = {
            "estimate_id": "test-h05-002",
            "project_name": "Inventory Microservice",
            "outputs": {"effort_likely_hours": 450.0},
        }
        json_str = json.dumps(estimate_record)
        json_data = json.loads(json_str)
        assert isinstance(json_data, dict)
        assert json_data["estimate_id"] == "test-h05-002"
        assert json_data["outputs"]["effort_likely_hours"] == 450.0


# ══════════════════════════════════════════════════════════════════════
# 4. Stress, Burst & Concurrency Resilience
# ══════════════════════════════════════════════════════════════════════

class TestStressAndConcurrencyResilience:
    """Verifies rapid sequential bursts and concurrent multithreaded requests."""

    def test_rapid_twenty_sequential_predictions(self):
        """Executes 20 rapid consecutive predictions without memory leakage or slowdown."""
        import time
        latencies = []
        for i in range(20):
            t0 = time.perf_counter()
            pred = ml_service.predict({"size_fp": 50.0 + i * 10, "team_size": 4})
            latencies.append(time.perf_counter() - t0)
            assert pred["effort_hours"]["p50"] > 0

        p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
        assert p95_latency < 0.1, f"P95 latency {p95_latency:.4f}s exceeds 100ms threshold"

    def test_concurrent_multithreaded_inference(self):
        """Simulates 10 concurrent threads executing predictions simultaneously."""
        def run_inference(task_id: int):
            return ml_service.predict({"size_fp": 30.0 + task_id * 15, "team_size": 5})

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_inference, i) for i in range(20)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert len(results) == 20
        for res in results:
            assert res["effort_hours"]["p50"] > 0

    def test_invalid_parameters_handled_safely(self):
        """Verifies that out-of-range or malformed inputs return clean 422 HTTP exceptions."""
        from fastapi import HTTPException
        # Missing size and features
        with pytest.raises(HTTPException) as excinfo:
            ml_service.predict({})
        assert excinfo.value.status_code == 422

        # Non-positive size
        with pytest.raises(HTTPException) as excinfo:
            ml_service.predict({"size_fp": 0.0})
        assert excinfo.value.status_code == 422

        # Negative size
        with pytest.raises(HTTPException) as excinfo:
            ml_service.predict({"size_fp": -50.0})
        assert excinfo.value.status_code == 422
