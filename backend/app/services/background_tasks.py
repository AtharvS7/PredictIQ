"""
Predictify — Background Task Service (T3.5)
FastAPI BackgroundTasks wrapper for async processing.

Handles:
  - Async document parsing (NLP extraction)
  - Post-estimation analytics logging
  - Future: email notifications, webhook delivery

Using FastAPI's built-in BackgroundTasks (zero infra, upgrade-ready to arq/Celery).
"""

import structlog

from app.core.database import get_db

logger = structlog.get_logger()


async def log_estimation_analytics(
    estimate_id: str,
    user_id: str,
    project_type: str,
    effort_hours: float,
    cost_usd: float,
    risk_score: float,
):
    """Background task: Log estimation analytics for future model retraining.

    This runs after the HTTP response is sent, so it doesn't block the user.
    """
    try:
        logger.info(
            "estimation_analytics",
            estimate_id=estimate_id,
            user_id=user_id,
            project_type=project_type,
            effort_hours=round(effort_hours, 1),
            cost_usd=round(cost_usd, 2),
            risk_score=round(risk_score, 2),
        )
    except Exception as e:
        # Background tasks should never crash — log and continue
        logger.error("analytics_background_task_failed", error=str(e))


async def update_document_preview(document_id: str, text_preview: str):
    """Background task: Update document parsed text preview after upload.

    This runs after the upload response is sent.
    """
    try:
        pool = await get_db()
        await pool.execute(
            """UPDATE document_uploads
               SET parsed_text_preview = $1, status = 'parsed'
               WHERE id = $2""",
            text_preview[:500],  # Truncate preview to 500 chars
            document_id,
        )
        logger.debug("document_preview_updated", document_id=document_id)
    except Exception as e:
        logger.error("document_preview_update_failed", error=str(e), document_id=document_id)


async def sync_profile_role(user_id: str, role: str):
    """Background task: Ensure DB profile role matches Firebase custom claims.

    Called after login to keep roles in sync.
    """
    try:
        pool = await get_db()
        await pool.execute(
            """UPDATE profiles SET role = $1, updated_at = NOW()
               WHERE id = $2 AND (role IS NULL OR role != $1)""",
            role, user_id,
        )
    except Exception as e:
        logger.error("profile_role_sync_failed", error=str(e), user_id=user_id)
