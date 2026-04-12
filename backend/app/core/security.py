"""
PredictIQ Security Module
Hybrid JWT verification: local HS256 (fast) with Supabase API fallback.

Strategy:
  1. Primary — Local HMAC-SHA256 verification using Supabase's legacy JWT secret.
     This is instant (< 1ms), requires no network call, and is the industry-standard
     approach for stateless token validation.
  2. Fallback — If local verification fails (e.g. token signed with the newer ECC
     P-256 key after key rotation), we call supabase.auth.get_user(token) which
     validates through Supabase's API. Adds ~100ms latency but covers all key types.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import structlog

from app.core.config import settings
from app.core.supabase import get_supabase

logger = structlog.get_logger()
security = HTTPBearer()


class CurrentUser(BaseModel):
    """Represents the authenticated user extracted from a Supabase JWT."""
    id: str
    email: Optional[str] = None
    role: str = "authenticated"


def _verify_jwt_local(token: str) -> dict:
    """
    Verify a Supabase JWT locally using the legacy HS256 shared secret.
    Returns the decoded payload if verification succeeds.
    Raises JWTError if the signature is invalid or the token is expired.
    """
    payload = jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=["HS256"],
        audience="authenticated",
        options={"verify_aud": True},
    )
    return payload


async def _verify_jwt_remote(token: str) -> dict:
    """
    Verify a JWT via Supabase's auth.get_user() API.
    Fallback for tokens signed with newer ECC (P-256) keys.
    Returns a dict with 'sub', 'email', and 'role' keys.
    """
    sb = get_supabase()
    user_response = sb.auth.get_user(token)

    if not user_response or not user_response.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = user_response.user
    return {
        "sub": user.id,
        "email": user.email,
        "role": user.role or "authenticated",
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    FastAPI dependency — extracts the current user from a Supabase JWT.

    Uses a two-tier verification strategy:
      1. Local HS256 verification (instant, no network call)
      2. Supabase API fallback (for ECC-signed tokens after key rotation)
    """
    token = credentials.credentials

    # ── Tier 1: Local HS256 verification ──────────────────────
    try:
        payload = _verify_jwt_local(token)
        user_id = payload.get("sub")
        if not user_id:
            raise JWTError("Missing 'sub' claim")

        logger.debug("jwt_verified", method="local_hs256", user_id=user_id)
        return CurrentUser(
            id=user_id,
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
        )
    except JWTError:
        # HS256 verification failed — token may be signed with ECC key
        pass

    # ── Tier 2: Supabase API fallback ────────────────────────
    try:
        payload = await _verify_jwt_remote(token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        logger.debug("jwt_verified", method="supabase_api", user_id=user_id)
        return CurrentUser(
            id=user_id,
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
