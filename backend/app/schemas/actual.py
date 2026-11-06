"""
Pydantic schemas for project actuals (Actuals Flywheel — CP06).
"""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ActualCreate(BaseModel):
    """Payload for submitting actual delivered project metrics."""

    model_config = ConfigDict(extra="forbid")

    actual_effort_hours: float = Field(
        ...,
        gt=0,
        le=1_000_000,
        description="Delivered effort in person-hours. Must be strictly positive.",
    )
    actual_cost_usd: float | None = Field(
        None,
        ge=0,
        le=100_000_000,
        description="Delivered project cost in USD.",
    )
    actual_duration_months: float | None = Field(
        None,
        ge=0,
        le=240,
        description="Delivered calendar duration in months.",
    )
    team_size: int | None = Field(
        None,
        ge=1,
        le=1000,
        description="Delivered core team size.",
    )
    functional_size_delivered: float | None = Field(
        None,
        ge=0,
        le=100_000,
        description="Delivered functional size (e.g. Function Points).",
    )
    notes: str | None = Field(
        None,
        max_length=5000,
        description="Delivery notes or retrospective insights.",
    )
    consent_for_training: bool = Field(
        False,
        description="Explicit user consent to include anonymized data in model retraining.",
    )


class ActualResponse(BaseModel):
    """Response model for recorded project actuals."""

    id: UUID
    estimate_id: UUID
    actual_effort_hours: float
    actual_cost_usd: float | None = None
    actual_duration_months: float | None = None
    team_size: int | None = None
    functional_size_delivered: float | None = None
    notes: str | None = None
    consent_for_training: bool
    created_at: datetime
    created_by_user_id: str


class ProjectsV2ExportItem(BaseModel):
    """Format compatible with projects_v2 dataset for consented actuals."""

    project_id: str
    source: str = "actuals_flywheel"
    year: int | None = None
    size_value: float | None = None
    size_unit: str | None = None
    effort_hours: float
    duration_months: float | None = None
    team_size: int | None = None
    platform: str | None = None
    language: str | None = None
    dev_type: str | None = None
    notes: str | None = None
