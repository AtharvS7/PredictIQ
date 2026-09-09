"""
Predictify — Pytest Configuration and Shared Fixtures
Provides reusable test data for all test modules.
"""
import os
import sys

import pytest

# Ensure backend/ is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Tests must never inherit usable cloud credentials from a developer's .env.
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "postgresql://test:test@127.0.0.1:1/predictiq_test"
os.environ["FIREBASE_CREDENTIALS_JSON"] = ""
os.environ["FIREBASE_CREDENTIALS_PATH"] = "./missing-test-service-account.json"
os.environ["STORAGE_BACKEND"] = "local"
os.environ["S3_ACCESS_KEY_ID"] = ""
os.environ["S3_SECRET_ACCESS_KEY"] = ""


@pytest.fixture
def contract_model_artifacts(tmp_path, monkeypatch):
    """Real serialized sklearn bundle for API contracts, NOT an accuracy fixture.

    The distributed model is revoked; numerical correctness is tested separately.
    This constant model keeps persistence/export tests independent of bad labels.
    """
    import json
    import pickle

    import numpy as np
    import pandas as pd
    from app.core.config import settings
    from ml.inference import EXPECTED_FEATURES, predictor
    from sklearn.dummy import DummyRegressor
    from sklearn.preprocessing import StandardScaler

    frame = pd.DataFrame(np.ones((4, 27)), columns=EXPECTED_FEATURES)
    scaler = StandardScaler().fit(frame)
    model = DummyRegressor().fit(scaler.transform(frame), np.full(4, np.log1p(1000)))
    model_path, scaler_path, features_path = [tmp_path / name for name in ("model.pkl", "scaler.pkl", "features.json")]
    model_path.write_bytes(pickle.dumps(model))
    scaler_path.write_bytes(pickle.dumps(scaler))
    features_path.write_text(json.dumps(EXPECTED_FEATURES))
    for key, value in (("ML_MODEL_PATH", model_path), ("ML_SCALER_PATH", scaler_path), ("ML_FEATURES_PATH", features_path)):
        monkeypatch.setattr(settings, key, str(value))
    previous = predictor.__dict__.copy()
    yield model_path, scaler_path, features_path
    predictor.__dict__.clear()
    predictor.__dict__.update(previous)


@pytest.fixture
def sample_project_params() -> dict:
    """Realistic project parameters for a mid-size web application."""
    return {
        "project_type": "Web App",
        "team_size": 6,
        "duration_months": 8.0,
        "complexity": "Medium",
        "methodology": "Agile",
        "hourly_rate_usd": 75.0,
        "tech_stack": ["React", "FastAPI", "PostgreSQL", "Docker"],
        "size_fp": 250.0,
        "feature_count": 15,
    }


@pytest.fixture
def sample_feature_vector() -> dict:
    """A complete 27-feature vector matching Predictify_features.json."""
    return {
        "TeamExp": 3.0,
        "ManagerExp": 3.5,
        "duration_months": 8.0,
        "Transactions": 212.5,
        "Entities": 75.0,
        "PointsNonAdjust": 260.42,
        "Adjustment": 0.96,
        "size_fp": 250.0,
        "T01": 2.25,
        "T02": 2.0,
        "T03": 2.125,
        "T04": 4.0,
        "T05": 4.0,
        "T06": 3.0,
        "T07": 2.5,
        "T08": 2.0,
        "T09": 2.5,
        "T10": 2.25,
        "T11": 2.125,
        "T12": 3.0,
        "T13": 2.4,
        "T14": 3.0,
        "T15": 2.7,
        "log_size_fp": 5.525,
        "complexity_score": 2.29,
        "team_skill_avg": 2.775,
        "risk_score": 2.25,
    }


@pytest.fixture
def sample_document_text() -> str:
    """Realistic SRS document snippet for NLP extraction tests."""
    return """
    Project: Customer Relationship Management System (CRM Pro)
    Client: Acme Corporation
    Duration: 12 months
    Team: 8 developers, 2 QA, 1 PM

    1. Project Overview
    This project aims to build a web application for managing customer
    relationships, sales pipelines, and support tickets. The system will
    use React for the frontend, Node.js with Express for the backend,
    and PostgreSQL as the primary database. Redis will be used for caching.

    2. Core Features
    - User authentication and role-based access control
    - Contact management with search and filtering
    - Sales pipeline visualization with drag-and-drop
    - Email integration with Gmail and Outlook
    - Reporting dashboard with charts and exports
    - Mobile-responsive design
    - REST API for third-party integrations
    - Real-time notifications using WebSockets
    - Document upload and storage
    - Audit trail and activity logging
    - Automated email campaigns
    - Customer segmentation engine
    - Support ticket management
    - Knowledge base with search
    - Analytics and KPI tracking

    3. Technical Requirements
    - High complexity due to real-time features and integrations
    - Must support 10,000+ concurrent users
    - 99.9% uptime SLA required
    - GDPR compliance mandatory
    """


@pytest.fixture
def high_risk_params() -> dict:
    """Parameters that should trigger high risk scores."""
    return {
        "project_type": "ML/AI System",
        "team_size": 2,
        "duration_months": 2.0,
        "complexity": "Very High",
        "methodology": "Agile",
        "hourly_rate_usd": 150.0,
        "tech_stack": ["PyTorch", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "Redis", "Kafka"],
        "size_fp": 500.0,
        "feature_count": 30,
    }


@pytest.fixture
def low_risk_params() -> dict:
    """Parameters that should produce low risk scores."""
    return {
        "project_type": "Web App",
        "team_size": 5,
        "duration_months": 9.0,
        "complexity": "Low",
        "methodology": "Agile",
        "hourly_rate_usd": 75.0,
        "tech_stack": ["React", "Node.js"],
        "size_fp": 100.0,
        "feature_count": 8,
    }
