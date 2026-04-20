"""
PredictIQ API — Estimate Endpoints
Core estimation pipeline: analyze, list, get, duplicate, delete, share.
All database access via asyncpg (Neon PostgreSQL).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta, timezone
import structlog
import json
import secrets
import bcrypt

from app.core.security import get_current_user, CurrentUser
from app.core.database import get_db
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
    build_feature_vector_params,
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
    1. Fetch document from database (BYTEA)
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

    # Step 10: Save to database via asyncpg
    pool = await get_db()
    inputs_dict = inputs.model_dump()
    outputs_dict = outputs.model_dump()

    saved = await pool.fetchrow(
        """INSERT INTO estimates
           (user_id, document_id, project_name, status, inputs_json, outputs_json,
            effort_likely_hours, cost_likely_usd, duration_likely_weeks, risk_score, confidence_pct)
           VALUES ($1, $2, $3, 'complete', $4, $5, $6, $7, $8, $9, $10)
           RETURNING *""",
        user_id,
        document_id,
        project_name,
        json.dumps(inputs_dict),
        json.dumps(outputs_dict),
        effort_likely,
        costs["cost_likely_usd"],
        timeline["timeline_likely_weeks"],
        risk_result["risk_score"],
        confidence,
    )

    if not saved:
        raise HTTPException(status_code=500, detail="Failed to save estimate")

    logger.info("estimate_created", id=str(saved["id"]), user_id=user_id)

    return EstimateResult(
        estimate_id=str(saved["id"]),
        document_id=document_id,
        user_id=user_id,
        project_name=project_name,
        created_at=str(saved["created_at"]),
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
        pool = await get_db()

        # Build sort clause
        sort_map = {
            "created_at_desc": "created_at DESC",
            "created_at_asc": "created_at ASC",
            "cost_asc": "cost_likely_usd ASC",
            "cost_desc": "cost_likely_usd DESC",
            "risk_desc": "risk_score DESC",
        }
        order_clause = sort_map.get(sort, "created_at DESC")
        offset = (page - 1) * per_page

        # Build query with optional project_type filter
        if project_type:
            rows = await pool.fetch(
                f"""SELECT * FROM estimates
                    WHERE user_id = $1 AND status != 'deleted'
                      AND inputs_json->>'project_type' = $2
                    ORDER BY {order_clause}
                    LIMIT $3 OFFSET $4""",
                user.id, project_type, per_page, offset,
            )
            count_row = await pool.fetchval(
                """SELECT COUNT(*) FROM estimates
                   WHERE user_id = $1 AND status != 'deleted'
                     AND inputs_json->>'project_type' = $2""",
                user.id, project_type,
            )
        else:
            rows = await pool.fetch(
                f"""SELECT * FROM estimates
                    WHERE user_id = $1 AND status != 'deleted'
                    ORDER BY {order_clause}
                    LIMIT $2 OFFSET $3""",
                user.id, per_page, offset,
            )
            count_row = await pool.fetchval(
                """SELECT COUNT(*) FROM estimates
                   WHERE user_id = $1 AND status != 'deleted'""",
                user.id,
            )

        estimates = []
        for row in rows:
            inputs_json = row.get("inputs_json") or {}
            outputs_json = row.get("outputs_json") or {}
            # asyncpg returns JSONB as dict already, but handle string case
            if isinstance(inputs_json, str):
                inputs_json = json.loads(inputs_json)
            if isinstance(outputs_json, str):
                outputs_json = json.loads(outputs_json)

            estimates.append(EstimateSummary(
                id=str(row["id"]),
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
                created_at=str(row["created_at"]),
                updated_at=str(row["updated_at"]) if row.get("updated_at") else None,
            ))

        total = count_row or len(estimates)
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
        pool = await get_db()
        row = await pool.fetchrow(
            """SELECT * FROM estimates WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )

        if not row:
            raise HTTPException(status_code=404, detail="Estimate not found")

        inputs_json = row.get("inputs_json") or {}
        outputs_json = row.get("outputs_json") or {}
        if isinstance(inputs_json, str):
            inputs_json = json.loads(inputs_json)
        if isinstance(outputs_json, str):
            outputs_json = json.loads(outputs_json)

        return EstimateResult(
            estimate_id=str(row["id"]),
            document_id=str(row["document_id"]) if row.get("document_id") else None,
            user_id=row["user_id"],
            project_name=row["project_name"],
            created_at=str(row["created_at"]),
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
        pool = await get_db()

        # Get original
        row = await pool.fetchrow(
            """SELECT * FROM estimates WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )
        if not row:
            raise HTTPException(status_code=404, detail="Estimate not found")

        # Get max version for this project
        max_version = await pool.fetchval(
            """SELECT MAX(version) FROM estimates
               WHERE user_id = $1 AND project_name = $2""",
            user.id, row["project_name"],
        )
        new_version = (max_version or 1) + 1

        # Insert duplicate
        dup = await pool.fetchrow(
            """INSERT INTO estimates
               (user_id, document_id, project_name, version, status,
                inputs_json, outputs_json, effort_likely_hours, cost_likely_usd,
                duration_likely_weeks, risk_score, confidence_pct)
               VALUES ($1, $2, $3, $4, 'complete', $5, $6, $7, $8, $9, $10, $11)
               RETURNING *""",
            user.id,
            row.get("document_id"),
            row["project_name"],
            new_version,
            json.dumps(row["inputs_json"]) if isinstance(row["inputs_json"], dict) else row["inputs_json"],
            json.dumps(row["outputs_json"]) if isinstance(row["outputs_json"], dict) else row["outputs_json"],
            row.get("effort_likely_hours"),
            row.get("cost_likely_usd"),
            row.get("duration_likely_weeks"),
            row.get("risk_score"),
            row.get("confidence_pct"),
        )

        if not dup:
            raise HTTPException(status_code=500, detail="Duplication failed")

        outputs_json = dup.get("outputs_json") or {}
        inputs_json = dup.get("inputs_json") or {}
        if isinstance(inputs_json, str):
            inputs_json = json.loads(inputs_json)
        if isinstance(outputs_json, str):
            outputs_json = json.loads(outputs_json)

        return EstimateSummary(
            id=str(dup["id"]),
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
            created_at=str(dup["created_at"]),
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
        pool = await get_db()
        result = await pool.execute(
            """UPDATE estimates SET status = 'deleted', updated_at = NOW()
               WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )

        # asyncpg execute returns a string like "UPDATE 1"
        if result == "UPDATE 0":
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
        pool = await get_db()

        # Verify ownership
        est = await pool.fetchrow(
            """SELECT id FROM estimates WHERE id = $1 AND user_id = $2""",
            estimate_id, user.id,
        )
        if not est:
            raise HTTPException(status_code=404, detail="Estimate not found")

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=request.expires_in_days)

        password_hash = None
        if request.password:
            password_hash = bcrypt.hashpw(
                request.password.encode(), bcrypt.gensalt()
            ).decode()

        await pool.execute(
            """INSERT INTO share_links (estimate_id, token, password_hash, expires_at)
               VALUES ($1, $2, $3, $4)""",
            estimate_id, token, password_hash, expires_at,
        )

        return ShareLinkResponse(
            share_url=f"/share/{token}",
            token=token,
            expires_at=expires_at.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("share_link_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
