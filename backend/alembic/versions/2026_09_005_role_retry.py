"""Schedule failed role synchronization without blocking other accounts."""
from alembic import op

revision = '005_role_retry'
down_revision = '004_managed_roles'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE profiles ADD COLUMN role_sync_after TIMESTAMPTZ NOT NULL DEFAULT NOW()')
    op.execute('CREATE INDEX idx_profiles_role_sync_due ON profiles (role_sync_after) WHERE role_sync_pending')


def downgrade():
    op.execute('DROP INDEX idx_profiles_role_sync_due')
    op.execute('ALTER TABLE profiles DROP COLUMN role_sync_after')
