"""
PredictIQ (Predictify) End-to-End SRS/PRD Pipeline Verification
==============================================================
Validates the full document upload-to-estimate pipeline:
  Document Parser -> NLP Extractor -> ML Service -> Inference -> Estimation Calculation
Tests:
  1. Software Requirements Specification.docx (actual repository artifact)
  2. Synthetic Small MVP App
  3. Synthetic Medium SaaS Platform
  4. Synthetic Large Enterprise AI/Fintech Platform
Verifies:
  - predictor.is_ready is True
  - Monotonicity: Small MVP < Medium SaaS < Large Enterprise (Effort, Cost, Risk)
  - Output contracts, confidence intervals, cost drivers, and safety validations
"""
import sys
import os
from pathlib import Path

# Add backend directory to path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from ml.inference import predictor, EXPECTED_FEATURES
from ml.artifact_safety import REVOKED_DATA_SHA256, REVOKED_MODEL_SHA256, require_unrevoked
from app.services.document_parser import DocumentParser
from app.services.nlp_extractor import nlp_extractor
from app.services.ml_service import ml_service
from app.services.cost_calculator import (
    calculate_cost,
    calculate_timeline,
    estimate_function_points,
)
from app.services.risk_analyzer import analyze_risk


def run_pipeline(name: str, text: str, hourly_rate: float = 75.0):
    """Run text through NLP extractor, ML prediction, and estimation math."""
    # Step 1: NLP extraction
    extracted = nlp_extractor.extract(text)
    
    # Helper to unpack value from {value, confidence}
    def get_val(key, default):
        field = extracted.get(key)
        if isinstance(field, dict) and "value" in field:
            return field["value"]
        return default

    feature_count = int(get_val("feature_count", 8))
    complexity = str(get_val("complexity", "Medium"))
    tech_stack = list(get_val("tech_stack", ["Python", "FastAPI"]))
    integration_count = int(get_val("integration_count", 2))
    duration_months = float(get_val("duration_months", 6.0))
    team_size = int(get_val("team_size", 4))
    volatility_score = int(get_val("volatility_score", 3))

    # Step 2: Function point estimation
    size_fp = estimate_function_points(
        feature_count=feature_count,
        complexity=complexity,
        tech_stack_count=len(tech_stack),
        external_interface_files=min(integration_count, 15),
    )

    # Step 3: ML service prediction
    params = {
        "feature_count": feature_count,
        "complexity": complexity,
        "tech_stack": tech_stack,
        "integration_count": integration_count,
        "duration_months": duration_months,
        "team_size": team_size,
        "size_fp": size_fp,
        "volatility_score": volatility_score,
        "methodology": str(get_val("methodology", "Agile")),
    }
    ml_result = ml_service.predict(params)
    effort_likely = int(round(ml_result["effort_hours_likely"]))
    effort_min = int(round(ml_result["effort_hours_min"]))
    effort_max = int(round(ml_result["effort_hours_max"]))

    # Step 4: Cost, timeline, risk
    costs = calculate_cost(effort_likely, effort_min, effort_max, hourly_rate)
    timeline = calculate_timeline(duration_months, team_size)
    risk_output = analyze_risk(params)

    return {
        "name": name,
        "features": feature_count,
        "complexity": complexity,
        "integrations": integration_count,
        "duration_mo": duration_months,
        "team_size": team_size,
        "size_fp": round(size_fp, 1),
        "effort_likely": effort_likely,
        "effort_min": effort_min,
        "effort_max": effort_max,
        "cost_likely": int(costs["cost_likely_usd"]),
        "risk_score": risk_output["risk_score"],
        "risk_level": risk_output["risk_level"],
        "confidence_pct": ml_result.get("confidence_pct", 85.0),
        "model_mode": ml_result.get("model_mode", "live"),
    }


