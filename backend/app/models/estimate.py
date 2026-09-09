"""
Predictify Pydantic Models — Estimate
Request/response schemas for estimation endpoints.
"""
from typing import Annotated, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints, field_validator

ProjectName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
ProjectType = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Technology = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
TechStack = Annotated[list[Technology], Field(max_length=50)]


class EstimateOverrides(BaseModel):
    """User-corrected parameters from Step 2 of the wizard."""
    project_type: Optional[ProjectType] = None
    team_size: Optional[int] = Field(None, ge=1, le=100)
    duration_months: Optional[float] = Field(None, ge=1, le=60)
    complexity: Optional[Literal["Low", "Medium", "High", "Very High"]] = None
    methodology: Optional[Literal["Agile", "Waterfall", "Hybrid"]] = None
    hourly_rate_usd: Optional[float] = Field(None, ge=10, le=500)
    tech_stack: Optional[TechStack] = None
    project_name: Optional[ProjectName] = None
    integration_count: Optional[int] = Field(None, ge=0, le=15)
    volatility_score: Optional[int] = Field(None, ge=1, le=5)
    team_experience: Optional[float] = Field(None, ge=1, le=4)


class EstimateRequest(BaseModel):
    """Request body for POST /api/v1/estimates/analyze."""
    document_id: UUID
    overrides: Optional[EstimateOverrides] = None


class ManualEstimateRequest(BaseModel):
    """Request body for manual estimate without document upload."""
    project_name: ProjectName
    project_type: ProjectType = "Web App"
    team_size: int = Field(5, ge=1, le=100)
    duration_months: float = Field(6, ge=1, le=60)
    complexity: Literal["Low", "Medium", "High", "Very High"] = "Medium"
    methodology: Literal["Agile", "Waterfall", "Hybrid"] = "Agile"
    hourly_rate_usd: float = Field(75.0, ge=10, le=500)
    tech_stack: TechStack = Field(default_factory=list)
    integration_count: int = Field(2, ge=0, le=15)
    volatility_score: int = Field(3, ge=1, le=5)
    team_experience: float = Field(2.0, ge=1, le=4)


class PhaseBreakdown(BaseModel):
    """Cost/effort breakdown for a single project phase."""
    phase: str
    effort_hours: float
    cost_usd: float
    duration_weeks: float
    pct_of_total: float


class RiskItem(BaseModel):
    """Individual risk factor."""
    name: str
    description: str
    severity: Literal["Low", "Medium", "High", "Critical"]


class EstimateOutputs(BaseModel):
    """ML prediction outputs."""
    effort_min_hours: float
    effort_likely_hours: float
    effort_max_hours: float
    cost_min_usd: float
    cost_likely_usd: float
    cost_max_usd: float
    timeline_min_weeks: float
    timeline_likely_weeks: float
    timeline_max_weeks: float
    confidence_pct: float
    risk_score: float
    risk_level: Literal["Low", "Medium", "High", "Critical"]
    top_risks: list[RiskItem]
    phase_breakdown: list[PhaseBreakdown]
    model_explanation: str = ""
    benchmark_comparison: str = ""


class EstimateInputs(BaseModel):
    """Captured input parameters for an estimate."""
    project_type: str
    tech_stack: list[str]
    team_size: int
    duration_months: float
    complexity: str
    methodology: str
    hourly_rate_usd: float
    # Older estimates did not persist these values. None means unknown, not a
    # retrospectively assumed default that could misrepresent their prediction.
    feature_count: Optional[int] = None
    integration_count: Optional[int] = None
    volatility_score: Optional[int] = None
    team_experience: Optional[float] = None
    size_fp: Optional[float] = None


class EstimateResult(BaseModel):
    """Full estimate result returned to the frontend."""
    estimate_id: str
    document_id: Optional[str] = None
    user_id: str
    project_name: str
    created_at: str
    version: int = 1
    status: str = "complete"
    inputs: EstimateInputs
    outputs: EstimateOutputs
    model_version: str = "2.0.0"


class EstimateSummary(BaseModel):
    """Summary of an estimate for list views."""
    id: str
    project_name: str
    project_type: str
    cost_likely_usd: float
    cost_min_usd: float
    cost_max_usd: float
    risk_score: float
    risk_level: str
    confidence_pct: float
    duration_likely_weeks: float
    status: str
    version: int
    created_at: str
    updated_at: Optional[str] = None


class EstimateListResponse(BaseModel):
    """Paginated list of estimate summaries."""
    estimates: list[EstimateSummary]
    total: int
    page: int
    per_page: int


class ShareLinkRequest(BaseModel):
    """Request to generate a share link."""
    expires_in_days: int = Field(7, ge=1, le=365)
    password: Optional[str] = Field(None, max_length=72)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value):
        if value is not None and len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 UTF-8 bytes")
        return value


class ShareLinkResponse(BaseModel):
    """Generated share link response."""
    share_url: str
    token: str
    expires_at: str
