"""
PredictIQ API — Auth Endpoints
Firebase token verification and user sync (backed by Neon PostgreSQL).
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import structlog

from app.core.security import get_current_user, CurrentUser
from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()


class AuthResponse(BaseModel):
    """Response returned after successful Firebase auth sync."""
    user_id: str
    email: str | None = None
    is_new: bool = False


@router.post("/auth/firebase", response_model=AuthResponse)
async def firebase_auth(user: CurrentUser = Depends(get_current_user)):
    """
    Verify a Firebase ID token and sync the user into the database.

    Called by the frontend after signInWithPopup (Google/GitHub) or
    signInWithEmailAndPassword. The token is already verified by
    `get_current_user` — this endpoint ensures the user exists in
    our Neon PostgreSQL profiles table.
    """
    pool = await get_db()

    # Check if profile already exists
    existing = await pool.fetchrow(
        "SELECT id FROM profiles WHERE id = $1", user.id
    )

    is_new = existing is None

    if is_new:
        # Create a default profile for new OAuth users
        await pool.execute(
            """INSERT INTO profiles (id, full_name, avatar_url, hourly_rate_usd, currency, theme, timezone)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               ON CONFLICT (id) DO NOTHING""",
            user.id,
            "",  # full_name — will be updated by frontend
            "",  # avatar_url — will be updated by frontend
            75.0,
            "USD",
            "system",
            "UTC",
        )
        logger.info("new_user_synced", user_id=user.id, email=user.email)
    else:
        logger.debug("user_auth_verified", user_id=user.id, email=user.email)

    return AuthResponse(
        user_id=user.id,
        email=user.email,
        is_new=is_new,
    )
