"""
Predictify — Audit Logging Middleware (S6)
Logs all API requests for SOC 2 compliance and security monitoring.

Each log entry includes:
  - Timestamp (ISO 8601)
  - Request method and path
  - User ID (from Firebase token, if authenticated)
  - Client IP address
  - Response status code
  - Request duration (ms)
  - Request ID (for correlation)
"""
import time

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger("audit")

# Paths to exclude from audit logging (noisy health/docs endpoints)
_SKIP_PATHS = frozenset({"/health", "/api/v1/health", "/docs", "/openapi.json", "/redoc", "/favicon.ico"})


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Middleware that emits a structured audit log entry for every API request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip noisy endpoints
        if request.url.path in _SKIP_PATHS:
            return await call_next(request)

        start = time.perf_counter()

        # Process the request
        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 1)
        request_id = getattr(request.state, "request_id", "N/A")
        route = request.scope.get("route")

        logger.info(
            "api_request",
            method=request.method,
            path=getattr(route, "path", "unmatched"),
            status=response.status_code,
            duration_ms=duration_ms,
            user=getattr(request.state, "user_id", "anonymous"),
            ip=request.client.host if request.client else "unknown",
            request_id=request_id,
        )

        return response
