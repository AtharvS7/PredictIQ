"""
Predictify API — Estimate Endpoints (Thin Controller)
Routes delegate to EstimateService for business logic (T3.2).
All database access via asyncpg (Neon PostgreSQL).
"""
import csv
import html
import io
import math
import re
from typing import Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import CurrentUser, get_current_user, require_role
from app.models.estimate import (
    EstimateListResponse,
    EstimateOverrides,
    EstimateRequest,
    EstimateResult,
    EstimateSummary,
    ManualEstimateRequest,
    ShareLinkRequest,
    ShareLinkResponse,
)
from app.schemas.bulk_import import (
    BulkImportResponse,
    BulkImportRowError,
    CalibrationPreviewSummary,
)
from app.services.background_tasks import log_estimation_analytics
from app.services.document_analysis import parse_stored_document
from app.services.estimate_service import estimate_service
from app.services.nlp_extractor import nlp_extractor
from app.services.org_calibration import OrgCalibrationService

router = APIRouter()
logger = structlog.get_logger()



def _sanitize_text(value: str, max_length: int = 200) -> str:
    """Sanitize user-supplied text: strip HTML/script tags, escape entities, limit length (S4)."""
    # Remove script tags and their content
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", value, flags=re.IGNORECASE | re.DOTALL)
    # Remove all remaining HTML tags
    cleaned = re.sub(r"<[^>]+>", "", cleaned)
    # Escape remaining HTML entities
    cleaned = html.escape(cleaned.strip())
    # Truncate to max length
    return cleaned[:max_length]


