-- ============================================================================
-- HOTFIX: Fix platform_credentials table column names
-- This fixes the mismatch between model and database schema
-- ============================================================================

BEGIN;

-- Check current column names in platform_credentials table
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;

-- Option 1: If database has 'encrypted_password' and 'encrypted_username'
-- Rename them to match the model

DO $$
BEGIN
    -- Rename encrypted_password to password_encrypted (if it exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_password'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN encrypted_password TO password_encrypted;
        RAISE NOTICE 'Renamed encrypted_password to password_encrypted';
    END IF;

    -- Rename encrypted_username to username_encrypted (if it exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_username'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN encrypted_username TO username_encrypted;
        RAISE NOTICE 'Renamed encrypted_username to username_encrypted';
    END IF;

    -- Check if username column exists and is not nullable
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials'
        AND column_name = 'username'
        AND is_nullable = 'YES'
    ) THEN
        -- Make username nullable temporarily (model doesn't use it as encrypted)
        ALTER TABLE platform_credentials ALTER COLUMN username DROP NOT NULL;
        RAISE NOTICE 'Made username column nullable';
    END IF;

    -- Add username_encrypted if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'username_encrypted'
    ) THEN
        ALTER TABLE platform_credentials ADD COLUMN username_encrypted TEXT;
        RAISE NOTICE 'Added username_encrypted column';
    END IF;

    -- Make password_encrypted NOT NULL if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'password_encrypted'
    ) THEN
        ALTER TABLE platform_credentials ALTER COLUMN password_encrypted SET NOT NULL;
        RAISE NOTICE 'Set password_encrypted to NOT NULL';
    END IF;

    -- Add is_verified column if missing (model uses is_verified instead of is_active in DB)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'is_verified'
    ) THEN
        ALTER TABLE platform_credentials ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_verified column';
    END IF;

END $$;

COMMIT;

-- Verify final structure
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;
