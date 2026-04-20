"""
PredictIQ API — Estimate Endpoints
Core estimation pipeline: analyze, list, get, duplicate, delete, share.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta, timezone
import structlog
import secrets
import bcrypt

from app.core.security import get_current_user, CurrentUser
from app.core.supabase import get_supabase_admin
from app.core.config import settings
from app.models.estimate import (
    EstimateRequest, ManualEstimateRequest, EstimateResult,
    EstimateSummary, EstimateListResponse, EstimateInputs,
    EstimateOutputs, ShareLinkRequest, ShareLinkResponse,
)
from app.services.ml_service import ml_service
from app.services.cost_calculator import (
    estimate_function_points, calculate_cost,
    calculate_timeline, calculate_phase_breakdown,
)
from app.services.risk_analyzer import analyze_risk
from app.services.benchmark import get_benchmark_comparison, get_model_explanation
from app.services.document_parser import document_parser
from app.services.nlp_extractor import nlp_extractor
from ml.inference import predictor

router = APIRouter()
logger = structlog.get_logger()


@router.post("/estimates/analyze", response_model=EstimateResult)
async def analyze_estimate(
    request: EstimateRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """
    Core estimation endpoint. Full pipeline:
    1. Fetch document from Supabase Storage
    2. Parse document text
    3. NLP extraction → project parameters
    4. Apply user overrides
    5. IFPUG Function Points → size_fp
    6. ML prediction → effort_hours
    7. Cost conversion → cost_usd
    8. Risk analysis → risk_score
    9. Save to database
    """
    try:
        supabase = get_supabase_admin()

        # Step 1: Get document metadata
        doc_result = supabase.table("document_uploads").select("*").eq(
            "id", str(request.document_id)
        ).eq("user_id", user.id).single().execute()

        if not doc_result.data:
            raise HTTPException(status_code=404, detail="Document not found")

        doc = doc_result.data

        # Step 2: Download and parse document
        try:
            file_response = supabase.storage.from_(
                settings.SUPABASE_STORAGE_BUCKET
            ).download(doc["storage_path"])
            parse_result = document_parser.parse(file_response, doc["mime_type"])
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
        project_name = (
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

        # Build complete estimate
        return await _run_estimation(
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("estimate_analyze_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


@router.post("/estimates/manual", response_model=EstimateResult)
async def manual_estimate(
    request: ManualEstimateRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Create an estimate from manually entered parameters (no document upload)."""
    try:
        return await _run_estimation(
            user_id=user.id,
            document_id=None,
            project_name=request.project_name,
            project_type=request.project_type,
            team_size=request.team_size,
            duration_months=request.duration_months,
            complexity=request.complexity,
            methodology=request.methodology,
            hourly_rate=request.hourly_rate_usd,
            tech_stack=request.tech_stack,
            feature_count=10,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("manual_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


async def _run_estimation(
    user_id: str,
    document_id: str | None,
    project_name: str,
    project_type: str,
    team_size: int,
    duration_months: float,
    complexity: str,
    methodology: str,
    hourly_rate: float,
    tech_stack: list[str],
    feature_count: int,
    integration_count: int = 2,
    volatility_score: int = 3,
    team_experience: float = 2.0,
) -> EstimateResult:
    """Shared estimation pipeline for both document and manual flows."""

    # Step 5: IFPUG Function Points
    size_fp = estimate_function_points(
        feature_count=feature_count,
        complexity=complexity,
        tech_stack_count=len(tech_stack),
        external_interface_files=min(integration_count, 15),
    )

    # Step 6: ML Prediction
    params = {
        "project_type": project_type,
        "team_size": team_size,
        "duration_months": duration_months,
        "complexity": complexity,
        "tech_stack": tech_stack,
        "size_fp": size_fp,
        "feature_count": feature_count,
        "methodology": methodology,
        "volatility_score": volatility_score,
        "team_experience": team_experience,
    }

    # ── ML_PLACEHOLDER START ─────────────────────────────────────
    ml_result = ml_service.predict(params)
    # ── ML_PLACEHOLDER END ───────────────────────────────────────

    effort_likely = ml_result["effort_hours_likely"]
    effort_min = ml_result["effort_hours_min"]
    effort_max = ml_result["effort_hours_max"]
    confidence = ml_result["confidence_pct"]

    # Step 7: Cost conversion
    costs = calculate_cost(effort_likely, effort_min, effort_max, hourly_rate)

    # Step 8: Timeline
    timeline = calculate_timeline(duration_months, team_size)

    # Phase breakdown
    phases = calculate_phase_breakdown(
        effort_likely, costs["cost_likely_usd"], timeline["timeline_likely_weeks"]
    )

    # Step 9: Risk analysis
    risk_result = analyze_risk(params)

    # Benchmark comparison
    benchmark = get_benchmark_comparison(
        size_fp=size_fp,
        effort_hours_likely=effort_likely,
        cost_likely_usd=costs["cost_likely_usd"],
        duration_months=duration_months,
        hourly_rate=hourly_rate,
    )

    # Model explanation
    explanation = get_model_explanation(
        params=params,
        effort_hours=effort_likely,
        feature_importance=predictor.get_feature_importance(),
    )

    # Build result
    inputs = EstimateInputs(
        project_type=project_type,
        tech_stack=tech_stack,
        team_size=team_size,
        duration_months=duration_months,
        complexity=complexity,
        methodology=methodology,
        hourly_rate_usd=hourly_rate,
    )

    outputs = EstimateOutputs(
        effort_min_hours=effort_min,
        effort_likely_hours=effort_likely,
        effort_max_hours=effort_max,
        cost_min_usd=costs["cost_min_usd"],
        cost_likely_usd=costs["cost_likely_usd"],
        cost_max_usd=costs["cost_max_usd"],
        timeline_min_weeks=timeline["timeline_min_weeks"],
        timeline_likely_weeks=timeline["timeline_likely_weeks"],
        timeline_max_weeks=timeline["timeline_max_weeks"],
        confidence_pct=confidence,
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        top_risks=risk_result["top_risks"],
        phase_breakdown=phases,
        model_explanation=explanation,
        benchmark_comparison=benchmark,
    )

    # Step 10: Save to database
    supabase = get_supabase_admin()
    estimate_data = {
        "user_id": user_id,
        "document_id": document_id,
        "project_name": project_name,
        "status": "complete",
        "inputs_json": inputs.model_dump(),
        "outputs_json": outputs.model_dump(),
        "effort_likely_hours": effort_likely,
        "cost_likely_usd": costs["cost_likely_usd"],
        "duration_likely_weeks": timeline["timeline_likely_weeks"],
        "risk_score": risk_result["risk_score"],
        "confidence_pct": confidence,
    }

    result = supabase.table("estimates").insert(estimate_data).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Failed to save estimate")

    saved = result.data[0]
    logger.info("estimate_created", id=saved["id"], user_id=user_id)

    return EstimateResult(
        estimate_id=saved["id"],
        document_id=document_id,
        user_id=user_id,
        project_name=project_name,
        created_at=saved["created_at"],
        version=saved.get("version", 1),
        status="complete",
        inputs=inputs,
        outputs=outputs,
    )


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
        supabase = get_supabase_admin()
        query = supabase.table("estimates").select(
            "*", count="exact"
        ).eq("user_id", user.id).neq("status", "deleted")

        if project_type:
            query = query.eq("inputs_json->>project_type", project_type)

        # Sorting
        sort_map = {
            "created_at_desc": ("created_at", {"desc": True}),
            "created_at_asc": ("created_at", {"desc": False}),
            "cost_asc": ("cost_likely_usd", {"desc": False}),
            "cost_desc": ("cost_likely_usd", {"desc": True}),
            "risk_desc": ("risk_score", {"desc": True}),
        }
        sort_col, sort_opts = sort_map.get(sort, ("created_at", {"desc": True}))
        query = query.order(sort_col, desc=sort_opts["desc"])

        # Pagination
        start = (page - 1) * per_page
        query = query.range(start, start + per_page - 1)

        result = query.execute()

        estimates = []
        for row in (result.data or []):
            inputs_json = row.get("inputs_json") or {}
            outputs_json = row.get("outputs_json") or {}
            estimates.append(EstimateSummary(
                id=row["id"],
                project_name=row["project_name"],
                project_type=inputs_json.get("project_type", "Unknown"),
                cost_likely_usd=row.get("cost_likely_usd") or 0,
                cost_min_usd=outputs_json.get("cost_min_usd", 0),
                cost_max_usd=outputs_json.get("cost_max_usd", 0),
                risk_score=row.get("risk_score") or 0,
                risk_level=outputs_json.get("risk_level", "Low"),
                confidence_pct=row.get("confidence_pct") or 0,
                duration_likely_weeks=row.get("duration_likely_weeks") or 0,
                status=row["status"],
                version=row.get("version", 1),
                created_at=row["created_at"],
                updated_at=row.get("updated_at"),
            ))

        total = result.count or len(estimates)
        return EstimateListResponse(
            estimates=estimates,
            total=total,
            page=page,
            per_page=per_page,
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
        supabase = get_supabase_admin()
        result = supabase.table("estimates").select("*").eq(
            "id", estimate_id
        ).eq("user_id", user.id).single().execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        row = result.data
        inputs_json = row.get("inputs_json") or {}
        outputs_json = row.get("outputs_json") or {}

        return EstimateResult(
            estimate_id=row["id"],
            document_id=row.get("document_id"),
            user_id=row["user_id"],
            project_name=row["project_name"],
            created_at=row["created_at"],
            version=row.get("version", 1),
            status=row["status"],
            inputs=EstimateInputs(**inputs_json),
            outputs=EstimateOutputs(**outputs_json),
            model_version=row.get("model_version", "1.0.0"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimates/{estimate_id}/duplicate", response_model=EstimateSummary)
async def duplicate_estimate(
    estimate_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Duplicate an estimate as a new version."""
    try:
        supabase = get_supabase_admin()

        # Get original
        original = supabase.table("estimates").select("*").eq(
            "id", estimate_id
        ).eq("user_id", user.id).single().execute()

        if not original.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        row = original.data

        # Get max version for this project
        version_result = supabase.table("estimates").select("version").eq(
            "user_id", user.id
        ).eq("project_name", row["project_name"]).order(
            "version", desc=True
        ).limit(1).execute()

        new_version = (version_result.data[0]["version"] + 1) if version_result.data else 2

        # Insert duplicate
        new_data = {
            "user_id": user.id,
            "document_id": row.get("document_id"),
            "project_name": row["project_name"],
            "version": new_version,
            "status": "complete",
            "inputs_json": row["inputs_json"],
            "outputs_json": row["outputs_json"],
            "effort_likely_hours": row.get("effort_likely_hours"),
            "cost_likely_usd": row.get("cost_likely_usd"),
            "duration_likely_weeks": row.get("duration_likely_weeks"),
            "risk_score": row.get("risk_score"),
            "confidence_pct": row.get("confidence_pct"),
        }

        result = supabase.table("estimates").insert(new_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Duplication failed")

        dup = result.data[0]
        outputs_json = dup.get("outputs_json") or {}
        inputs_json = dup.get("inputs_json") or {}
        return EstimateSummary(
            id=dup["id"],
            project_name=dup["project_name"],
            project_type=inputs_json.get("project_type", "Unknown"),
            cost_likely_usd=dup.get("cost_likely_usd") or 0,
            cost_min_usd=outputs_json.get("cost_min_usd", 0),
            cost_max_usd=outputs_json.get("cost_max_usd", 0),
            risk_score=dup.get("risk_score") or 0,
            risk_level=outputs_json.get("risk_level", "Low"),
            confidence_pct=dup.get("confidence_pct") or 0,
            duration_likely_weeks=dup.get("duration_likely_weeks") or 0,
            status=dup["status"],
            version=dup["version"],
            created_at=dup["created_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("duplicate_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/estimates/{estimate_id}")
async def delete_estimate(
    estimate_id: str,
    user: CurrentUser = Depends(get_current_user),
):
    """Soft-delete an estimate."""
    try:
        supabase = get_supabase_admin()
        result = supabase.table("estimates").update(
            {"status": "deleted"}
        ).eq("id", estimate_id).eq("user_id", user.id).execute()

        if not result.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_estimate_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/estimates/{estimate_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    estimate_id: str,
    request: ShareLinkRequest,
    user: CurrentUser = Depends(get_current_user),
):
    """Generate a shareable read-only link for an estimate."""
    try:
        supabase = get_supabase_admin()

        # Verify ownership
        est = supabase.table("estimates").select("id").eq(
            "id", estimate_id
        ).eq("user_id", user.id).single().execute()

        if not est.data:
            raise HTTPException(status_code=404, detail="Estimate not found")

        token = secrets.token_urlsafe(32)
        expires_at = (
            datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)
        ).isoformat()

        share_data = {
            "estimate_id": estimate_id,
            "token": token,
            "expires_at": expires_at,
        }
        if request.password:
            share_data["password_hash"] = bcrypt.hashpw(
                request.password.encode(), bcrypt.gensalt()
            ).decode()

        result = supabase.table("share_links").insert(share_data).execute()
        if not result.data:
            raise HTTPException(status_code=500, detail="Failed to create share link")

        return ShareLinkResponse(
            share_url=f"/share/{token}",
            token=token,
            expires_at=expires_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("share_link_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
