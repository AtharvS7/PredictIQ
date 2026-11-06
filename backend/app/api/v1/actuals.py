"""
Predictify API — Project Actuals Endpoints (Actuals Flywheel — CP06)
Manages delivery feedback, explicit training consent, and ML export.
"""
import csv
import html
import io
import json
import re
from typing import Literal
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.database import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.schemas.actual import (
    ActualCreate,
    ActualResponse,
    ProjectsV2ExportItem,
)

router = APIRouter()
logger = structlog.get_logger()


def _sanitize_notes(value: str | None, max_length: int = 5000) -> str | None:
    """Sanitize user-supplied delivery notes."""
    if not value:
        return None
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    cleaned = html.escape(cleaned.strip())
    return cleaned[:max_length] if cleaned else None


def _extract_inputs_metadata(inputs_data: dict | str | None) -> tuple[str | None, str | None, str | None]:
    """Extract (platform, language, dev_type) from estimate inputs_json."""
    if not inputs_data:
        return None, None, None
    if isinstance(inputs_data, str):
        try:
            inputs_data = json.loads(inputs_data)
        except Exception:
            return None, None, None
    if not isinstance(inputs_data, dict):
        return None, None, None

    dev_type = inputs_data.get("project_type")
    platform = inputs_data.get("platform") or dev_type

    tech_stack = inputs_data.get("tech_stack")
    if isinstance(tech_stack, list) and tech_stack:
        language = ", ".join(str(t) for t in tech_stack)
    elif isinstance(tech_stack, str) and tech_stack:
        language = tech_stack
    else:
        language = None

    return platform, language, dev_type


@router.post(
    "/estimates/{estimate_id}/actuals",
    response_model=ActualResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit project actuals for an estimate",
)
async def create_estimate_actual(
    estimate_id: UUID,
    body: ActualCreate,
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Submit delivered actuals for a completed project estimate.
    Verifies that the caller owns the estimate or possesses the admin role.
    Records explicit user consent for retraining use.
    """
    pool = await get_db()
    est = await pool.fetchrow(
        "SELECT id, user_id FROM estimates WHERE id = $1 AND status != 'deleted'",
        estimate_id,
    )
    if not est:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")

    if est["user_id"] != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to submit actuals for this estimate",
        )

    sanitized_notes = _sanitize_notes(body.notes)

    row = await pool.fetchrow(
        """
        INSERT INTO estimate_actuals (
            estimate_id,
            actual_effort_hours,
            actual_cost_usd,
            actual_duration_months,
            team_size,
            functional_size_delivered,
            notes,
            consent_for_training,
            created_by_user_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, estimate_id, actual_effort_hours, actual_cost_usd,
                  actual_duration_months, team_size, functional_size_delivered,
                  notes, consent_for_training, created_at, created_by_user_id
        """,
        estimate_id,
        body.actual_effort_hours,
        body.actual_cost_usd,
        body.actual_duration_months,
        body.team_size,
        body.functional_size_delivered,
        sanitized_notes,
        body.consent_for_training,
        user.id,
    )

    if not row:
        logger.error("estimate_actuals_insert_failed", estimate_id=str(estimate_id))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record project actuals",
        )

    logger.info(
        "estimate_actual_recorded",
        actual_id=str(row["id"]),
        estimate_id=str(estimate_id),
        consent=body.consent_for_training,
        user_id=user.id,
    )

    return ActualResponse.model_validate(dict(row))


@router.get(
    "/estimates/{estimate_id}/actuals",
    response_model=list[ActualResponse],
    summary="Retrieve recorded actuals for an estimate",
)
async def get_estimate_actuals(
    estimate_id: UUID,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Retrieve project actuals for an estimate.
    Verifies that the caller owns the estimate or is an admin.
    """
    pool = await get_db()
    est = await pool.fetchrow(
        "SELECT id, user_id FROM estimates WHERE id = $1 AND status != 'deleted'",
        estimate_id,
    )
    if not est:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")

    if est["user_id"] != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view actuals for this estimate",
        )

    rows = await pool.fetch(
        """
        SELECT id, estimate_id, actual_effort_hours, actual_cost_usd,
               actual_duration_months, team_size, functional_size_delivered,
               notes, consent_for_training, created_at, created_by_user_id
        FROM estimate_actuals
        WHERE estimate_id = $1
        ORDER BY created_at DESC
        """,
        estimate_id,
    )

    return [ActualResponse.model_validate(dict(r)) for r in rows]


@router.get(
    "/admin/actuals/export",
    summary="Export consented actuals in projects_v2 format (Admin only)",
)
async def export_consented_actuals(
    format: Literal["json", "csv"] = Query("json", description="Export format: json or csv"),
    admin: CurrentUser = Depends(require_role("admin")),
):
    """
    Export consented project actuals strictly formatted for projects_v2 dataset compatibility.
    Only entries with consent_for_training=TRUE are included. Restricted to administrators.
    """
    pool = await get_db()
    rows = await pool.fetch(
        """
        SELECT ea.id, ea.estimate_id, ea.actual_effort_hours, ea.actual_cost_usd,
               ea.actual_duration_months, ea.team_size, ea.functional_size_delivered,
               ea.notes, ea.created_at, e.inputs_json
        FROM estimate_actuals ea
        LEFT JOIN estimates e ON ea.estimate_id = e.id
        WHERE ea.consent_for_training = TRUE
        ORDER BY ea.created_at ASC
        """
    )

    export_items: list[ProjectsV2ExportItem] = []
    for r in rows:
        platform, language, dev_type = _extract_inputs_metadata(r["inputs_json"])
        created_at = r["created_at"]
        year = created_at.year if hasattr(created_at, "year") else None

        item = ProjectsV2ExportItem(
            project_id=f"actual_{str(r['id'])[:8]}",
            source="actuals_flywheel",
            year=year,
            size_value=float(r["functional_size_delivered"]) if r["functional_size_delivered"] is not None else None,
            size_unit="FP" if r["functional_size_delivered"] is not None else None,
            effort_hours=float(r["actual_effort_hours"]),
            duration_months=float(r["actual_duration_months"]) if r["actual_duration_months"] is not None else None,
            team_size=int(r["team_size"]) if r["team_size"] is not None else None,
            platform=platform,
            language=language,
            dev_type=dev_type,
            notes=r["notes"] or "",
        )
        export_items.append(item)

    logger.info(
        "admin_actuals_exported",
        admin_id=admin.id,
        count=len(export_items),
        format=format,
    )

    if format == "csv":
        fieldnames = [
            "project_id",
            "source",
            "year",
            "size_value",
            "size_unit",
            "effort_hours",
            "duration_months",
            "team_size",
            "platform",
            "language",
            "dev_type",
            "notes",
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for item in export_items:
            writer.writerow(item.model_dump())

        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="consented_actuals.csv"'},
        )

    return JSONResponse(content=jsonable_encoder([item.model_dump() for item in export_items]))
