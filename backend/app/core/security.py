"""
Predictify Security Module
Firebase Admin SDK token verification + RBAC.

Strategy:
  Verify Firebase ID tokens using the Firebase Admin SDK.
  Extracts role from Firebase custom claims for RBAC enforcement.
  Provides require_role() dependency factory for route-level access control.
"""
from typing import Optional

import firebase_admin
import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from app.core.config import settings

logger = structlog.get_logger()
security = HTTPBearer()

# ── Firebase Admin SDK initialization ──────────────────────────
_firebase_app = None


def init_firebase():
    """Initialize Firebase Admin SDK. Called once during app startup.

    Supports two credential sources (checked in order):
      1. FIREBASE_CREDENTIALS_JSON env var — raw JSON string (Codespaces / Railway)
      2. FIREBASE_CREDENTIALS_PATH — path to a .json file (local dev)
    """
    global _firebase_app
    if _firebase_app is not None:
        return

    import json
    import os

    # Option 1: Raw JSON from environment variable
    json_str = settings.FIREBASE_CREDENTIALS_JSON
    if json_str:
        try:
            cert_dict = json.loads(json_str)
            cred = credentials.Certificate(cert_dict)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("firebase_admin_initialized", source="env_var",
                        project_id=cert_dict.get("project_id"))
            return
        except Exception as e:
            logger.error("firebase_json_env_parse_error", error=str(e))

    # Option 2: JSON file on disk
    cred_path = settings.FIREBASE_CREDENTIALS_PATH
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("firebase_admin_initialized", source="file", project_id=cred.project_id)
        return

    raise FileNotFoundError(
        f"Firebase credentials not found. Either:\n"
        f"  1. Set FIREBASE_CREDENTIALS_JSON env var with the JSON content, or\n"
        f"  2. Place the service account file at: {cred_path}"
    )


# ── RBAC ───────────────────────────────────────────────────────

# Role hierarchy — higher number = more privileges
ROLE_HIERARCHY = {"viewer": 1, "editor": 2, "admin": 3}
VALID_ROLES = frozenset(ROLE_HIERARCHY.keys())


class CurrentUser(BaseModel):
    """Represents the authenticated user extracted from a Firebase ID token."""
    id: str
    email: Optional[str] = None
    role: str = "editor"


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    FastAPI dependency — extracts the current user from a Firebase ID token.

    Verifies the token using Firebase Admin SDK, which checks:
      - Token signature against Google's public keys
      - Token expiration
      - Audience matches our Firebase project
      - Issuer is correct

    Extracts role from Firebase custom claims (set via Admin SDK).
    Falls back to 'editor' if no custom claim is present.
    """
    token = credentials.credentials

    try:
        decoded = await run_in_threadpool(firebase_auth.verify_id_token, token, check_revoked=True)
        user_id = decoded.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        # Extract role from Firebase custom claims
        role = decoded.get("role", "editor")
        if role not in VALID_ROLES:
            role = "viewer"

        logger.debug("jwt_verified", method="firebase_admin", user_id=user_id, role=role)
        user = CurrentUser(
            id=user_id,
            email=decoded.get("email"),
            role=role,
        )
        request.state.user_id = user.id
        request.state.user_role = user.role
        return user
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (firebase_auth.InvalidIdTokenError, firebase_auth.UserDisabledError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception:
        logger.error("auth_verification_failed")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(minimum_role: str):
    """FastAPI dependency factory — enforces a minimum role level.

    Usage:
        @router.post("/admin-only")
        async def admin_action(user: CurrentUser = Depends(require_role("admin"))):
            ...

    Role hierarchy: admin > editor > viewer
    A user with 'admin' role passes checks for 'editor' and 'viewer'.
    """
    if minimum_role not in VALID_ROLES:
        raise ValueError(f"Invalid role: {minimum_role}. Must be one of {VALID_ROLES}")

    required_level = ROLE_HIERARCHY[minimum_role]

    async def _check_role(
        user: CurrentUser = Depends(get_current_user),
    ) -> CurrentUser:
        user_level = ROLE_HIERARCHY.get(user.role, 0)
        if user_level < required_level:
            logger.warning(
                "rbac_denied",
                user_id=user.id,
                user_role=user.role,
                required_role=minimum_role,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {minimum_role}",
            )
        return user

    return _check_role