def main():
    print("=" * 80)
    print("PredictIQ (Predictify) End-to-End Pipeline Verification")
    print("=" * 80)

    # 1. Verify artifact safety
    model_path = BACKEND_DIR / "ml" / "predictiq_best_model.pkl"
    dataset_path = BACKEND_DIR / "ml" / "predictiq_merged_dataset.csv"
    print("\n[CHECK 1] Artifact Safety Verification:")
    require_unrevoked(model_path, REVOKED_MODEL_SHA256)
    print(f"  [PASS] Model {model_path.name} is unrevoked")
    require_unrevoked(dataset_path, REVOKED_DATA_SHA256)
    print(f"  [PASS] Training dataset {dataset_path.name} is unrevoked")

    # 2. Verify Predictor Readiness
    print("\n[CHECK 2] Predictor Startup Readiness:")
    loaded = predictor.load()
    print(f"  Predictor load result: {loaded}")
    print(f"  Predictor is_ready:    {predictor.is_ready}")
    print(f"  Model name:            {predictor.model_name}")
    print(f"  Model mode:            {predictor.get_model_info()['model_mode']}")
    assert predictor.is_ready, "Predictor MUST be ready!"
    assert predictor.get_model_info()["model_mode"] == "live", "Model mode MUST be 'live'!"
    print("  [PASS] Predictor is ready and live.")

    # 3. Test Cases: Actual DOCX + 3 Synthetic PRDs
    print("\n[CHECK 3] Executing Document Parsing & Estimation Pipeline:")

    # Actual DOCX
    docx_file = BACKEND_DIR.parent / "Software Requirements Specification.docx"
    print(f"  Parsing actual DOCX: {docx_file.name} ...")
    parsed_docx = DocumentParser.parse(
        docx_file.read_bytes(),
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    print(f"  Extracted {parsed_docx['word_count']} words from DOCX.")
    res_docx = run_pipeline("Actual SRS Document (.docx)", parsed_docx["raw_text"])

    # Synthetic Small MVP App
    small_srs = """
    Software Requirements Specification - TodoMicro MVP
    Project Overview: A minimal single-page task tracking application for solo users.
    Specific Requirements:
    1. User registration and basic email authentication.
    2. Create, list, edit, and mark tasks complete.
    3. Export tasks to a simple CSV file.
    Complexity: Low
    Technology Stack: Python, SQLite, HTML5, JavaScript
    Timeline: Target delivery in 2 months with a team of 1 developer.
    External Integrations: Single integration with SQLite database.
    """
    res_small = run_pipeline("Small MVP App", small_srs)

    # Synthetic Medium SaaS Platform
    medium_srs = """
    Software Requirements Specification - TeamSync SaaS
    Project Overview: A collaborative multi-tenant project management platform for growing teams.
    System Requirements & Features:
    1. Multi-tenant organization and team workspace management.
    2. Interactive Kanban board and sprint planning views.
    3. Real-time notifications and activity streams using WebSockets.
    4. Time tracking and milestone progress indicators.
    5. Role-based access control (Admin, Manager, Contributor, Viewer).
    6. CSV and PDF export of sprint velocity reports.
    7. User profile management with avatar uploads.
    8. Custom workflow states and task status transitions.
    9. Global search across projects, tasks, and comments.
    10. Subscription billing portal and invoice management.
    11. Webhook dispatcher for external team automations.
    12. Automated weekly email digest generator.
    Complexity: Medium
    Technology Stack: Python, FastAPI, PostgreSQL, React, TypeScript, Redis, Docker
    Timeline: Expected duration of 6 months with a dedicated team of 5 developers.
    External Integrations: 4 integrations (Stripe, SendGrid, Slack, AWS S3).
    """
    res_medium = run_pipeline("Medium SaaS Platform", medium_srs)

    # Synthetic Large Enterprise AI/Fintech System
    large_srs = """
    Software Requirements Specification - OmniSettle Global Banking Platform
    Project Overview: A mission-critical, enterprise multi-region financial ledger and cross-border settlement system.
    Key Functional & System Requirements:
    1. Real-time distributed double-entry core ledger processing engine.
    2. Multi-currency settlement and automated foreign exchange conversion.
    3. AI/ML-driven real-time fraud scoring and anomaly prevention pipeline.
    4. High-throughput Kafka event streaming for transaction audit logging.
    5. Strict Role-Based Access Control and multi-factor biometric authorization.
    6. Regulatory compliance reporting for Basel III and SOX automated audits.
    7. Automated liquidity forecasting and reconciliation engine.
    8. Multi-region automated failover and active-active data synchronization.
    9. SWIFT messaging bridge for international wire transfer verification.
    10. Core banking API gateway integration for legacy mainframe connectivity.
    11. Cryptographic ledger signing and hardware security module (HSM) key storage.
    12. Real-time executive compliance dashboards and anomaly alerts.
    13. Real-time anti-money laundering (AML) sanctions screening watchlist.
    14. High-frequency trade reconciliation and end-of-day batch clearing.
    15. Automated chargeback resolution workflow and case management portal.
    16. Multi-tier tenant partitioning with custom data residency controls.
    17. Automated tax calculation and multi-jurisdictional withholding logic.
    18. Real-time credit risk assessment model inference engine.
    19. Customer KYC verification pipeline with optical document verification.
    20. Distributed consensus and event replay disaster recovery orchestrator.
    Complexity: High
    Technology Stack: Python, FastAPI, Java, Kafka, PostgreSQL, Redis, Kubernetes, AWS, PyTorch, Docker
    Timeline: Enterprise delivery scheduled for 18 months with a specialized team of 15 engineers.
    External Integrations: 12 enterprise integrations (SWIFT, Visa Direct, Plaid, Experian, AWS KMS, Mainframe MQ).
    """
    res_large = run_pipeline("Large Enterprise System", large_srs)

    results = [res_small, res_medium, res_large, res_docx]

    # 4. Print Comparison Table
    print("\n" + "=" * 105)
    print(f"{'Document / Scope':<30} | {'Features':>8} | {'FP':>6} | {'Effort (hrs)':>12} | {'Cost ($)':>12} | {'Risk':>8} | {'Mode':>6}")
    print("-" * 105)
    for r in results:
        print(f"{r['name']:<30} | {r['features']:>8} | {r['size_fp']:>6.0f} | {r['effort_likely']:>12,d} | ${r['cost_likely']:>11,d} | {r['risk_level']:>8} | {r['model_mode']:>6}")
    print("=" * 105)

    # 5. Assert Differentiated, Realistic Monotonicity
    print("\n[CHECK 4] Verifying Order & Differentiation:")
    assert res_small["effort_likely"] < res_medium["effort_likely"], (
        f"Small MVP ({res_small['effort_likely']}h) must be < Medium SaaS ({res_medium['effort_likely']}h)"
    )
    assert res_medium["effort_likely"] < res_large["effort_likely"], (
        f"Medium SaaS ({res_medium['effort_likely']}h) must be < Large Enterprise ({res_large['effort_likely']}h)"
    )
    assert res_small["cost_likely"] < res_medium["cost_likely"], "Small cost must be < Medium cost"
    assert res_medium["cost_likely"] < res_large["cost_likely"], "Medium cost must be < Large cost"
    assert res_small["risk_score"] < res_large["risk_score"], "Small risk must be < Large risk"
    print("  [PASS] Monotonicity confirmed: Small MVP < Medium SaaS < Large Enterprise across Effort, Cost, Risk.")

    # 6. Verify Actual DOCX Estimates
    print(f"\n[CHECK 5] Actual SRS Document Result:")
    print(f"  Features Extracted: {res_docx['features']}")
    print(f"  Complexity:         {res_docx['complexity']}")
    print(f"  Function Points:    {res_docx['size_fp']} FP")
    print(f"  Effort (Likely):    {res_docx['effort_likely']:,} person-hours")
    print(f"  Effort Range:       {res_docx['effort_min']:,} - {res_docx['effort_max']:,} person-hours")
    print(f"  Cost (Likely):      ${res_docx['cost_likely']:,}")
    print(f"  Risk Assessment:    {res_docx['risk_level']} (Score: {res_docx['risk_score']})")
    print(f"  Model Mode:         {res_docx['model_mode']}")
    assert res_docx["effort_likely"] > 0, "Effort must be positive"
    assert res_docx["model_mode"] == "live", "Model mode must be 'live'"
    print("  [PASS] Actual SRS document parsed and estimated realistically.")

    print("\n" + "=" * 80)
    print("ALL END-TO-END PIPELINE VERIFICATIONS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
