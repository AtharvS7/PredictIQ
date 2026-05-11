"""
Predictify API — Estimate Endpoints (Thin Controller)
Routes delegate to EstimateService for business logic (T3.2).
All database access via asyncpg (Neon PostgreSQL).
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request as StarletteRequest
from typing import Optional
import re
import html
import structlog


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

from app.core.security import get_current_user, require_role, CurrentUser
from app.core.database import get_db
from app.core.config import settings
from app.models.estimate import (
    EstimateRequest, ManualEstimateRequest, EstimateResult,
    EstimateSummary, EstimateListResponse,
    ShareLinkRequest, ShareLinkResponse,
)
from app.services.estimate_service import estimate_service
from app.services.document_parser import document_parser
from app.services.nlp_extractor import nlp_extractor
from app.services.background_tasks import log_estimation_analytics

router = APIRouter()
logger = structlog.get_logger()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


@router.post("/estimates/analyze", response_model=EstimateResult)
async def analyze_estimate(
    request: EstimateRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(require_role("editor")),
):
    """
    Core estimation endpoint. Full pipeline:
    1. Fetch document from database (BYTEA)
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

        # Step 2: Download and parse document
        try:
            file_data = doc["file_data"]
            if file_data:
                parse_result = document_parser.parse(bytes(file_data), doc["mime_type"])
            else:
                parse_result = {
                    "raw_text": "",
                    "text_preview": "",
                    "word_count": 0,
                    "page_count": None,
                }
        except Exception as parse_err:
            logger.warning("document_parse_fallback", error=str(parse_err))
            parse_result = {
                "raw_text": "",
                "text_preview": "",
                "word_count": 0,
                "page_count": None,
            }

        # Step 3: NLP extraction
        extracted = nlp_extractor.extract(parse_result.get("raw_text", ""))

        # Step 4: Apply user overrides
        overrides = request.overrides or ManualEstimateRequest(
            project_name="Untitled Project"
        )
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
            getattr(overrides, "tech_stack", None)
            or extracted.get("tech_stack", {}).get("value", [])
        )
        feature_count = extracted.get("feature_count", {}).get("value", 10)
        integration_count = extracted.get("integration_count", {}).get("value", 2)
        volatility_score = extracted.get("volatility_score", {}).get("value", 3)
        team_experience = extracted.get("team_experience", {}).get("value", 2.0)

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
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


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
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estimates/{estimate_id}", response_model=EstimateResult)
async def get_estimate(
    estimate_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Get full estimate details."""
    try:
        result = await estimate_service.get_estimate(estimate_id, user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimates/{estimate_id}/duplicate", response_model=EstimateSummary)
async def duplicate_estimate(
    estimate_id: str,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Duplicate an estimate as a new version."""
    try:
        result = await estimate_service.duplicate_estimate(estimate_id, user.id)
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("duplicate_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/estimates/{estimate_id}")
async def delete_estimate(
    estimate_id: str,
    user: CurrentUser = Depends(require_role("editor")),
):
    """Soft-delete an estimate."""
    try:
        deleted = await estimate_service.delete_estimate(estimate_id, user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimates/{estimate_id}/share", response_model=ShareLinkResponse)
@limiter.limit("10/hour")  # S5: rate-limit share link creation to prevent abuse
async def create_share_link(
    request_obj: Request,  # required by slowapi limiter
    estimate_id: str,
    request: ShareLinkRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Generate a shareable read-only link for an estimate."""
    try:
        result = await estimate_service.create_share_link(
            estimate_id=estimate_id,
            user_id=user.id,
            expires_in_days=request.expires_in_days,
            password=request.password,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Estimate not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("share_link_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
