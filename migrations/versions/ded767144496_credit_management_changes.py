"""Credit management changes

Revision ID: ded767144496
Revises: 
Create Date: 2024-12-24 17:46:29.037580

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ded767144496'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mentor_profile')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('credits', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('credits')

    op.create_table('mentor_profile',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('bio', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('expertise_areas', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True),
    sa.Column('years_of_experience', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('application_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('application_submitted_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('vector_embedding', postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='mentor_profile_pkey')
    )
    # ### end Alembic commands ###
