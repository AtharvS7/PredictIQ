"""Add owner-scoped task budgets without modifying existing estimates."""
from alembic import op

revision = "006_manual_budgets"
down_revision = "005_role_retry"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE budgets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id TEXT NOT NULL,
            inputs_json JSONB NOT NULL CHECK (jsonb_typeof(inputs_json) = 'object'),
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX idx_budgets_owner_created ON budgets(user_id, created_at DESC, id DESC)")


def downgrade():
    op.execute("DROP TABLE budgets")
