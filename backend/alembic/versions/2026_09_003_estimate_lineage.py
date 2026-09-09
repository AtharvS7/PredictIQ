"""Give estimate versions stable lineage and enforce uniqueness.

Existing relationships cannot reliably be recovered from project names, so each
existing row starts an independent lineage without altering its version.
"""
from alembic import op

revision = "003_estimate_lineage"
down_revision = "002_add_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE estimates ADD COLUMN lineage_id UUID NOT NULL DEFAULT gen_random_uuid()")
    op.execute("""ALTER TABLE estimates ADD CONSTRAINT uq_estimates_lineage_version
                  UNIQUE (user_id, lineage_id, version)""")


def downgrade() -> None:
    op.execute("ALTER TABLE estimates DROP CONSTRAINT uq_estimates_lineage_version")
    op.execute("ALTER TABLE estimates DROP COLUMN lineage_id")
