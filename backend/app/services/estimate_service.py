"""
Predictify — Estimate Service Layer
Extracted from estimates.py (T3.2).

This service encapsulates the core estimation business logic:
  - ML prediction pipeline
  - Database CRUD operations
  - Share link management

Route handlers in estimates.py become thin controllers that delegate here.
"""
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import structlog
from ml.inference import predictor
from starlette.concurrency import run_in_threadpool

from app.core.database import get_db
from app.models.estimate import (
    EstimateInputs,
    EstimateListResponse,
    EstimateOutputs,
    EstimateResult,
    EstimateSummary,
    PhaseBreakdown,
    ShareLinkResponse,
)
from app.services.benchmark import get_benchmark_comparison, get_model_explanation
from app.services.cost_calculator import (
    calculate_cost,
    calculate_phase_breakdown,
    calculate_timeline,
    estimate_function_points,
)
from app.services.ml_service import ml_service
from app.services.risk_analyzer import analyze_risk

logger = structlog.get_logger()


class EstimateService:
    """Service layer for all estimate operations."""

    # ── Estimation Pipeline ────────────────────────────────────────

    async def run_estimation(
        self,
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
        """Core estimation pipeline — shared by both document and manual flows.

        Steps:
          1. IFPUG Function Points → size_fp
          2. ML prediction → effort_hours
          3. Cost conversion → cost_usd
          4. Timeline calculation
          5. Risk analysis → risk_score
          6. Benchmark comparison
          7. Save to database
        """
        # Step 1: IFPUG Function Points
        size_fp = estimate_function_points(
            feature_count=feature_count,
            complexity=complexity,
            tech_stack_count=len(tech_stack),
            external_interface_files=min(integration_count, 15),
        )

        # Step 2: ML Prediction
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

        ml_result = ml_service.predict(params)
        effort_likely = ml_result["effort_hours_likely"]
        effort_min = ml_result["effort_hours_min"]
        effort_max = ml_result["effort_hours_max"]
        confidence = ml_result["confidence_pct"]

        # Step 3: Cost conversion
        costs = calculate_cost(effort_likely, effort_min, effort_max, hourly_rate)

        # Step 4: Timeline
        timeline = calculate_timeline(duration_months, team_size)

        # Phase breakdown
        phases = calculate_phase_breakdown(
            effort_likely, costs["cost_likely_usd"], timeline["timeline_likely_weeks"]
        )

        # Step 5: Risk analysis
        risk_result = analyze_risk(params)

        # Step 6: Benchmark comparison
        benchmark = get_benchmark_comparison(
            size_fp=size_fp,
            effort_hours_likely=effort_likely,
            cost_likely_usd=costs["cost_likely_usd"],
            duration_months=duration_months,
            hourly_rate=hourly_rate,
        )

        explanation = get_model_explanation(
            params=params,
            effort_hours=effort_likely,
            feature_importance=predictor.get_feature_importance(),
        )

        # Build result objects
        inputs = EstimateInputs(
            project_type=project_type,
            tech_stack=tech_stack,
            team_size=team_size,
            duration_months=duration_months,
            complexity=complexity,
            methodology=methodology,
            hourly_rate_usd=hourly_rate,
            feature_count=feature_count,
            integration_count=integration_count,
            volatility_score=volatility_score,
            team_experience=team_experience,
            size_fp=size_fp,
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
            phase_breakdown=[PhaseBreakdown.model_validate(phase) for phase in phases],
            model_explanation=explanation,
            benchmark_comparison=benchmark,
        )

        # Step 7: Save to database
        pool = await get_db()
        inputs_dict = inputs.model_dump()
        outputs_dict = outputs.model_dump()
        model_version = predictor.get_model_info()["model_version"]

        saved = await pool.fetchrow(
            """INSERT INTO estimates
               (user_id, document_id, project_name, status, inputs_json, outputs_json,
                effort_likely_hours, cost_likely_usd, duration_likely_weeks, risk_score, confidence_pct, model_version)
               VALUES ($1, $2, $3, 'complete', $4, $5, $6, $7, $8, $9, $10, $11)
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
            model_version,
        )

        if not saved:
            raise RuntimeError("Failed to save estimate")

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
            model_version=model_version,
        )

    # ── CRUD Operations ────────────────────────────────────────────

    async def list_estimates(
        self,
        user_id: str,
        page: int = 1,
        per_page: int = 20,
        sort: str = "created_at_desc",
        project_type: Optional[str] = None,
    ) -> EstimateListResponse:
        """List estimates for a user with pagination and filtering."""
        pool = await get_db()

        sort_map = {
            "created_at_desc": "created_at DESC",
            "created_at_asc": "created_at ASC",
            "cost_asc": "cost_likely_usd ASC",
            "cost_desc": "cost_likely_usd DESC",
            "risk_desc": "risk_score DESC",
        }
        if sort and sort not in sort_map:
            logger.warning("invalid_sort_param", sort=sort, allowed=list(sort_map.keys()))
        order_clause = sort_map.get(sort, "created_at DESC")
        offset = (page - 1) * per_page

        if project_type:
            rows = await pool.fetch(
                f"""SELECT * FROM estimates
                    WHERE user_id = $1 AND status != 'deleted'
                      AND inputs_json->>'project_type' = $2
                    ORDER BY {order_clause}
                    LIMIT $3 OFFSET $4""",
                user_id, project_type, per_page, offset,
            )
            count_row = await pool.fetchval(
                """SELECT COUNT(*) FROM estimates
                   WHERE user_id = $1 AND status != 'deleted'
                     AND inputs_json->>'project_type' = $2""",
                user_id, project_type,
            )
        else:
            rows = await pool.fetch(
                f"""SELECT * FROM estimates
                    WHERE user_id = $1 AND status != 'deleted'
                    ORDER BY {order_clause}
                    LIMIT $2 OFFSET $3""",
                user_id, per_page, offset,
            )
            count_row = await pool.fetchval(
                """SELECT COUNT(*) FROM estimates
                   WHERE user_id = $1 AND status != 'deleted'""",
                user_id,
            )

        estimates = [self._row_to_summary(row) for row in rows]
        total = count_row or len(estimates)

        return EstimateListResponse(
            estimates=estimates,
            total=total,
            page=page,
            per_page=per_page,
        )

    async def get_estimate(self, estimate_id: str, user_id: str) -> EstimateResult:
        """Get full estimate details by ID."""
        pool = await get_db()
        row = await pool.fetchrow(
            """SELECT * FROM estimates WHERE id = $1 AND user_id = $2 AND status != 'deleted'""",
            estimate_id, user_id,
        )

        if not row:
            return None

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

    async def duplicate_estimate(self, estimate_id: str, user_id: str) -> EstimateSummary:
        """Duplicate an estimate as a new version."""
        pool = await get_db()

        async with pool.acquire() as conn:
            async with conn.transaction():
                row = await conn.fetchrow(
                    "SELECT * FROM estimates WHERE id = $1 AND user_id = $2 AND status != 'deleted'",
                    estimate_id, user_id,
                )
                if not row:
                    return None

                # Ancestors share one lock, even after rename or soft deletion.
                # READ COMMITTED refreshes MAX's snapshot after the lock is acquired.
                await conn.fetchval(
                    "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))",
                    f"{user_id}:{row['lineage_id']}",
                )
                max_version = await conn.fetchval(
                    """SELECT MAX(version) FROM estimates
                       WHERE user_id = $1 AND lineage_id = $2""",
                    user_id, row["lineage_id"],
                )
                new_version = (max_version or 1) + 1

                dup = await conn.fetchrow(
                    """INSERT INTO estimates
                       (user_id, document_id, project_name, version, status,
                        inputs_json, outputs_json, effort_likely_hours, cost_likely_usd,
                        duration_likely_weeks, risk_score, confidence_pct, lineage_id, model_version)
                       VALUES ($1, $2, $3, $4, 'complete', $5, $6, $7, $8, $9, $10, $11, $12, $13)
                       RETURNING *""",
                    user_id,
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
                    row["lineage_id"],
                    row.get("model_version"),
                )
        if not dup:
            raise RuntimeError("Duplication failed")

        return self._row_to_summary(dup)

    async def delete_estimate(self, estimate_id: str, user_id: str) -> bool:
        """Soft-delete an estimate. Returns True if found and deleted."""
        pool = await get_db()
        result = await pool.execute(
            """UPDATE estimates SET status = 'deleted', updated_at = NOW()
               WHERE id = $1 AND user_id = $2""",
            estimate_id, user_id,
        )
        return result != "UPDATE 0"

    async def create_share_link(
        self,
        estimate_id: str,
        user_id: str,
        expires_in_days: int,
        password: Optional[str] = None,
    ) -> Optional[ShareLinkResponse]:
        """Generate a shareable read-only link for an estimate."""
        pool = await get_db()

        est = await pool.fetchrow(
            """SELECT id FROM estimates WHERE id = $1 AND user_id = $2 AND status != 'deleted'""",
            estimate_id, user_id,
        )
        if not est:
            return None

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        password_hash = None
        if password:
            password_hash = (await run_in_threadpool(bcrypt.hashpw,
                password.encode(), bcrypt.gensalt()
            )).decode()

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

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _row_to_summary(row) -> EstimateSummary:
        """Convert a database row to an EstimateSummary."""
        inputs_json = row.get("inputs_json") or {}
        outputs_json = row.get("outputs_json") or {}
        if isinstance(inputs_json, str):
            inputs_json = json.loads(inputs_json)
        if isinstance(outputs_json, str):
            outputs_json = json.loads(outputs_json)

        return EstimateSummary(
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
        )


# Module-level singleton
estimate_service = EstimateService()
