"""
Predictify API — Estimate Endpoints (Thin Controller)
Routes delegate to EstimateService for business logic (T3.2).
All database access via asyncpg (Neon PostgreSQL).
"""
import html
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
from app.services.background_tasks import log_estimation_analytics
from app.services.document_analysis import parse_stored_document
from app.services.estimate_service import estimate_service
from app.services.nlp_extractor import nlp_extractor

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
        logger.error("estimate_analyze_error", error=str(e))
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
        logger.error("manual_estimate_error", error=str(e))
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
        logger.error("list_estimates_error", error=str(e))
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
        logger.error("get_estimate_error", error=str(e))
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
        logger.error("duplicate_estimate_error", error=str(e))
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
        logger.error("delete_estimate_error", error=str(e))
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
        logger.error("share_link_error", error=str(e))
        raise HTTPException(status_code=500, detail="Estimate operation failed")
