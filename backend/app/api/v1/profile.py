"""
Predictify API — Profile Endpoints
User profile management (backed by Neon PostgreSQL).
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import structlog

from app.core.security import get_current_user, CurrentUser
from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()

# ── Allowlisted columns that may be updated via PATCH/POST ──────
# This prevents SQL injection by ensuring only known column names
# are interpolated into queries (never user-supplied strings).
ALLOWED_PROFILE_COLUMNS = frozenset({
    "full_name", "avatar_url", "hourly_rate_usd",
    "currency", "theme", "timezone",
})


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    hourly_rate_usd: Optional[float] = None
    currency: Optional[str] = None
    theme: Optional[str] = None
    timezone: Optional[str] = None


def _build_update_query(updates: dict) -> tuple[str, list]:
    """Build a safe UPDATE query using only allowlisted column names.

    Returns:
        Tuple of (query_string, list_of_parameter_values).
        Parameter $1 is always the user id.
    """
    safe_updates = {
        k: v for k, v in updates.items()
        if k in ALLOWED_PROFILE_COLUMNS
    }
    if not safe_updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    set_parts = []
    values = []
    for idx, (col, val) in enumerate(safe_updates.items(), start=2):
        set_parts.append(f"{col} = ${idx}")
        values.append(val)

    set_clause = ", ".join(set_parts)
    query = f"UPDATE profiles SET {set_clause}, updated_at = NOW() WHERE id = $1 RETURNING *"
    return query, values


@router.get("/profile")
async def get_profile(user: CurrentUser = Depends(get_current_user)):
    """Get the current user's profile."""
    pool = await get_db()
    row = await pool.fetchrow(
        "SELECT * FROM profiles WHERE id = $1", user.id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    return dict(row)


@router.post("/profile")
async def create_or_update_profile(
    data: ProfileUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    """Create or update the current user's profile (upsert)."""
    pool = await get_db()

    # Check if profile exists
    existing = await pool.fetchrow(
        "SELECT id FROM profiles WHERE id = $1", user.id
    )

    if existing:
        # Update existing profile
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if updates:
            query, values = _build_update_query(updates)
            row = await pool.fetchrow(query, user.id, *values)
        else:
            row = existing
    else:
        # Create new profile
        row = await pool.fetchrow(
            """INSERT INTO profiles (id, full_name, avatar_url, hourly_rate_usd, currency, theme, timezone)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               RETURNING *""",
            user.id,
            data.full_name or "",
            data.avatar_url or "",
            data.hourly_rate_usd or 75.0,
            data.currency or "USD",
            data.theme or "system",
            data.timezone or "UTC",
        )

    logger.info("profile_upserted", user_id=user.id)
    return dict(row)


@router.patch("/profile")
async def patch_profile(
    data: ProfileUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    """Partially update the current user's profile."""
    pool = await get_db()

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    query, values = _build_update_query(updates)
    row = await pool.fetchrow(query, user.id, *values)

    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    return dict(row)
