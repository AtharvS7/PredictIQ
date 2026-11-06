"""Create estimate_actuals table for actuals flywheel (CP06)."""
from typing import Sequence, Union

from alembic import op

revision: str = "007_estimate_actuals"
down_revision: Union[str, None] = "006_manual_budgets"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE IF NOT EXISTS estimate_actuals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            estimate_id UUID NOT NULL REFERENCES estimates(id) ON DELETE CASCADE,
            actual_effort_hours DOUBLE PRECISION NOT NULL CHECK (actual_effort_hours > 0),
            actual_cost_usd DOUBLE PRECISION CHECK (actual_cost_usd IS NULL OR actual_cost_usd >= 0),
            actual_duration_months DOUBLE PRECISION CHECK (actual_duration_months IS NULL OR actual_duration_months >= 0),
            team_size INTEGER CHECK (team_size IS NULL OR team_size >= 1),
            functional_size_delivered DOUBLE PRECISION CHECK (functional_size_delivered IS NULL OR functional_size_delivered >= 0),
            notes TEXT,
            consent_for_training BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            created_by_user_id TEXT NOT NULL
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_estimate_actuals_estimate_id ON estimate_actuals(estimate_id)")
    op.execute("CREATE INDEX IF NOT EXISTS idx_estimate_actuals_consent ON estimate_actuals(consent_for_training) WHERE consent_for_training = TRUE")
    op.execute("CREATE INDEX IF NOT EXISTS idx_estimate_actuals_created_by ON estimate_actuals(created_by_user_id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS estimate_actuals CASCADE")
