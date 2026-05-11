"""
Predictify API — Admin Endpoints
Admin-only user management routes (RBAC).

All endpoints require admin role.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import structlog

from firebase_admin import auth as firebase_auth

from app.core.security import require_role, CurrentUser, VALID_ROLES
from app.core.database import get_db

router = APIRouter()
logger = structlog.get_logger()


class RoleUpdateRequest(BaseModel):
    """Request body for updating a user's role."""
    role: Literal["admin", "editor", "viewer"]


class UserListItem(BaseModel):
    """User item returned in the admin user list."""
    id: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "editor"
    created_at: Optional[str] = None


# ── Admin Endpoints ────────────────────────────────────────────


@router.get("/admin/users")
async def list_users(
    admin: CurrentUser = Depends(require_role("admin")),
):
    """List all users with their roles (admin only)."""
    pool = await get_db()
    rows = await pool.fetch(
        """SELECT id, email, full_name, role, created_at
           FROM profiles
           ORDER BY created_at DESC"""
    )
    return {
        "users": [dict(r) for r in rows],
        "total": len(rows),
    }


@router.patch("/admin/users/{user_id}")
async def update_user_role(
    user_id: str,
    data: RoleUpdateRequest,
    admin: CurrentUser = Depends(require_role("admin")),
):
    """Update a user's role (admin only).

    Security controls:
      - Admins cannot demote themselves (prevents lockout)
      - Role must be one of: admin, editor, viewer
      - Updates both PostgreSQL AND Firebase custom claims
    """
    # Prevent self-demotion
    if user_id == admin.id and data.role != "admin":
        raise HTTPException(
            status_code=400,
            detail="Cannot demote yourself. Ask another admin to change your role.",
        )

    pool = await get_db()

    # Verify user exists
    existing = await pool.fetchrow(
        "SELECT id, role FROM profiles WHERE id = $1", user_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = existing["role"] or "editor"

    # Update role in database
    await pool.execute(
        "UPDATE profiles SET role = $1, updated_at = NOW() WHERE id = $2",
        data.role, user_id,
    )

    # Sync role to Firebase custom claims
    try:
        firebase_auth.set_custom_user_claims(user_id, {"role": data.role})
        logger.info(
            "rbac_role_updated",
            admin_id=admin.id,
            target_user_id=user_id,
            old_role=old_role,
            new_role=data.role,
        )
    except Exception as e:
        # Rollback DB change if Firebase sync fails
        await pool.execute(
            "UPDATE profiles SET role = $1, updated_at = NOW() WHERE id = $2",
            old_role, user_id,
        )
        logger.error("firebase_claim_sync_failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=500,
            detail="Failed to sync role to authentication provider",
        )

    return {
        "user_id": user_id,
        "old_role": old_role,
        "new_role": data.role,
        "synced_to_firebase": True,
    }
