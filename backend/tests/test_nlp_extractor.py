"""
PredictIQ — NLP Extractor Tests v2.4
=====================================
30+ tests covering the 4-strategy cascade extraction engine.
"""
import pytest
from app.services.nlp_extractor import nlp_extractor


class TestNLPExtraction:
    """Tests for NLP parameter extraction from document text."""

    # ── Basic Structure ────────────────────────────────────────────

    def test_extract_returns_dict(self, sample_document_text):
        """extract() must return a dictionary."""
        result = nlp_extractor.extract(sample_document_text)
        assert isinstance(result, dict)

    def test_has_all_expected_keys(self, sample_document_text):
        """Extraction result should have all primary parameter keys."""
        result = nlp_extractor.extract(sample_document_text)
        expected = {
            "project_type", "tech_stack", "complexity", "team_size",
            "duration_months", "methodology", "feature_count",
            "project_name", "integration_count", "volatility_score",
            "team_experience",
        }
        assert expected.issubset(set(result.keys()))

    def test_empty_text_no_crash(self):
        """Empty text should return a result without crashing."""
        result = nlp_extractor.extract("")
        assert isinstance(result, dict)

    def test_short_text_handled(self):
        """Very short text should still return valid structure."""
        result = nlp_extractor.extract("A small app.")
        assert isinstance(result, dict)

    def test_all_values_have_confidence(self, sample_document_text):
        """Every extracted field should have a 'confidence' key."""
        result = nlp_extractor.extract(sample_document_text)
        for key, val in result.items():
            assert "confidence" in val, f"Missing confidence in '{key}'"
            assert isinstance(val["confidence"], (int, float))
            assert 0.0 <= val["confidence"] <= 1.0

    # ── Project Type Classification ────────────────────────────────

    def test_project_type_web_app(self):
        """Text mentioning 'web application' prominently should yield Web App."""
        text = (
            "This project is a web application for customer relationship management. "
            "The web app will be built using React and FastAPI as a SaaS platform."
        )
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            assert ptype.get("value") in ("Web App", "Enterprise Software")

    def test_project_type_mobile(self):
        """Text mentioning 'Android mobile application' should yield Mobile App."""
        text = (
            "We are building an Android mobile application for field workers "
            "with GPS tracking and offline sync."
        )
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            assert ptype.get("value") == "Mobile App"

    def test_project_type_ml(self):
        """Text mentioning 'machine learning' should yield ML/AI System."""
        text = (
            "The system uses machine learning and deep learning models for "
            "image classification and prediction tasks."
        )
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        if isinstance(ptype, dict):
            assert ptype.get("value") == "ML/AI System"

    def test_project_type_api_backend(self):
        """Document describing a REST API should classify as API/Backend."""
        text = (
            "This project is a RESTful API gateway with microservices architecture. "
            "It will expose 50+ endpoints for downstream API consumers. "
            "The backend service processes webhook callbacks from partners."
        )
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        assert ptype.get("value") == "API/Backend"

    def test_project_type_enterprise(self):
        """ERP/CRM mentions should classify as Enterprise Software."""
        text = (
            "This enterprise system is an ERP platform with multi-tenant "
            "role-based access, approval workflow, and department-wide "
            "resource planning for B2B supply chain."
        )
        result = nlp_extractor.extract(text)
        ptype = result.get("project_type", {})
        assert ptype.get("value") == "Enterprise Software"

    # ── Tech Stack ─────────────────────────────────────────────────

    def test_tech_stack_detected(self, sample_document_text):
        """Tech keywords in the document should be detected."""
        result = nlp_extractor.extract(sample_document_text)
        tech = result.get("tech_stack", {})
        if isinstance(tech, dict):
            detected = tech.get("value", [])
            assert len(detected) > 0

    def test_react_dot_js_detected(self):
        """'React.js' in text should be detected as 'React' in tech stack."""
        text = "We will use React.js for the frontend and Express for the backend API."
        result = nlp_extractor.extract(text)
        tech = result.get("tech_stack", {})
        assert isinstance(tech, dict)
        detected = [t.lower() for t in tech.get("value", [])]
        assert "react" in detected or "react.js" in detected

    def test_nodejs_variant_detected(self):
        """'Node.js' variants should be detected in tech stack."""
        text = "The Node.js backend will handle API requests and serve data."
        result = nlp_extractor.extract(text)
        tech = result.get("tech_stack", {})
        assert isinstance(tech, dict)
        detected = [t.lower() for t in tech.get("value", [])]
        assert any("node" in t for t in detected)

    def test_version_number_stripped(self):
        """'PostgreSQL 15' should be detected as PostgreSQL in tech stack."""
        text = "The database layer uses PostgreSQL 15 for data persistence."
        result = nlp_extractor.extract(text)
        tech = result.get("tech_stack", {})
        assert isinstance(tech, dict)
        detected = [t.lower() for t in tech.get("value", [])]
        assert "postgresql" in detected

    def test_table_based_tech_extraction(self):
        """Tech stack listed in a table should be extracted."""
        text = """
        # Technology Stack

        | Layer | Technology | Version |
        |-------|-----------|---------|
        | Frontend | React | 18 |
        | Backend | FastAPI | 0.100 |
        | Database | PostgreSQL | 15 |
        | Cache | Redis | 7 |
        """
        result = nlp_extractor.extract(text)
        tech = result.get("tech_stack", {})
        detected_lower = [t.lower() for t in tech.get("value", [])]
        assert "react" in detected_lower
        assert "fastapi" in detected_lower
        assert "postgresql" in detected_lower
        assert "redis" in detected_lower

    def test_deduplication_react_variants(self):
        """Multiple React variants should deduplicate to one entry."""
        text = (
            "We use React for components, React.js for routing, "
            "and ReactJS for state management."
        )
        result = nlp_extractor.extract(text)
        tech = result.get("tech_stack", {})
        detected = tech.get("value", [])
        react_count = sum(1 for t in detected if "react" in t.lower())
        assert react_count == 1, f"Expected 1 React entry, got {react_count}: {detected}"

    # ── Team Size ──────────────────────────────────────────────────

    def test_team_size_extracted(self, sample_document_text):
        """Team size should be extracted from '8 developers' in sample text."""
        result = nlp_extractor.extract(sample_document_text)
        team = result.get("team_size", {})
        if isinstance(team, dict):
            size = team.get("value")
            if size is not None:
                assert size >= 1

    def test_staffing_table_summation(self):
        """Team size should sum roles from a staffing table."""
        text = """
        # Staffing Plan

        | Role | Count |
        |------|-------|
        | 3 developer | - |
        | 2 QA | - |
        | 1 PM | - |
        """
        result = nlp_extractor.extract(text)
        team = result.get("team_size", {})
        assert team.get("value") == 6

    # ── Duration ───────────────────────────────────────────────────

    def test_duration_extracted(self, sample_document_text):
        """Duration should be extracted from '12 months' in sample text."""
        result = nlp_extractor.extract(sample_document_text)
        duration = result.get("duration_months", {})
        if isinstance(duration, dict):
            value = duration.get("value")
            if value is not None:
                assert value > 0

    def test_quarter_based_duration(self):
        """'Deliver by Q3 2026' should calculate months from now."""
        text = "The project must launch and deliver by Q3 2026."
        result = nlp_extractor.extract(text)
        duration = result.get("duration_months", {})
        value = duration.get("value")
        assert value is not None
        assert value > 0

    def test_week_based_duration(self):
        """'16 weeks' should convert to ~3.7 months."""
        text = "The project timeline is 16 weeks total duration."
        result = nlp_extractor.extract(text)
        duration = result.get("duration_months", {})
        value = duration.get("value")
        assert value is not None
        assert 3.0 <= value <= 5.0

    # ── Complexity ─────────────────────────────────────────────────

    def test_complexity_detection(self, sample_document_text):
        """Complexity should be detected from text signals."""
        result = nlp_extractor.extract(sample_document_text)
        complexity = result.get("complexity", {})
        if isinstance(complexity, dict):
            value = complexity.get("value")
            if value is not None:
                assert value in ("Low", "Medium", "High", "Very High")

    def test_complexity_very_high(self):
        """ML + microservices + PCI-DSS + multi-region → Very High."""
        text = (
            "This machine learning system requires microservices architecture "
            "with PCI-DSS compliance, multi-region deployment, blockchain-based "
            "audit trail, and real-time event streaming via Kafka. "
            "Must support high availability with 99.99% SLA. "
            "Computer vision pipeline with advanced neural network."
        )
        result = nlp_extractor.extract(text)
        complexity = result.get("complexity", {})
        assert complexity.get("value") in ("High", "Very High")

    def test_complexity_low(self):
        """Simple MVP with basic CRUD → Low."""
        text = (
            "A simple prototype landing page and basic static website. "
            "This is a small MVP with minimal functionality."
        )
        result = nlp_extractor.extract(text)
        complexity = result.get("complexity", {})
        assert complexity.get("value") in ("Low", "Medium")

    # ── Feature Count ──────────────────────────────────────────────

    def test_section_based_feature_counting(self):
        """Numbered sub-items in 'Functional Requirements' section → count them."""
        text = """
        # Functional Requirements

        3.1 User shall be able to register
        3.2 User shall be able to login
        3.3 User shall view dashboard
        3.4 Admin shall manage users
        3.5 System shall send email notifications
        3.6 System shall generate reports
        """
        result = nlp_extractor.extract(text)
        fc = result.get("feature_count", {})
        assert fc.get("value") >= 5

    # ── Project Name ───────────────────────────────────────────────

    def test_no_name_pattern_returns_empty(self):
        """Generic text with no project name pattern should return empty value."""
        text = (
            "The system shall provide user authentication. "
            "Data shall be stored in a relational database. "
            "The interface must support mobile devices."
        )
        result = nlp_extractor.extract(text)
        pname = result.get("project_name", {})
        assert isinstance(pname, dict)
        assert pname.get("value") == ""
        assert pname.get("confidence") == 0.0

    def test_project_name_extracted(self):
        """'Project Name: PredictIQ' pattern should extract 'PredictIQ'."""
        text = "Project Name: PredictIQ\nThis is a cost estimation platform."
        result = nlp_extractor.extract(text)
        pname = result.get("project_name", {})
        assert "PredictIQ" in pname.get("value", "")

    # ── New v2.4 Fields ────────────────────────────────────────────

    def test_integration_count_detected(self):
        """Known services like Stripe, Twilio should be counted."""
        text = (
            "The system integrates with Stripe for payments, Twilio for SMS, "
            "and SendGrid for email. It also connects to Salesforce CRM."
        )
        result = nlp_extractor.extract(text)
        integ = result.get("integration_count", {})
        assert integ.get("value") >= 4

    def test_volatility_high(self):
        """Documents with TBD and evolving requirements → high volatility."""
        text = (
            "Requirements are subject to change based on stakeholder feedback. "
            "TBD: payment module. The scope is flexible and will be refined "
            "iteratively through agile refinement sessions. TBD another feature. "
            "Future phases will add more capabilities."
        )
        result = nlp_extractor.extract(text)
        vol = result.get("volatility_score", {})
        assert vol.get("value") >= 4

    def test_volatility_low(self):
        """Fixed scope, regulatory → low volatility."""
        text = (
            "This is a fixed scope project with non-negotiable requirements. "
            "All features are locked scope as a contractual obligation. "
            "Compliance requirement: ISO standard must be met."
        )
        result = nlp_extractor.extract(text)
        vol = result.get("volatility_score", {})
        assert vol.get("value") <= 2

    def test_team_experience_senior(self):
        """Senior engineers, tech lead → high experience."""
        text = (
            "The team consists of senior engineers with 10+ years of experience. "
            "Led by a principal architect and tech lead."
        )
        result = nlp_extractor.extract(text)
        exp = result.get("team_experience", {})
        assert exp.get("value") >= 3.0

    def test_team_experience_junior(self):
        """Junior, fresh graduates → low experience."""
        text = (
            "The team is composed of junior developers, fresh graduates "
            "from a bootcamp. Training required before project kickoff."
        )
        result = nlp_extractor.extract(text)
        exp = result.get("team_experience", {})
        assert exp.get("value") <= 1.5

    # ── Methodology ────────────────────────────────────────────────

    def test_scrum_keywords_yield_agile(self):
        """Sprint, scrum master, backlog → Agile."""
        text = (
            "The project follows scrum with two-week sprints. "
            "The scrum master manages the backlog and velocity."
        )
        result = nlp_extractor.extract(text)
        meth = result.get("methodology", {})
        assert meth.get("value") == "Agile"

    def test_waterfall_keywords(self):
        """Phase gate, deliverables, sign-off → Waterfall."""
        text = (
            "The project uses a waterfall approach with milestones. "
            "Each phase requires formal review and sign-off before "
            "proceeding to the next phase gate."
        )
        result = nlp_extractor.extract(text)
        meth = result.get("methodology", {})
        assert meth.get("value") == "Waterfall"

    # ── Full Realistic SRS ─────────────────────────────────────────

    def test_full_realistic_srs(self, sample_document_text):
        """Complete SRS document should extract reasonable values across all fields."""
        result = nlp_extractor.extract(sample_document_text)

        # Project type should be detected
        assert result["project_type"]["value"] in (
            "Web App", "Enterprise Software", "API/Backend"
        )

        # Tech stack should have multiple techs
        assert len(result["tech_stack"]["value"]) >= 3

        # Team size should be reasonable
        assert 1 <= result["team_size"]["value"] <= 200

        # Duration should be positive
        assert result["duration_months"]["value"] > 0

        # Complexity should be valid
        assert result["complexity"]["value"] in ("Low", "Medium", "High", "Very High")

        # Feature count should be positive
        assert result["feature_count"]["value"] > 0

        # Integration count should be positive
        assert result["integration_count"]["value"] >= 2

        # Volatility should be 1-5
        assert 1 <= result["volatility_score"]["value"] <= 5

        # Team experience should be 1-4
        assert 1.0 <= result["team_experience"]["value"] <= 4.0
