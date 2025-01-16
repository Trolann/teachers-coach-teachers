"""fix credits available

Revision ID: fix_credits_available
Revises: <previous_revision_id>
Create Date: 2025-01-16 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_credits_available'
down_revision = '7c9df6b9f052'  # Points to the previous migration that added credits_available column
branch_labels = None
depends_on = None

def upgrade():
    # Update existing rows to have credits_available = 0
    op.execute("UPDATE credit_pools SET credits_available = 0 WHERE credits_available IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('credit_pools', 'credits_available',
               existing_type=sa.Integer(),
               nullable=False,
               server_default='0')

def downgrade():
    op.alter_column('credit_pools', 'credits_available',
               existing_type=sa.Integer(),
               nullable=True,
               server_default=None)
