"""Pydantic schemas for Bulk Project Import and Calibration (Checkpoint S06)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class BulkProjectItem(BaseModel):
    """Single historical project record for bulk import."""

    project_name: str = Field(..., min_length=1, max_length=255, description="Project or system name")
    size_fp: float = Field(..., gt=0.0, description="Functional size in IFPUG Function Points (FP)")
    actual_hours: float = Field(..., gt=0.0, description="Actual delivered effort in person-hours")
    platform: str | None = Field(None, max_length=100)
    tech_stack: str | None = Field(None, max_length=200)
    dev_type: str | None = Field(None, max_length=100)
    completed_at: str | None = Field(None, max_length=50)
    notes: str | None = Field(None, max_length=2000)


class BulkImportRequest(BaseModel):
    """Request payload containing a list of project items for bulk import."""

    projects: list[BulkProjectItem] = Field(..., min_length=1, description="List of completed projects")


class BulkImportRowError(BaseModel):
    """Validation error encountered in a specific row or item."""

    row_index: int
    project_name: str | None = None
    reason: str


class CalibrationPreviewSummary(BaseModel):
    """Empirical Bayes calibration preview result."""

    k_projects: int
    shrinkage_weight: float
    global_a: float
    calibrated_a: float
    exponent_b: float
    scaling_ratio: float
    mdape_before: float
    mdape_after: float
    relative_gain_pct: float
    pred25_before: float
    pred25_after: float


class BulkImportResponse(BaseModel):
    """Response returned upon completing a bulk import."""

    total_submitted: int
    valid_count: int
    error_count: int
    errors: list[BulkImportRowError] = Field(default_factory=list)
    calibration_preview: CalibrationPreviewSummary
