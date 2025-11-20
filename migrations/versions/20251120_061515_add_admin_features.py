"""Add admin features: Video, Settings, ActivityLog models and User role field

Revision ID: 20251120_061515
Revises: 20251115_072114
Create Date: 2025-11-20 06:15:15.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251120_061515'
down_revision = '20251115_072114'
branch_labels = None
depends_on = None


def upgrade():
    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=False, server_default='user'))
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Create videos table
    op.create_table('videos',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('video_base64', sa.Text(), nullable=False),
        sa.Column('thumbnail_base64', sa.Text(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=True),
        sa.Column('uploaded_by', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_videos_created_at'), 'videos', ['created_at'], unique=False)

    # Create settings table
    op.create_table('settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_name', sa.String(length=255), nullable=True),
        sa.Column('site_description', sa.Text(), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('support_phone', sa.String(length=20), nullable=True),
        sa.Column('logo_base64', sa.Text(), nullable=True),
        sa.Column('email_notifications_enabled', sa.Boolean(), nullable=True),
        sa.Column('system_alerts_enabled', sa.Boolean(), nullable=True),
        sa.Column('admin_notification_email', sa.String(length=255), nullable=True),
        sa.Column('low_balance_threshold', sa.Integer(), nullable=True),
        sa.Column('session_timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('max_login_attempts', sa.Integer(), nullable=True),
        sa.Column('password_min_length', sa.Integer(), nullable=True),
        sa.Column('require_email_verification', sa.Boolean(), nullable=True),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=True),
        sa.Column('maintenance_mode', sa.Boolean(), nullable=True),
        sa.Column('maintenance_message', sa.Text(), nullable=True),
        sa.Column('api_rate_limit_per_hour', sa.Integer(), nullable=True),
        sa.Column('max_file_upload_mb', sa.Integer(), nullable=True),
        sa.Column('allowed_file_types', sa.JSON(), nullable=True),
        sa.Column('max_applications_per_user_per_day', sa.Integer(), nullable=True),
        sa.Column('auto_cleanup_days', sa.Integer(), nullable=True),
        sa.Column('linkedin_integration_enabled', sa.Boolean(), nullable=True),
        sa.Column('indeed_integration_enabled', sa.Boolean(), nullable=True),
        sa.Column('ai_matching_enabled', sa.Boolean(), nullable=True),
        sa.Column('video_tutorials_enabled', sa.Boolean(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create activity_logs table
    op.create_table('activity_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('admin_id', sa.String(length=36), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.String(length=36), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_action'), 'activity_logs', ['action'], unique=False)
    op.create_index(op.f('ix_activity_logs_admin_id'), 'activity_logs', ['admin_id'], unique=False)
    op.create_index(op.f('ix_activity_logs_created_at'), 'activity_logs', ['created_at'], unique=False)


def downgrade():
    # Drop activity_logs table
    op.drop_index(op.f('ix_activity_logs_created_at'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_admin_id'), table_name='activity_logs')
    op.drop_index(op.f('ix_activity_logs_action'), table_name='activity_logs')
    op.drop_table('activity_logs')

    # Drop settings table
    op.drop_table('settings')

    # Drop videos table
    op.drop_index(op.f('ix_videos_created_at'), table_name='videos')
    op.drop_table('videos')

    # Remove role column from users table
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_column('users', 'role')
