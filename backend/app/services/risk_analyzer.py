"""
Predictify Risk Analyzer Service
Computes risk scores and identifies top risk factors.
"""
from app.models.estimate import RiskItem


RISK_FACTORS = [
    {
        "name": "Scope Ambiguity",
        "check": lambda p: p.get("feature_count", 0) < 5 or p.get("complexity") == "Very High",
        "description": "Insufficient scope definition or extremely high complexity increases risk of scope creep.",
        "weight": 15,
    },
    {
        "name": "Technology Complexity",
        "check": lambda p: len(p.get("tech_stack", [])) > 6 or p.get("complexity") in ("High", "Very High"),
        "description": "Large or complex technology stack increases integration risk and learning curve.",
        "weight": 12,
    },
    {
        "name": "Team Experience Gap",
        "check": lambda p: p.get("team_size", 5) < 3 and p.get("complexity") in ("High", "Very High"),
        "description": "Small team handling high-complexity project may lack required expertise coverage.",
        "weight": 14,
    },
    {
        "name": "Timeline Constraint",
        "check": lambda p: p.get("duration_months", 6) < 3 and p.get("complexity") != "Low",
        "description": "Short timeline for non-trivial project increases schedule pressure and technical debt risk.",
        "weight": 13,
    },
    {
        "name": "Requirement Volatility",
        "check": lambda p: p.get("methodology") == "Agile" and p.get("complexity") in ("High", "Very High"),
        "description": "Agile methodology with high complexity suggests evolving requirements that may impact cost.",
        "weight": 10,
    },
    {
        "name": "Integration Risk",
        "check": lambda p: len(p.get("tech_stack", [])) > 4,
        "description": "Multiple technology integrations increase the risk of compatibility issues.",
        "weight": 8,
    },
    {
        "name": "Resource Availability",
        "check": lambda p: p.get("team_size", 5) > 15,
        "description": "Large team coordination increases communication overhead and risk.",
        "weight": 7,
    },
    {
        "name": "Technical Debt Accumulation",
        "check": lambda p: p.get("duration_months", 6) > 18,
        "description": "Long project durations tend to accumulate technical debt requiring additional effort.",
        "weight": 6,
    },
    {
        "name": "Quality Assurance Gap",
        "check": lambda p: p.get("duration_months", 6) < 4 and p.get("team_size", 5) < 4,
        "description": "Small team with short timeline may compromise testing quality.",
        "weight": 9,
    },
    {
        "name": "Deployment Complexity",
        "check": lambda p: any(t.lower() in ("kubernetes", "k8s", "microservices", "docker")
                               for t in p.get("tech_stack", [])),
        "description": "Complex deployment infrastructure adds operational risk.",
        "weight": 5,
    },
]


def analyze_risk(params: dict) -> dict:
    """
    Analyze project risk based on input parameters.

    Args:
        params: Project parameters including team_size, complexity,
                duration_months, tech_stack, methodology, feature_count.

    Returns:
        Dictionary with risk_score (0-100), risk_level, and top_risks.
    """
    triggered_risks = []
    total_risk_weight = 0

    for factor in RISK_FACTORS:
        try:
            if factor["check"](params):
                severity = _weight_to_severity(factor["weight"])
                triggered_risks.append(
                    RiskItem(
                        name=factor["name"],
                        description=factor["description"],
                        severity=severity,
                    )
                )
                total_risk_weight += factor["weight"]
        except Exception:
            continue

    # Calculate base risk score (0-100)
    max_possible_weight = sum(f["weight"] for f in RISK_FACTORS)
    risk_score = min(100, (total_risk_weight / max_possible_weight) * 100)

    # Add complexity-based risk boost
    complexity_boost = {
        "Low": 0,
        "Medium": 5,
        "High": 15,
        "Very High": 25,
    }.get(params.get("complexity", "Medium"), 5)

    risk_score = min(100, risk_score + complexity_boost)

    # Determine risk level
    risk_level = _score_to_level(risk_score)

    # Sort risks by severity and take top 5
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    triggered_risks.sort(key=lambda r: severity_order.get(r.severity, 4))
    top_risks = triggered_risks[:5]

    # If no risks triggered, add a baseline low risk
    if not top_risks:
        top_risks = [
            RiskItem(
                name="Standard Project Risk",
                description="All projects carry inherent risk. This project has no major identified risk factors.",
                severity="Low",
            )
        ]

    return {
        "risk_score": round(risk_score, 1),
        "risk_level": risk_level,
        "top_risks": top_risks,
    }


def _weight_to_severity(weight: int) -> str:
    """Convert risk weight to severity level."""
    if weight >= 14:
        return "Critical"
    elif weight >= 10:
        return "High"
    elif weight >= 7:
        return "Medium"
    else:
        return "Low"


def _score_to_level(score: float) -> str:
    """Convert risk score to risk level string."""
    if score >= 70:
        return "Critical"
    elif score >= 45:
        return "High"
    elif score >= 25:
        return "Medium"
    else:
        return "Low"
