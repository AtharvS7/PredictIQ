"""Durable application role authority and pending Firebase synchronization."""
from alembic import op

revision = '004_managed_roles'
down_revision = '003_estimate_lineage'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE profiles ADD COLUMN role_managed BOOLEAN NOT NULL DEFAULT FALSE')
    op.execute('ALTER TABLE profiles ADD COLUMN role_sync_pending BOOLEAN NOT NULL DEFAULT FALSE')
    op.execute('CREATE INDEX idx_profiles_role_sync_pending ON profiles (id) WHERE role_sync_pending')


def downgrade():
    op.execute('DROP INDEX idx_profiles_role_sync_pending')
    op.execute('ALTER TABLE profiles DROP COLUMN role_sync_pending')
    op.execute('ALTER TABLE profiles DROP COLUMN role_managed')
