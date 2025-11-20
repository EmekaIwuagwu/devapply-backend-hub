"""Fix platform_credentials column names

Revision ID: 20251120_130652
Revises: 20251120_061515
Create Date: 2025-11-20 13:06:52.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251120_130652'
down_revision = '20251120_061515'
branch_labels = None
depends_on = None


def upgrade():
    """Fix platform_credentials column name mismatches"""

    # Use raw SQL to safely rename columns
    connection = op.get_bind()

    # Issue 1: Rename last_verified to last_verified_at (if exists)
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'last_verified'
            ) THEN
                ALTER TABLE platform_credentials
                RENAME COLUMN last_verified TO last_verified_at;
            END IF;
        END $$;
    """))

    # Issue 2: Set default for is_active and update nulls
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'is_active'
            ) THEN
                ALTER TABLE platform_credentials
                ALTER COLUMN is_active SET DEFAULT true;

                UPDATE platform_credentials
                SET is_active = true
                WHERE is_active IS NULL;
            END IF;
        END $$;
    """))

    # Issue 3: Rename password to encrypted_password (if exists)
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'password'
            ) THEN
                ALTER TABLE platform_credentials
                RENAME COLUMN password TO encrypted_password;
            END IF;

            -- Ensure encrypted_password is NOT NULL
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_password'
            ) THEN
                ALTER TABLE platform_credentials
                ALTER COLUMN encrypted_password SET NOT NULL;
            END IF;
        END $$;
    """))

    # Additional: Ensure username_encrypted exists
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'username_encrypted'
            ) THEN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'platform_credentials' AND column_name = 'username'
                ) THEN
                    ALTER TABLE platform_credentials
                    RENAME COLUMN username TO username_encrypted;
                ELSE
                    ALTER TABLE platform_credentials
                    ADD COLUMN username_encrypted TEXT;
                END IF;
            END IF;
        END $$;
    """))

    # Additional: Ensure is_verified exists (model uses this now)
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'is_verified'
            ) THEN
                ALTER TABLE platform_credentials
                ADD COLUMN is_verified BOOLEAN DEFAULT false;

                -- Copy data from is_active if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'platform_credentials' AND column_name = 'is_active'
                ) THEN
                    UPDATE platform_credentials
                    SET is_verified = is_active;
                END IF;
            END IF;
        END $$;
    """))


def downgrade():
    """Revert column name changes"""

    connection = op.get_bind()

    # Revert column renames
    connection.execute(sa.text("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'last_verified_at'
            ) THEN
                ALTER TABLE platform_credentials
                RENAME COLUMN last_verified_at TO last_verified;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_password'
            ) THEN
                ALTER TABLE platform_credentials
                RENAME COLUMN encrypted_password TO password;
            END IF;

            IF EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_credentials' AND column_name = 'username_encrypted'
            ) THEN
                ALTER TABLE platform_credentials
                RENAME COLUMN username_encrypted TO username;
            END IF;
        END $$;
    """))
