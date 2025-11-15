"""Initial database schema

Revision ID: 20251115_000000
Revises:
Create Date: 2025-11-15 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251115_000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('github_url', sa.String(length=500), nullable=True),
        sa.Column('portfolio_url', sa.String(length=500), nullable=True),
        sa.Column('current_role', sa.String(length=255), nullable=True),
        sa.Column('years_experience', sa.Integer(), nullable=True),
        sa.Column('preferred_job_type', sa.String(length=50), nullable=True),
        sa.Column('salary_expectations', sa.String(length=100), nullable=True),
        sa.Column('professional_bio', sa.Text(), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('avatar_base64', sa.Text(), nullable=True),
        sa.Column('oauth_provider', sa.String(length=50), nullable=True),
        sa.Column('oauth_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_oauth_provider_oauth_id', 'users', ['oauth_provider', 'oauth_id'], unique=False)

    # Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('plan_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('applications_limit', sa.Integer(), nullable=True),
        sa.Column('applications_used', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('billing_cycle', sa.String(length=20), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('next_billing_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'], unique=False)

    # Create payments table
    op.create_table(
        'payments',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('subscription_id', sa.String(length=36), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='USD'),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', sa.String(length=255), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='SET NULL')
    )
    op.create_index('ix_payments_user_id', 'payments', ['user_id'], unique=False)

    # Create resumes table
    op.create_table(
        'resumes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_base64', sa.Text(), nullable=False),
        sa.Column('file_type', sa.String(length=10), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('job_type_tag', sa.String(length=100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'], unique=False)

    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('job_type', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('salary_range', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='sent'),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('job_url', sa.String(length=1000), nullable=True),
        sa.Column('resume_used_id', sa.String(length=36), nullable=True),
        sa.Column('cover_letter', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('last_status_update', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resume_used_id'], ['resumes.id'], ondelete='SET NULL')
    )
    op.create_index('ix_applications_user_id', 'applications', ['user_id'], unique=False)
    op.create_index('ix_applications_platform', 'applications', ['platform'], unique=False)
    op.create_index('ix_applications_status', 'applications', ['status'], unique=False)

    # Create platform_credentials table
    op.create_table(
        'platform_credentials',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('encrypted_password', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_verified', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'platform', name='uq_user_platform')
    )
    op.create_index('ix_platform_credentials_user_id', 'platform_credentials', ['user_id'], unique=False)

    # Create job_search_configs table
    op.create_table(
        'job_search_configs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('platforms', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('primary_job_title', sa.String(length=255), nullable=True),
        sa.Column('primary_location', sa.String(length=255), nullable=True),
        sa.Column('primary_min_salary', sa.Integer(), nullable=True),
        sa.Column('primary_experience_level', sa.String(length=50), nullable=True),
        sa.Column('primary_keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('primary_resume_id', sa.String(length=36), nullable=True),
        sa.Column('secondary_job_title', sa.String(length=255), nullable=True),
        sa.Column('secondary_location', sa.String(length=255), nullable=True),
        sa.Column('secondary_min_salary', sa.Integer(), nullable=True),
        sa.Column('secondary_experience_level', sa.String(length=50), nullable=True),
        sa.Column('secondary_keywords', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('secondary_resume_id', sa.String(length=36), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['primary_resume_id'], ['resumes.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['secondary_resume_id'], ['resumes.id'], ondelete='SET NULL')
    )
    op.create_index('ix_job_search_configs_user_id', 'job_search_configs', ['user_id'], unique=False)

    # Create platforms table
    op.create_table(
        'platforms',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_popular', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('requires_credentials', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index('ix_platforms_code', 'platforms', ['code'], unique=True)

    # Create job_listings table
    op.create_table(
        'job_listings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('salary_min', sa.Integer(), nullable=True),
        sa.Column('salary_max', sa.Integer(), nullable=True),
        sa.Column('job_type', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('job_url', sa.String(length=1000), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('scraped_at', sa.DateTime(), nullable=True),
        sa.Column('posted_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('platform', 'external_id', name='uq_platform_external_id')
    )
    op.create_index('ix_job_listings_platform', 'job_listings', ['platform'], unique=False)

    # Create job_queue table
    op.create_table(
        'job_queue',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('job_search_config_id', sa.String(length=36), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('job_listing_id', sa.String(length=36), nullable=True),
        sa.Column('company_name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=False),
        sa.Column('job_url', sa.String(length=1000), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('priority', sa.Integer(), nullable=True, server_default='5'),
        sa.Column('match_score', sa.Integer(), nullable=True),
        sa.Column('scheduled_for', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_search_config_id'], ['job_search_configs.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['job_listing_id'], ['job_listings.id'], ondelete='SET NULL')
    )
    op.create_index('ix_job_queue_user_id', 'job_queue', ['user_id'], unique=False)
    op.create_index('ix_job_queue_status', 'job_queue', ['status'], unique=False)

    # Create automation_logs table
    op.create_table(
        'automation_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('job_queue_id', sa.String(length=36), nullable=True),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['job_queue_id'], ['job_queue.id'], ondelete='SET NULL')
    )
    op.create_index('ix_automation_logs_user_id', 'automation_logs', ['user_id'], unique=False)
    op.create_index('ix_automation_logs_action_type', 'automation_logs', ['action_type'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index('ix_automation_logs_action_type', table_name='automation_logs')
    op.drop_index('ix_automation_logs_user_id', table_name='automation_logs')
    op.drop_table('automation_logs')

    op.drop_index('ix_job_queue_status', table_name='job_queue')
    op.drop_index('ix_job_queue_user_id', table_name='job_queue')
    op.drop_table('job_queue')

    op.drop_index('ix_job_listings_platform', table_name='job_listings')
    op.drop_table('job_listings')

    op.drop_index('ix_platforms_code', table_name='platforms')
    op.drop_table('platforms')

    op.drop_index('ix_job_search_configs_user_id', table_name='job_search_configs')
    op.drop_table('job_search_configs')

    op.drop_index('ix_platform_credentials_user_id', table_name='platform_credentials')
    op.drop_table('platform_credentials')

    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_platform', table_name='applications')
    op.drop_index('ix_applications_user_id', table_name='applications')
    op.drop_table('applications')

    op.drop_index('ix_resumes_user_id', table_name='resumes')
    op.drop_table('resumes')

    op.drop_index('ix_payments_user_id', table_name='payments')
    op.drop_table('payments')

    op.drop_index('ix_subscriptions_user_id', table_name='subscriptions')
    op.drop_table('subscriptions')

    op.drop_index('ix_users_oauth_provider_oauth_id', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
