"""Add cookies_encrypted field to platform_credentials

Revision ID: 20251122_add_cookies
Revises: 20251120_130652
Create Date: 2025-11-22 06:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251122_add_cookies'
down_revision = '20251120_130652'
branch_labels = None
depends_on = None


def upgrade():
    # Add cookies_encrypted column to platform_credentials table
    op.add_column('platform_credentials', sa.Column('cookies_encrypted', sa.Text(), nullable=True))


def downgrade():
    # Remove cookies_encrypted column
    op.drop_column('platform_credentials', 'cookies_encrypted')
