"""Updates pre-embeddings

Revision ID: 4700fc4eaabe
Revises: 883b5867cba1
Create Date: 2025-03-10 19:02:36.060211

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '4700fc4eaabe'
down_revision = '883b5867cba1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # Drop mentor_profiles cascade to fix constraint dependency issue
    op.execute('DROP TABLE mentor_profiles CASCADE')


    op.drop_table('mytable')
    with op.batch_alter_table('credit_pools', schema=None) as batch_op:
        batch_op.drop_constraint('credit_pools_owner_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['owner_id'], ['cognito_sub'], ondelete='CASCADE')

    with op.batch_alter_table('credit_redemptions', schema=None) as batch_op:
        batch_op.drop_constraint('credit_redemptions_created_by_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['created_by'], ['cognito_sub'], ondelete='CASCADE')

    with op.batch_alter_table('mentorship_sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('meta_data', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.alter_column('mentee_id',
               existing_type=sa.VARCHAR(length=36),
               type_=sa.String(length=100),
               existing_nullable=False)
        batch_op.alter_column('mentor_id',
               existing_type=sa.VARCHAR(length=36),
               type_=sa.String(length=100),
               existing_nullable=False)
        # Use server_default with explicit USING clause for enum conversion
        batch_op.execute('ALTER TABLE mentorship_sessions ALTER COLUMN status TYPE sessionstatus USING status::text::sessionstatus')
        batch_op.alter_column('mentor_feedback',
               existing_type=sa.TEXT(),
               type_=sa.JSON(),
               existing_nullable=True)
        batch_op.alter_column('mentee_feedback',
               existing_type=sa.TEXT(),
               type_=sa.JSON(),
               existing_nullable=True)
        batch_op.create_index(batch_op.f('ix_mentorship_sessions_mentee_id'), ['mentee_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mentorship_sessions_mentor_id'), ['mentor_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_mentorship_sessions_scheduled_datetime'), ['scheduled_datetime'], unique=False)
        batch_op.create_index(batch_op.f('ix_mentorship_sessions_status'), ['status'], unique=False)
        batch_op.drop_constraint('mentorship_sessions_mentee_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('mentorship_sessions_mentor_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['mentee_id'], ['cognito_sub'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'users', ['mentor_id'], ['cognito_sub'], ondelete='CASCADE')
        batch_op.drop_column('zoom_meeting_link')
        batch_op.drop_column('google_calendar_event_id')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_type', sa.Enum('MENTOR', 'MENTEE', name='usertype'), nullable=False))
        batch_op.add_column(sa.Column('profile', sa.JSON(), nullable=False))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False))
        batch_op.add_column(sa.Column('application_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'REVOKED', name='applicationstatus'), nullable=True))
        batch_op.alter_column('cognito_sub',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.drop_constraint('users_cognito_sub_key', type_='unique')
        batch_op.drop_constraint('users_email_key', type_='unique')
        batch_op.create_index(batch_op.f('ix_users_application_status'), ['application_status'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_created_at'), ['created_at'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_user_type'), ['user_type'], unique=False)
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False))
        batch_op.drop_index(batch_op.f('ix_users_user_type'))
        batch_op.drop_index(batch_op.f('ix_users_email'))
        batch_op.drop_index(batch_op.f('ix_users_created_at'))
        batch_op.drop_index(batch_op.f('ix_users_application_status'))
        batch_op.create_unique_constraint('users_email_key', ['email'])
        batch_op.create_unique_constraint('users_cognito_sub_key', ['cognito_sub'])
        batch_op.alter_column('cognito_sub',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.drop_column('application_status')
        batch_op.drop_column('is_active')
        batch_op.drop_column('created_at')
        batch_op.drop_column('profile')
        batch_op.drop_column('user_type')

    with op.batch_alter_table('mentorship_sessions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_calendar_event_id', sa.VARCHAR(length=100), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('zoom_meeting_link', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('mentorship_sessions_mentor_id_fkey', 'mentor_profiles', ['mentor_id'], ['id'])
        batch_op.create_foreign_key('mentorship_sessions_mentee_id_fkey', 'users', ['mentee_id'], ['id'])
        batch_op.drop_index(batch_op.f('ix_mentorship_sessions_status'))
        batch_op.drop_index(batch_op.f('ix_mentorship_sessions_scheduled_datetime'))
        batch_op.drop_index(batch_op.f('ix_mentorship_sessions_mentor_id'))
        batch_op.drop_index(batch_op.f('ix_mentorship_sessions_mentee_id'))
        batch_op.alter_column('mentee_feedback',
               existing_type=sa.JSON(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('mentor_feedback',
               existing_type=sa.JSON(),
               type_=sa.TEXT(),
               existing_nullable=True)
        batch_op.alter_column('status',
               existing_type=sa.Enum('SCHEDULED', 'COMPLETED', 'CANCELLED', 'RESCHEDULED', name='sessionstatus'),
               type_=sa.VARCHAR(length=20),
               existing_nullable=True)
        batch_op.alter_column('mentor_id',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=36),
               existing_nullable=False)
        batch_op.alter_column('mentee_id',
               existing_type=sa.String(length=100),
               type_=sa.VARCHAR(length=36),
               existing_nullable=False)
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('meta_data')

    with op.batch_alter_table('credit_redemptions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('credit_redemptions_created_by_fkey', 'users', ['created_by'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('credit_pools', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('credit_pools_owner_id_fkey', 'users', ['owner_id'], ['id'], ondelete='CASCADE')

    op.create_table('mytable',
    sa.Column('uuid', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('data', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('uuid', name='mytable_pkey')
    )
    op.create_table('mentor_profiles',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('application_status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('application_submitted_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('profile_data', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='mentor_profiles_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='mentor_profiles_pkey')
    )
    # ### end Alembic commands ###
