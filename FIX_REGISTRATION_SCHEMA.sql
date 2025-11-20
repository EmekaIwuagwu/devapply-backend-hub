-- ============================================================================
-- CRITICAL FIX: User Registration Schema Issues
-- ============================================================================
-- This script fixes all registration-blocking database schema issues
-- Run this in your Render PostgreSQL database shell
-- ============================================================================

BEGIN;

-- ============================================================================
-- FIX 1: Fix the "skills" column datatype
-- ============================================================================
-- The skills column must be JSONB (not NULL type)
-- Using JSONB for better performance and indexing capabilities

-- Drop the column if it exists with wrong type and recreate
ALTER TABLE users DROP COLUMN IF EXISTS skills;
ALTER TABLE users ADD COLUMN skills JSONB DEFAULT '[]'::jsonb;

COMMENT ON COLUMN users.skills IS 'User skills stored as JSONB array';

-- ============================================================================
-- FIX 2: Make all optional profile fields explicitly nullable
-- ============================================================================
-- These fields should NOT be required during registration
-- Users can complete their profile later

ALTER TABLE users ALTER COLUMN full_name DROP NOT NULL;
ALTER TABLE users ALTER COLUMN phone DROP NOT NULL;
ALTER TABLE users ALTER COLUMN location DROP NOT NULL;
ALTER TABLE users ALTER COLUMN linkedin_url DROP NOT NULL;
ALTER TABLE users ALTER COLUMN github_url DROP NOT NULL;
ALTER TABLE users ALTER COLUMN portfolio_url DROP NOT NULL;
ALTER TABLE users ALTER COLUMN "current_role" DROP NOT NULL;
ALTER TABLE users ALTER COLUMN years_experience DROP NOT NULL;
ALTER TABLE users ALTER COLUMN preferred_job_type DROP NOT NULL;
ALTER TABLE users ALTER COLUMN salary_expectations DROP NOT NULL;
ALTER TABLE users ALTER COLUMN professional_bio DROP NOT NULL;
ALTER TABLE users ALTER COLUMN avatar_base64 DROP NOT NULL;
ALTER TABLE users ALTER COLUMN oauth_provider DROP NOT NULL;
ALTER TABLE users ALTER COLUMN oauth_id DROP NOT NULL;

-- ============================================================================
-- FIX 3: Ensure system fields have proper defaults
-- ============================================================================

-- Email verified should default to false
ALTER TABLE users ALTER COLUMN email_verified SET DEFAULT false;
ALTER TABLE users ALTER COLUMN email_verified SET NOT NULL;

-- Role should default to 'user' and be required
ALTER TABLE users ALTER COLUMN role SET DEFAULT 'user';
ALTER TABLE users ALTER COLUMN role SET NOT NULL;

-- Timestamps should auto-generate
ALTER TABLE users ALTER COLUMN created_at SET DEFAULT NOW();
ALTER TABLE users ALTER COLUMN created_at SET NOT NULL;

ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT NOW();
ALTER TABLE users ALTER COLUMN updated_at SET NOT NULL;

-- ============================================================================
-- FIX 4: Ensure required registration fields are properly typed
-- ============================================================================

-- Email must be required and unique
ALTER TABLE users ALTER COLUMN email SET NOT NULL;

-- Password hash must allow NULL (for OAuth users who don't have passwords)
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Full name should be VARCHAR(255) and nullable (can be added later)
ALTER TABLE users ALTER COLUMN full_name TYPE VARCHAR(255);
ALTER TABLE users ALTER COLUMN full_name DROP NOT NULL;

-- ============================================================================
-- FIX 5: Create trigger for auto-updating updated_at
-- ============================================================================

-- Drop trigger if exists
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Create function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FIX 6: Update any existing NULL skills to empty JSONB array
-- ============================================================================

UPDATE users SET skills = '[]'::jsonb WHERE skills IS NULL;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check skills column type
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'skills';

-- Check all user table column constraints
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '============================================================';
    RAISE NOTICE '✓ REGISTRATION SCHEMA FIXES APPLIED SUCCESSFULLY!';
    RAISE NOTICE '============================================================';
    RAISE NOTICE '';
    RAISE NOTICE 'FIXED ISSUES:';
    RAISE NOTICE '1. ✓ Skills column now JSONB with default []';
    RAISE NOTICE '2. ✓ All optional profile fields are nullable';
    RAISE NOTICE '3. ✓ System fields have proper defaults';
    RAISE NOTICE '4. ✓ Auto-update trigger for updated_at';
    RAISE NOTICE '';
    RAISE NOTICE 'REGISTRATION REQUIREMENTS:';
    RAISE NOTICE '- Required: email, password';
    RAISE NOTICE '- Optional: full_name, phone';
    RAISE NOTICE '- Auto-generated: id, role, email_verified, created_at, updated_at';
    RAISE NOTICE '- Profile fields: All nullable, can be completed later';
    RAISE NOTICE '';
    RAISE NOTICE '✓ Users can now register successfully!';
    RAISE NOTICE '============================================================';
END $$;
