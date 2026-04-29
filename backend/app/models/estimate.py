"""
Predictify Pydantic Models — Estimate
Request/response schemas for estimation endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID


class EstimateOverrides(BaseModel):
    """User-corrected parameters from Step 2 of the wizard."""
    project_type: Optional[str] = None
    team_size: Optional[int] = Field(None, ge=1, le=100)
    duration_months: Optional[float] = Field(None, ge=1, le=60)
    complexity: Optional[Literal["Low", "Medium", "High", "Very High"]] = None
    methodology: Optional[Literal["Agile", "Waterfall", "Hybrid"]] = None
    hourly_rate_usd: Optional[float] = Field(None, ge=10, le=500)
    tech_stack: Optional[list[str]] = None
    project_name: Optional[str] = None


class EstimateRequest(BaseModel):
    """Request body for POST /api/v1/estimates/analyze."""
    document_id: UUID
    overrides: Optional[EstimateOverrides] = None


class ManualEstimateRequest(BaseModel):
    """Request body for manual estimate without document upload."""
    project_name: str = Field(..., min_length=1, max_length=200)
    project_type: str = "Web App"
    team_size: int = Field(5, ge=1, le=100)
    duration_months: float = Field(6, ge=1, le=60)
    complexity: Literal["Low", "Medium", "High", "Very High"] = "Medium"
    methodology: Literal["Agile", "Waterfall", "Hybrid"] = "Agile"
    hourly_rate_usd: float = Field(75.0, ge=10, le=500)
    tech_stack: list[str] = Field(default_factory=list)


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
    password: Optional[str] = None


class ShareLinkResponse(BaseModel):
    """Generated share link response."""
    share_url: str
    token: str
    expires_at: str
