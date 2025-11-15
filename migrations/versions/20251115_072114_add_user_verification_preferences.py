"""Add user email verification, password reset, and preferences

Revision ID: 20251115_072114
Revises:
Create Date: 2025-11-15 07:21:14

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251115_072114'
down_revision = None  # Set this to the previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to users table
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('email_verification_sent_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_sent_at', sa.DateTime(), nullable=True))

    # Create unique indexes
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'], unique=True)
    op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'], unique=True)

    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('daily_summary_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('application_updates_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('job_matches_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('marketing_emails_enabled', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('auto_apply_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('max_applications_per_day', sa.Integer(), nullable=True, server_default='20'),
        sa.Column('min_match_score', sa.Integer(), nullable=True, server_default='70'),
        sa.Column('timezone', sa.String(length=50), nullable=True, server_default='UTC'),
        sa.Column('language', sa.String(length=10), nullable=True, server_default='en'),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'], unique=True)


def downgrade():
    # Drop user_preferences table
    op.drop_index('ix_user_preferences_user_id', table_name='user_preferences')
    op.drop_table('user_preferences')

    # Drop indexes
    op.drop_index('ix_users_password_reset_token', table_name='users')
    op.drop_index('ix_users_email_verification_token', table_name='users')

    # Remove columns from users table
    op.drop_column('users', 'password_reset_sent_at')
    op.drop_column('users', 'password_reset_token')
    op.drop_column('users', 'email_verification_sent_at')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')
