"""
Predictify API — Health Check
Exposes model status, training metrics, DB connectivity, and Firebase status.
"""
import time
import structlog
from fastapi import APIRouter
from ml.inference import predictor
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()
logger = structlog.get_logger()

# Track application start time for uptime reporting
_start_time = time.time()


@router.get("/health")
async def health_check():
    """
    Comprehensive health check — verifies DB, ML model, and reports uptime.
    Used by load balancers, Docker HEALTHCHECK, and monitoring tools (D2).
    """
    model_info = predictor.get_model_info()

    # DB connectivity check
    db_status = "unknown"
    try:
        pool = await get_db()
        result = await pool.fetchval("SELECT 1")
        db_status = "connected" if result == 1 else "error"
    except Exception as e:
        db_status = f"error: {type(e).__name__}"
        logger.warning("health_check_db_fail", error=str(e))

    # Firebase status (check if SDK initialized)
    firebase_status = "unknown"
    try:
        import firebase_admin
        app = firebase_admin.get_app()
        firebase_status = "initialized" if app else "not_initialized"
    except Exception:
        firebase_status = "not_initialized"

    # Overall status: healthy only if all critical services are up
    all_healthy = (
        db_status == "connected"
        and predictor.is_ready
        and firebase_status == "initialized"
    )

    uptime_seconds = int(time.time() - _start_time)

    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.APP_VERSION,
        "uptime_seconds": uptime_seconds,
        "services": {
            "database": db_status,
            "ml_model": "ready" if predictor.is_ready else "not_loaded",
            "firebase": firebase_status,
        },
        **model_info,
    }
