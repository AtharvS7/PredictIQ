"""
PredictIQ Security Module
Firebase Admin SDK token verification.

Strategy:
  Verify Firebase ID tokens using the Firebase Admin SDK.
  This validates the token signature, expiration, audience, and issuer
  against Google's public keys — no shared secret needed.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import structlog

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

from app.core.config import settings

logger = structlog.get_logger()
security = HTTPBearer()

# ── Firebase Admin SDK initialization ──────────────────────────
_firebase_app = None


def init_firebase():
    """Initialize Firebase Admin SDK. Called once during app startup."""
    global _firebase_app
    if _firebase_app is None:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        _firebase_app = firebase_admin.initialize_app(cred)
        logger.info("firebase_admin_initialized", project_id=cred.project_id)


class CurrentUser(BaseModel):
    """Represents the authenticated user extracted from a Firebase ID token."""
    id: str
    email: Optional[str] = None
    role: str = "authenticated"


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    FastAPI dependency — extracts the current user from a Firebase ID token.

    Verifies the token using Firebase Admin SDK, which checks:
      - Token signature against Google's public keys
      - Token expiration
      - Audience matches our Firebase project
      - Issuer is correct
    """
    token = credentials.credentials

    try:
        decoded = firebase_auth.verify_id_token(token)
        user_id = decoded.get("uid")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        logger.debug("jwt_verified", method="firebase_admin", user_id=user_id)
        return CurrentUser(
            id=user_id,
            email=decoded.get("email"),
            role="authenticated",
        )
    except firebase_auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.InvalidIdTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except firebase_auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error("auth_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
