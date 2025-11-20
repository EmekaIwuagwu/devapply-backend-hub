-- ============================================================================
-- COMPREHENSIVE FIX: Platform Credentials Column Name Mismatches
-- Run this SQL in your PostgreSQL database to fix all column naming issues
-- ============================================================================

BEGIN;

-- ============================================================================
-- ISSUE 1: Fix last_verified vs last_verified_at
-- ============================================================================

DO $$
BEGIN
    -- Check if last_verified exists and rename it
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'last_verified'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN last_verified TO last_verified_at;

        RAISE NOTICE '✓ Renamed last_verified to last_verified_at';
    ELSE
        RAISE NOTICE '  last_verified_at column already exists or last_verified not found';
    END IF;
END $$;

-- ============================================================================
-- ISSUE 2: Fix is_active column (set default and update nulls)
-- ============================================================================

DO $$
BEGIN
    -- Check if is_active column exists
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'is_active'
    ) THEN
        -- Set default value
        ALTER TABLE platform_credentials
        ALTER COLUMN is_active SET DEFAULT true;

        -- Update existing NULL values
        UPDATE platform_credentials
        SET is_active = true
        WHERE is_active IS NULL;

        -- Optionally rename to is_verified (to match model)
        -- Uncomment the next line if you want to use is_verified instead
        -- ALTER TABLE platform_credentials RENAME COLUMN is_active TO is_verified;

        RAISE NOTICE '✓ Set is_active default to true and updated NULL values';
    END IF;

    -- Check if we should use is_verified instead
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'is_verified'
    ) THEN
        RAISE NOTICE '  is_verified column exists (good!)';
    END IF;
END $$;

-- ============================================================================
-- ISSUE 3: Fix password vs encrypted_password
-- ============================================================================

DO $$
BEGIN
    -- Check if 'password' column exists and rename it
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'password'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN password TO encrypted_password;

        RAISE NOTICE '✓ Renamed password to encrypted_password';
    ELSE
        RAISE NOTICE '  encrypted_password column already exists or password not found';
    END IF;

    -- Ensure encrypted_password is NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials'
        AND column_name = 'encrypted_password'
    ) THEN
        ALTER TABLE platform_credentials
        ALTER COLUMN encrypted_password SET NOT NULL;

        RAISE NOTICE '✓ Set encrypted_password to NOT NULL';
    END IF;
END $$;

-- ============================================================================
-- ADDITIONAL FIXES: Ensure all expected columns exist
-- ============================================================================

DO $$
BEGIN
    -- Add username_encrypted if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'username_encrypted'
    ) THEN
        -- Check if there's a username column to migrate
        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'platform_credentials' AND column_name = 'username'
        ) THEN
            -- Rename existing username to username_encrypted
            ALTER TABLE platform_credentials
            RENAME COLUMN username TO username_encrypted;

            RAISE NOTICE '✓ Renamed username to username_encrypted';
        ELSE
            -- Create new column
            ALTER TABLE platform_credentials
            ADD COLUMN username_encrypted TEXT;

            RAISE NOTICE '✓ Added username_encrypted column';
        END IF;
    END IF;

    -- Add is_verified if it doesn't exist and we're not using is_active
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

            RAISE NOTICE '✓ Added is_verified column and copied data from is_active';
        ELSE
            RAISE NOTICE '✓ Added is_verified column';
        END IF;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION: Check final column structure
-- ============================================================================

SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;

-- ============================================================================
-- EXPECTED FINAL STRUCTURE:
-- ============================================================================
-- id                    VARCHAR(36)     NOT NULL
-- user_id               VARCHAR(36)     NOT NULL
-- platform              VARCHAR(50)     NOT NULL
-- username_encrypted    TEXT            NULL
-- encrypted_password    TEXT            NOT NULL
-- is_verified           BOOLEAN         DEFAULT false
-- last_verified_at      TIMESTAMP       NULL
-- created_at            TIMESTAMP       DEFAULT now()
-- updated_at            TIMESTAMP       DEFAULT now()
-- ============================================================================
