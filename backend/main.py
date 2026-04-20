"""
PredictIQ Backend — FastAPI Application Entry Point
"""
import structlog
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.core.config import settings  # noqa: E402
from app.api.v1.health import router as health_router  # noqa: E402
from app.api.v1.documents import router as documents_router  # noqa: E402
from app.api.v1.estimates import router as estimates_router  # noqa: E402
from app.api.v1.export import router as export_router  # noqa: E402
from app.api.v1.currencies import router as currencies_router  # noqa: E402

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
    logger.info("starting_predictiq", env=settings.APP_ENV, version=settings.APP_VERSION)

    # Load ML model
    from ml.inference import predictor
    predictor.load()
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

    # Shutdown
    logger.info("shutting_down_predictiq")


# Create FastAPI application
app = FastAPI(
    title="PredictIQ API",
    description="AI-Powered Software Project Cost & Timeline Predictor",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Rate limiting — prevents API abuse
limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware — adds X-Request-ID to every response
@app.middleware("http")
async def add_request_id(request: Request, call_next) -> Response:
    """Attach a unique request ID to every response header."""
    request_id = str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Register API routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(documents_router, prefix="/api/v1", tags=["Documents"])
app.include_router(estimates_router, prefix="/api/v1", tags=["Estimates"])
app.include_router(export_router, prefix="/api/v1", tags=["Export"])
app.include_router(currencies_router, prefix="/api/v1", tags=["Currencies"])


@app.get("/")
async def root():
    """Root endpoint — API info."""
    return {
        "name": "PredictIQ API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health",
    }