@router.post("/estimates/analyze", response_model=EstimateResult)
async def analyze_estimate(
    request: EstimateRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Core estimation endpoint. Full pipeline:
    1. Fetch owned document metadata and object bytes
    2. Parse document text
    3. NLP extraction → project parameters
    4. Apply user overrides
    5. Delegate to EstimateService for ML + DB
    """
    try:
        pool = await get_db()

        # Step 1: Get document metadata + file data
        doc = await pool.fetchrow(
            """SELECT * FROM document_uploads
               WHERE id = $1 AND user_id = $2""",
            str(request.document_id),
            user.id,
        )

        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # Step 2: Read the same object stored by the upload route.
        parse_result = await parse_stored_document(doc, user.id)

        # Step 3: NLP extraction
        extracted = nlp_extractor.extract(parse_result.get("raw_text", ""))

        # Step 4: Apply user overrides
        overrides = request.overrides or EstimateOverrides()
        project_name = _sanitize_text(
            getattr(overrides, "project_name", None)
            or extracted.get("project_name", {}).get("value", "")
            or doc["original_filename"].rsplit(".", 1)[0]
        )
        project_type = (
            getattr(overrides, "project_type", None)
            or extracted.get("project_type", {}).get("value", "Web App")
        )
        team_size = (
            getattr(overrides, "team_size", None)
            or extracted.get("team_size", {}).get("value", 5)
        )
        duration_months = (
            getattr(overrides, "duration_months", None)
            or extracted.get("duration_months", {}).get("value", 6.0)
        )
        complexity = (
            getattr(overrides, "complexity", None)
            or extracted.get("complexity", {}).get("value", "Medium")
        )
        methodology = (
            getattr(overrides, "methodology", None)
            or extracted.get("methodology", {}).get("value", "Agile")
        )
        hourly_rate = (
            getattr(overrides, "hourly_rate_usd", None)
            or settings.DEFAULT_HOURLY_RATE_USD
        )
        tech_stack = (
            overrides.tech_stack if overrides.tech_stack is not None
            else extracted.get("tech_stack", {}).get("value", [])
        )
        feature_count = extracted.get("feature_count", {}).get("value", 10)
        integration_count = overrides.integration_count if overrides.integration_count is not None else extracted.get("integration_count", {}).get("value", 2)
        volatility_score = overrides.volatility_score if overrides.volatility_score is not None else extracted.get("volatility_score", {}).get("value", 3)
        team_experience = overrides.team_experience if overrides.team_experience is not None else extracted.get("team_experience", {}).get("value", 2.0)

        # Step 5: Delegate to service
        result = await estimate_service.run_estimation(
            user_id=user.id,
            document_id=str(request.document_id),
            project_name=project_name,
            project_type=project_type,
            team_size=team_size,
            duration_months=duration_months,
            complexity=complexity,
            methodology=methodology,
            hourly_rate=hourly_rate,
            tech_stack=tech_stack,
            feature_count=feature_count,
            integration_count=integration_count,
            volatility_score=volatility_score,
            team_experience=team_experience,
        )

        # Background: log analytics (runs after response is sent)
        background_tasks.add_task(
            log_estimation_analytics,
            estimate_id=result.estimate_id,
            user_id=user.id,
            project_type=project_type,
            effort_hours=result.outputs.effort_likely_hours,
            cost_usd=result.outputs.cost_likely_usd,
            risk_score=result.outputs.risk_score,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("estimate_analyze_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimation failed")


@router.post("/estimates/manual", response_model=EstimateResult)
async def manual_estimate(
    request: ManualEstimateRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Create an estimate from manually entered parameters (no document upload)."""
    try:
        result = await estimate_service.run_estimation(
            user_id=user.id,
            document_id=None,
            project_name=_sanitize_text(request.project_name),
            project_type=request.project_type,
            team_size=request.team_size,
            duration_months=request.duration_months,
            complexity=request.complexity,
            methodology=request.methodology,
            hourly_rate=request.hourly_rate_usd,
            tech_stack=request.tech_stack,
            feature_count=10,
            integration_count=request.integration_count,
            volatility_score=request.volatility_score,
            team_experience=request.team_experience,
        )

        # Background: log analytics
        background_tasks.add_task(
            log_estimation_analytics,
            estimate_id=result.estimate_id,
            user_id=user.id,
            project_type=request.project_type,
            effort_hours=result.outputs.effort_likely_hours,
            cost_usd=result.outputs.cost_likely_usd,
            risk_score=result.outputs.risk_score,
        )

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("manual_estimate_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimation failed")


@router.get("/estimates", response_model=EstimateListResponse)
async def list_estimates(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at_desc"),
    project_type: Optional[str] = None,
    user: CurrentUser = Depends(get_current_user),
):
    """List all estimates for the authenticated user."""
    try:
        return await estimate_service.list_estimates(
            user_id=user.id,
            page=page,
            per_page=per_page,
            sort=sort,
            project_type=project_type,
        )
    except Exception as e:
        logger.error("list_estimates_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimate operation failed")


@router.get("/estimates/{estimate_id}", response_model=EstimateResult)
async def get_estimate(
    estimate_id: UUID,
    user: CurrentUser = Depends(get_current_user),
):
    """Get full estimate details."""
    try:
        result = await estimate_service.get_estimate(str(estimate_id), user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_estimate_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimate operation failed")


@router.post("/estimates/{estimate_id}/duplicate", response_model=EstimateSummary)
async def duplicate_estimate(
    estimate_id: UUID,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Duplicate an estimate as a new version."""
    try:
        result = await estimate_service.duplicate_estimate(str(estimate_id), user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("duplicate_estimate_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimate operation failed")


@router.delete("/estimates/{estimate_id}")
async def delete_estimate(
    estimate_id: UUID,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Soft-delete an estimate."""
    try:
        deleted = await estimate_service.delete_estimate(str(estimate_id), user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_estimate_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimate operation failed")


@router.post("/estimates/{estimate_id}/share", response_model=ShareLinkResponse)
@limiter.limit("10/hour")  # S5: rate-limit share link creation to prevent abuse
async def create_share_link(
    request: Request,
    estimate_id: UUID,
    payload: ShareLinkRequest,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Generate a shareable read-only link for an estimate."""
    try:
        result = await estimate_service.create_share_link(
            estimate_id=str(estimate_id),
            user_id=user.id,
            expires_in_days=payload.expires_in_days,
            password=payload.password,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("share_link_error", error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Estimate operation failed")


@router.post("/estimates/bulk-import", response_model=BulkImportResponse)
async def bulk_import_projects(
    request: Request,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Import historical completed projects from CSV or JSON to calibrate organization estimates."""
    content_type = request.headers.get("content-type", "")
    items_to_process: list[dict] = []

    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

        if isinstance(body, dict):
            items_to_process = body.get("projects", [])
        elif isinstance(body, list):
            items_to_process = body
        else:
            raise HTTPException(status_code=400, detail="JSON payload must be an object with 'projects' key or a list")

    elif "multipart/form-data" in content_type or "text/csv" in content_type:
        try:
            form = await request.form()
            upload = form.get("file")
            if upload is None or isinstance(upload, str) or not hasattr(upload, "read"):
                raise HTTPException(status_code=400, detail="Missing or invalid 'file' in multipart form data")

            file_bytes = await upload.read()
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {exc}") from exc

        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty (0 bytes)")
        if len(file_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Uploaded file exceeds 10MB limit")

        decoded_text = ""
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                decoded_text = file_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if not decoded_text:
            raise HTTPException(status_code=400, detail="Unable to decode file as UTF-8 or Latin-1 text")

        # Determine delimiter
        first_line = decoded_text.splitlines()[0] if decoded_text.splitlines() else ""
        delimiter = ","
        if "\t" in first_line:
            delimiter = "\t"
        elif ";" in first_line:
            delimiter = ";"

        reader = csv.DictReader(io.StringIO(decoded_text), delimiter=delimiter)
        for row in reader:
            normalized_row = {k.strip().lower(): v.strip() for k, v in row.items() if k}
            items_to_process.append(normalized_row)
    else:
        raise HTTPException(status_code=400, detail="Unsupported Content-Type. Must be application/json or multipart/form-data")

    if not items_to_process:
        raise HTTPException(status_code=400, detail="Empty import payload: no records found")

    valid_records: list[dict] = []
    errors: list[BulkImportRowError] = []

    for idx, item in enumerate(items_to_process, start=1):
        # Extract project name
        name = item.get("project_name") or item.get("name") or item.get("project") or f"Project_{idx}"
        name = str(name).strip()

        # Extract size
        size_raw = item.get("size_fp") or item.get("size") or item.get("fp") or item.get("functional_size")
        try:
            size_val = float(size_raw) if size_raw is not None else 0.0
        except (ValueError, TypeError):
            errors.append(BulkImportRowError(row_index=idx, project_name=name, reason="Invalid size_fp: must be a positive number"))
            continue

        if size_val <= 0.0 or not math.isfinite(size_val):
            errors.append(BulkImportRowError(row_index=idx, project_name=name, reason="Invalid size_fp: must be > 0.0"))
            continue

        # Extract actual effort
        effort_raw = item.get("actual_hours") or item.get("effort_hours") or item.get("effort") or item.get("hours") or item.get("actuals")
        try:
            effort_val = float(effort_raw) if effort_raw is not None else 0.0
        except (ValueError, TypeError):
            errors.append(BulkImportRowError(row_index=idx, project_name=name, reason="Invalid actual_hours: must be a positive number"))
            continue

        if effort_val <= 0.0 or not math.isfinite(effort_val):
            errors.append(BulkImportRowError(row_index=idx, project_name=name, reason="Invalid actual_hours: must be > 0.0"))
            continue

        valid_records.append({
            "project_name": name,
            "size_fp": size_val,
            "actual_hours": effort_val,
            "platform": item.get("platform"),
            "tech_stack": item.get("tech_stack") or item.get("language"),
            "dev_type": item.get("dev_type"),
            "completed_at": item.get("completed_at"),
            "notes": item.get("notes"),
        })

    # Run Empirical Bayes Calibration
    cal_service = OrgCalibrationService()
    cal_preview = cal_service.calibrate(valid_records)

    preview_summary = CalibrationPreviewSummary(
        k_projects=cal_preview.k_projects,
        shrinkage_weight=cal_preview.shrinkage_weight,
        global_a=cal_preview.global_a,
        calibrated_a=cal_preview.calibrated_a,
        exponent_b=cal_preview.exponent_b,
        scaling_ratio=cal_preview.scaling_ratio,
        mdape_before=cal_preview.mdape_before,
        mdape_after=cal_preview.mdape_after,
        relative_gain_pct=cal_preview.relative_gain_pct,
        pred25_before=cal_preview.pred25_before,
        pred25_after=cal_preview.pred25_after,
    )

    return BulkImportResponse(
        total_submitted=len(items_to_process),
        valid_count=len(valid_records),
        error_count=len(errors),
        errors=errors,
        calibration_preview=preview_summary,
    )


@router.post("/estimates/calibration-preview", response_model=CalibrationPreviewSummary)
async def preview_calibration(
    request: Request,
    user: CurrentUser = Depends(get_current_user),
):
    """Compute Empirical Bayes calibration preview on submitted project records."""
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {exc}") from exc

    projects: list[dict] = []
    if isinstance(body, dict):
        projects = body.get("projects", [])
    elif isinstance(body, list):
        projects = body

    cal_service = OrgCalibrationService()
    cal_preview = cal_service.calibrate(projects)

    return CalibrationPreviewSummary(
        k_projects=cal_preview.k_projects,
        shrinkage_weight=cal_preview.shrinkage_weight,
        global_a=cal_preview.global_a,
        calibrated_a=cal_preview.calibrated_a,
        exponent_b=cal_preview.exponent_b,
        scaling_ratio=cal_preview.scaling_ratio,
        mdape_before=cal_preview.mdape_before,
        mdape_after=cal_preview.mdape_after,
        relative_gain_pct=cal_preview.relative_gain_pct,
        pred25_before=cal_preview.pred25_before,
        pred25_after=cal_preview.pred25_after,
    )

