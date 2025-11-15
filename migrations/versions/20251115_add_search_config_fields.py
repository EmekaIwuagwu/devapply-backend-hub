"""Add missing fields to job search config

Revision ID: 20251115_add_search_config_fields
Revises: 20251115_072114_add_user_verification_preferences
Create Date: 2025-11-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251115_add_search_config_fields'
down_revision = '20251115_072114_add_user_verification_preferences'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to job_search_configs table
    op.add_column('job_search_configs', sa.Column('config_name', sa.String(length=255), nullable=True))
    op.add_column('job_search_configs', sa.Column('primary_job_type', sa.String(length=50), nullable=True))
    op.add_column('job_search_configs', sa.Column('primary_max_salary', sa.Integer(), nullable=True))
    op.add_column('job_search_configs', sa.Column('primary_remote_preference', sa.String(length=50), nullable=True))
    op.add_column('job_search_configs', sa.Column('secondary_job_type', sa.String(length=50), nullable=True))
    op.add_column('job_search_configs', sa.Column('secondary_max_salary', sa.Integer(), nullable=True))
    op.add_column('job_search_configs', sa.Column('secondary_remote_preference', sa.String(length=50), nullable=True))


def downgrade():
    # Remove added columns
    op.drop_column('job_search_configs', 'secondary_remote_preference')
    op.drop_column('job_search_configs', 'secondary_max_salary')
    op.drop_column('job_search_configs', 'secondary_job_type')
    op.drop_column('job_search_configs', 'primary_remote_preference')
    op.drop_column('job_search_configs', 'primary_max_salary')
    op.drop_column('job_search_configs', 'primary_job_type')
    op.drop_column('job_search_configs', 'config_name')
