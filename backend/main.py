"""
Predictify Backend — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.currencies import router as currencies_router
from app.api.v1.documents import router as documents_router
from app.api.v1.estimates import router as estimates_router
from app.api.v1.export import router as export_router
from app.api.v1.health import router as health_router
from app.api.v1.profile import router as profile_router
from app.api.v1.shared import router as shared_router

# Load environment variables
from app.core.config import settings
from app.core.database import close_db_pool, init_db_pool
from app.core.rate_limit import limiter
from app.core.security import init_firebase
from app.middleware.audit_log import AuditLogMiddleware
from app.middleware.body_limit import BodyLimitMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("starting_Predictify", env=settings.APP_ENV, version=settings.APP_VERSION)

    # Initialize Firebase Admin SDK
    init_firebase()

    # Initialize database connection pool
    await init_db_pool()

    try:
        # Load ML model
        from ml.inference import predictor
        predictor.load(settings.ML_MODEL_PATH, settings.ML_SCALER_PATH, settings.ML_FEATURES_PATH)
        model_info = predictor.get_model_info()
        logger.info("ml_model_status", ready=predictor.is_ready, mode=model_info.get("model_mode"))

        # Load benchmark data
        from app.services.benchmark import load_benchmark_data
        load_benchmark_data()

        # Startup diagnostics checklist
        logger.info("startup_checklist",
            model_loaded=predictor.is_ready,
            model_mode=model_info.get("model_mode", "unknown"),
            training_samples=model_info.get("training_samples", 0),
            cors_origins=settings.cors_origins,
            app_env=settings.APP_ENV,
        )

        yield
    finally:
        await close_db_pool()
        logger.info("shutting_down_Predictify")
# Create FastAPI application
app = FastAPI(
    title="Predictify API",
    description="AI-Powered Software Project Cost & Timeline Predictor",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Rate limiting — prevents API abuse
app.add_middleware(SlowAPIMiddleware)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware — restrict to needed methods and headers only (S7)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization", "Content-Type", "Accept",
        "X-Request-ID", "X-Requested-With",
    ],
    expose_headers=["X-Request-ID"],
)

app.add_middleware(BodyLimitMiddleware)

# Security headers middleware — OWASP best practices (S8)
@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Add security headers to every response."""
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    # Share URLs contain bearer credentials. Protect error responses as well as
    # successful reads; endpoint headers are discarded on HTTPException.
    if request.url.path.startswith("/api/v1/shared/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response


# Request ID middleware — adds X-Request-ID to every response
@app.middleware("http")
async def add_request_id(request: Request, call_next) -> Response:
    """Attach a unique request ID to every response header."""
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Audit logging middleware — logs every API call for SOC 2 compliance (S6)
app.add_middleware(AuditLogMiddleware)


# Register API routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(documents_router, prefix="/api/v1", tags=["Documents"])
app.include_router(estimates_router, prefix="/api/v1", tags=["Estimates"])
app.include_router(export_router, prefix="/api/v1", tags=["Export"])
app.include_router(currencies_router, prefix="/api/v1", tags=["Currencies"])
app.include_router(profile_router, prefix="/api/v1", tags=["Profile"])
app.include_router(auth_router, prefix="/api/v1", tags=["Auth"])
app.include_router(admin_router, prefix="/api/v1", tags=["Admin"])
app.include_router(shared_router, prefix="/api/v1", tags=["Shared estimates"])


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": "Predictify API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }

