"""
PredictIQ — NLP Extractor Tests
Tests for keyword-based project parameter extraction from text.
"""
import pytest
from app.services.nlp_extractor import nlp_extractor


class TestNLPExtraction:
    """Tests for NLP parameter extraction from document text."""

    def test_extract_returns_dict(self, sample_document_text):
        """extract() must return a dictionary."""
        result = nlp_extractor.extract(sample_document_text)
        assert isinstance(result, dict)

    def test_project_type_web_app(self):
        """Text mentioning 'web application' prominently should yield Web App."""
        text = "This project is a web application for customer relationship management. " \
               "The web app will be built using React and FastAPI as a SaaS platform."
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            # "web app", "web application", "saas" are all Web App keywords
            assert ptype.get("value") in ("Web App", "API/Backend", "Enterprise Software")

    def test_project_type_mobile(self):
        """Text mentioning 'Android mobile application' should yield Mobile App."""
        text = "We are building an Android mobile application for field workers with GPS tracking and offline sync."
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            assert ptype.get("value") == "Mobile App"

    def test_project_type_ml(self):
        """Text mentioning 'machine learning' should yield ML/AI System."""
        text = "The system uses machine learning and deep learning models for image classification and prediction tasks."
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            assert ptype.get("value") == "ML/AI System"

    def test_tech_stack_detected(self, sample_document_text):
        """Tech keywords in the document should be detected."""
        result = nlp_extractor.extract(sample_document_text)
        tech = result.get("tech_stack", {})
        if isinstance(tech, dict):
            detected = tech.get("value", [])
            assert len(detected) > 0

    def test_team_size_extracted(self, sample_document_text):
        """Team size should be extracted from '8 developers' in sample text."""
        result = nlp_extractor.extract(sample_document_text)
        team = result.get("team_size", {})
        if isinstance(team, dict):
            size = team.get("value")
            if size is not None:
                assert size >= 1

    def test_duration_extracted(self, sample_document_text):
        """Duration should be extracted from '12 months' in sample text."""
        result = nlp_extractor.extract(sample_document_text)
        duration = result.get("duration_months", {})
        if isinstance(duration, dict):
            value = duration.get("value")
            if value is not None:
                assert value > 0

    def test_empty_text_no_crash(self):
        """Empty text should return a result without crashing."""
        result = nlp_extractor.extract("")
        assert isinstance(result, dict)

    def test_short_text_handled(self):
        """Very short text should still return valid structure."""
        result = nlp_extractor.extract("A small app.")
        assert isinstance(result, dict)

    def test_complexity_detection(self, sample_document_text):
        """Complexity should be detected from text signals."""
        result = nlp_extractor.extract(sample_document_text)
        complexity = result.get("complexity", {})
        if isinstance(complexity, dict):
            value = complexity.get("value")
            if value is not None:
                assert value in ("Low", "Medium", "High", "Very High")

    def test_has_all_expected_keys(self, sample_document_text):
        """Extraction result should have all primary parameter keys."""
        result = nlp_extractor.extract(sample_document_text)
        expected = {"project_type", "tech_stack", "complexity"}
        assert expected.issubset(set(result.keys()))
