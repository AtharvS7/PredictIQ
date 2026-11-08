"""
PredictIQ v2 — Test Suite for NLP Extractor on Gold Standard SRS Benchmark (Checkpoint R09)
==========================================================================================
Verifies that:
1. Gold standard SRS fixtures (>= 30 documents across 6 domains) load reliably.
2. The NLP extractor runs without crashing on every gold document.
3. Extracted features satisfy mathematical bounds:
   - size_fp is strictly finite, positive, and satisfies non-crossing quantiles (p10 <= p50 <= p90).
   - feature_count and integration_count are bounded integers.
   - tech_stack is a non-empty list of detected strings.
   - complexity is a valid ordinal level.
4. Benchmark quality gates strictly pass:
   - Functional size MdAPE <= 20.0%
   - Tech stack classification Micro-F1 >= 0.8500
   - Feature extraction recall >= 90.0%
   - Integration count MAE <= 1.00
   - Zero crashes or non-finite outputs across all domains
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

import backend.app.services.nlp_extractor as nlp_mod

# Backward-compatible hook
if not hasattr(nlp_mod, "extract_features_from_document"):
    nlp_mod.extract_features_from_document = nlp_mod.nlp_extractor.extract

from backend.app.services.nlp_extractor import extract_features_from_document
from backend.ml.eval.run_r09_srs_eval import evaluate_srs_extractor, load_gold_srs_suite


@pytest.fixture(scope="module")
def gold_suite_data() -> tuple[Path, dict[str, Any]]:
    """Fixture providing the SRS fixtures directory and loaded annotations."""
    return load_gold_srs_suite()


class TestNLPGoldSRS:
    """Automated benchmark tests for NLP parameter extraction on gold SRS documents."""

    def test_gold_suite_fixtures_exist(self, gold_suite_data):
        """Verify >= 30 gold standard documents exist covering 6 distinct software domains."""
        srs_dir, annotations = gold_suite_data
        
        assert len(annotations) >= 30, f"Expected >= 30 documents, got {len(annotations)}"
        
        # Verify 6 distinct software domains
        domains = {meta["domain"] for meta in annotations.values()}
        expected_domains = {
            "Web Applications",
            "Mobile Applications",
            "Cloud / REST APIs & Microservices",
            "Data & Analytics Pipelines",
            "Enterprise / ERP Systems",
            "Embedded / IoT / Systems",
        }
        assert expected_domains.issubset(domains), f"Missing domains: {expected_domains - domains}"
        
        # Verify each domain has >= 5 documents
        for dom in expected_domains:
            count = sum(1 for m in annotations.values() if m["domain"] == dom)
            assert count >= 5, f"Domain '{dom}' has fewer than 5 documents ({count})"
        
        # Verify all fixture markdown files exist on disk and have meaningful content
        for meta in annotations.values():
            file_path = srs_dir / meta["filename"]
            assert file_path.exists(), f"Missing SRS file: {file_path}"
            assert file_path.stat().st_size > 150, f"Document too small: {file_path}"

    def test_nlp_extractor_no_crash_on_gold_suite(self, gold_suite_data):
        """Verify extract_features_from_document processes every gold document without crashing."""
        srs_dir, annotations = gold_suite_data
        required_keys = {
            "size_fp",
            "tech_stack",
            "feature_count",
            "integration_count",
            "complexity",
            "project_type",
            "team_size",
            "duration_months",
            "methodology",
        }
        
        for doc_id, meta in annotations.items():
            doc_path = srs_dir / meta["filename"]
            text = doc_path.read_text(encoding="utf-8")
            
            result = extract_features_from_document(text)
            assert isinstance(result, dict), f"Failed for {doc_id}: expected dict, got {type(result)}"
            assert required_keys.issubset(set(result.keys())), f"Missing keys in {doc_id}: {required_keys - set(result.keys())}"

    def test_size_fp_finite_and_calibrated_bounds(self, gold_suite_data):
        """Verify functional size is finite, positive, and satisfies monotonic non-crossing quantiles."""
        srs_dir, annotations = gold_suite_data
        
        for doc_id, meta in annotations.items():
            doc_path = srs_dir / meta["filename"]
            text = doc_path.read_text(encoding="utf-8")
            result = extract_features_from_document(text)
            
            size_data = result.get("size_fp", {})
            val = size_data.get("value")
            assert isinstance(val, (int, float)), f"{doc_id}: size_fp value not numeric"
            assert np.isfinite(val), f"{doc_id}: size_fp value not finite ({val})"
            assert val > 0.0, f"{doc_id}: size_fp must be strictly positive ({val})"
            
            # Confidence must be bounded in [0.0, 1.0]
            conf = size_data.get("confidence")
            assert isinstance(conf, (int, float)), f"{doc_id}: confidence not numeric"
            assert 0.0 <= conf <= 1.0, f"{doc_id}: confidence out of [0, 1] ({conf})"
            
            # Uncertainty non-crossing bounds: 0 < p10 <= p50 <= p90
            uncertainty = size_data.get("uncertainty", {})
            p10 = uncertainty.get("p10")
            p50 = uncertainty.get("p50")
            p90 = uncertainty.get("p90")
            
            assert all(isinstance(p, (int, float)) and np.isfinite(p) for p in (p10, p50, p90)), (
                f"{doc_id}: non-finite uncertainty quantiles"
            )
            assert 0 < p10 <= p50 <= p90, f"{doc_id}: quantile non-crossing violated: p10={p10}, p50={p50}, p90={p90}"

    def test_tech_stack_extraction_validity(self, gold_suite_data):
        """Verify tech stack is returned as a non-empty list of detected strings."""
        srs_dir, annotations = gold_suite_data
        
        for doc_id, meta in annotations.items():
            doc_path = srs_dir / meta["filename"]
            text = doc_path.read_text(encoding="utf-8")
            result = extract_features_from_document(text)
            
            tech_data = result.get("tech_stack", {})
            techs = tech_data.get("value")
            assert isinstance(techs, list), f"{doc_id}: tech_stack value is not a list"
            assert len(techs) > 0, f"{doc_id}: tech_stack must not be empty"
            assert all(isinstance(t, str) and len(t) > 0 for t in techs), f"{doc_id}: invalid tech stack element"

    def test_feature_and_integration_counts_bounded(self, gold_suite_data):
        """Verify feature_count and integration_count are valid bounded integers."""
        srs_dir, annotations = gold_suite_data
        valid_complexities = {"Low", "Medium", "High", "Very High"}
        
        for doc_id, meta in annotations.items():
            doc_path = srs_dir / meta["filename"]
            text = doc_path.read_text(encoding="utf-8")
            result = extract_features_from_document(text)
            
            fc = result.get("feature_count", {}).get("value")
            assert isinstance(fc, int) and 1 <= fc <= 200, f"{doc_id}: invalid feature_count {fc}"
            
            ic = result.get("integration_count", {}).get("value")
            assert isinstance(ic, int) and 2 <= ic <= 30, f"{doc_id}: invalid integration_count {ic}"
            
            comp = result.get("complexity", {}).get("value")
            assert comp in valid_complexities, f"{doc_id}: invalid complexity {comp}"

    def test_nlp_benchmark_quality_gates(self):
        """Execute full benchmark harness and assert all 5 quality gates pass."""
        results = evaluate_srs_extractor()
        gates = results["quality_gates"]
        
        assert results["sample_size"] >= 30, f"Expected >= 30 sample size, got {results['sample_size']}"
        assert results["domains_evaluated"] == 6, f"Expected 6 domains, got {results['domains_evaluated']}"
        
        # Gate 1: Functional Size MdAPE <= 20.0%
        assert gates["gate_1_functional_size_mdape"]["pass"] is True, (
            f"Gate 1 failed: {gates['gate_1_functional_size_mdape']['achieved']}"
        )
        
        # Gate 2: Tech Stack Micro-F1 >= 0.8500
        assert gates["gate_2_tech_stack_micro_f1"]["pass"] is True, (
            f"Gate 2 failed: {gates['gate_2_tech_stack_micro_f1']['achieved']}"
        )
        
        # Gate 3: Feature Extraction Recall >= 90.0%
        assert gates["gate_3_feature_extraction_recall"]["pass"] is True, (
            f"Gate 3 failed: {gates['gate_3_feature_extraction_recall']['achieved']}"
        )
        
        # Gate 4: Integration Count MAE <= 1.00
        assert gates["gate_4_integration_count_mae"]["pass"] is True, (
            f"Gate 4 failed: {gates['gate_4_integration_count_mae']['achieved']}"
        )
        
        # Gate 5: Zero crashes & non-finite outputs
        assert gates["gate_5_zero_crashes_and_finite_outputs"]["pass"] is True, (
            f"Gate 5 failed: {gates['gate_5_zero_crashes_and_finite_outputs']['achieved']}"
        )
        
        assert gates["all_gates_pass"] is True
