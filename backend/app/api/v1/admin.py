"""
Predictify API — Admin Endpoints
Admin-only user management routes (RBAC).

All endpoints require admin role.
"""
from typing import Literal, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import CurrentUser, require_role
from app.services.role_sync import sync_pending

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

    # Lock, update authority and queue synchronization in one database statement.
    existing = await pool.fetchrow(
        """WITH previous AS MATERIALIZED (
               SELECT id, role FROM profiles WHERE id=$2 FOR UPDATE
           ) UPDATE profiles SET role=$1, role_managed=TRUE, role_sync_pending=TRUE,
                 role_sync_after=NOW(), updated_at=NOW()
             FROM previous WHERE profiles.id=previous.id
             RETURNING profiles.id, previous.role""", data.role, user_id
    )
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    old_role = existing["role"] or "editor"

    # Best effort delivery: failure leaves a durable pending update, never a rollback
    # that could race another administrator or restore an already revoked privilege.
    try:
        synced = bool(await sync_pending(user_id))
    except Exception as e:
        synced = False
        logger.error("firebase_claim_sync_failed", error_type=type(e).__name__, user_id=user_id)

    return {
        "user_id": user_id,
        "old_role": old_role,
        "new_role": data.role,
        "synced_to_firebase": synced,
        "sync_pending": not synced,
    }
