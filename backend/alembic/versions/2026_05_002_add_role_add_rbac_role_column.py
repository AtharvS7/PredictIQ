"""Add RBAC role column to profiles

Revision ID: 002_add_role
Revises: 001_initial
Create Date: 2026-05-11
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002_add_role"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add role column and email column to profiles for RBAC."""
    op.execute("""
        ALTER TABLE profiles
          ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'editor'
          CHECK (role IN ('admin', 'editor', 'viewer'))
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_role ON profiles(role)")

    op.execute("ALTER TABLE profiles ADD COLUMN IF NOT EXISTS email TEXT")
    op.execute("CREATE INDEX IF NOT EXISTS idx_profiles_email ON profiles(email)")


def downgrade() -> None:
    """Remove role and email columns."""
    op.execute("DROP INDEX IF EXISTS idx_profiles_role")
    op.execute("DROP INDEX IF EXISTS idx_profiles_email")
    op.execute("ALTER TABLE profiles DROP COLUMN IF EXISTS role")
    op.execute("ALTER TABLE profiles DROP COLUMN IF EXISTS email")
