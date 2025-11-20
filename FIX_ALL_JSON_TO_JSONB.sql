-- ============================================================================
-- COMPREHENSIVE FIX: Convert ALL JSON columns to JSONB
-- ============================================================================
-- This script fixes the datatype mismatch errors by converting all JSON
-- columns to JSONB across all tables
-- ============================================================================
-- Run this in your Render PostgreSQL database shell
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. USERS TABLE - Fix skills column
-- ============================================================================

-- Drop and recreate skills column as JSONB
ALTER TABLE users DROP COLUMN IF EXISTS skills CASCADE;
ALTER TABLE users ADD COLUMN skills JSONB DEFAULT '[]'::jsonb NOT NULL;

-- ============================================================================
-- 2. JOB_SEARCH_CONFIG TABLE - Fix all JSON arrays
-- ============================================================================

-- Only run if table exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'job_search_config') THEN
        -- Fix job_titles
        ALTER TABLE job_search_config DROP COLUMN IF EXISTS job_titles CASCADE;
        ALTER TABLE job_search_config ADD COLUMN job_titles JSONB DEFAULT '[]'::jsonb;

        -- Fix locations
        ALTER TABLE job_search_config DROP COLUMN IF EXISTS locations CASCADE;
        ALTER TABLE job_search_config ADD COLUMN locations JSONB DEFAULT '[]'::jsonb;

        -- Fix keywords
        ALTER TABLE job_search_config DROP COLUMN IF EXISTS keywords CASCADE;
        ALTER TABLE job_search_config ADD COLUMN keywords JSONB DEFAULT '[]'::jsonb;

        -- Fix exclude_keywords
        ALTER TABLE job_search_config DROP COLUMN IF EXISTS exclude_keywords CASCADE;
        ALTER TABLE job_search_config ADD COLUMN exclude_keywords JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- ============================================================================
-- 3. AUTOMATION_LOGS TABLE - Fix details column
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'automation_logs') THEN
        ALTER TABLE automation_logs DROP COLUMN IF EXISTS details CASCADE;
        ALTER TABLE automation_logs ADD COLUMN details JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- ============================================================================
-- 4. ACTIVITY_LOGS TABLE - Fix changes column
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'activity_logs') THEN
        ALTER TABLE activity_logs DROP COLUMN IF EXISTS changes CASCADE;
        ALTER TABLE activity_logs ADD COLUMN changes JSONB DEFAULT '{}'::jsonb;
    END IF;
END $$;

-- ============================================================================
-- 5. SETTINGS TABLE - Fix allowed_file_types column
-- ============================================================================

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'settings') THEN
        ALTER TABLE settings DROP COLUMN IF EXISTS allowed_file_types CASCADE;
        ALTER TABLE settings ADD COLUMN allowed_file_types JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

SELECT '============================================================' as separator;
SELECT '✓ JSON TO JSONB CONVERSION VERIFICATION' as status;
SELECT '============================================================' as separator;

-- Check users.skills
SELECT
    'users.skills' as column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'skills';

-- Check job_search_config JSON columns
SELECT
    'job_search_config.' || column_name as column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'job_search_config'
AND column_name IN ('job_titles', 'locations', 'keywords', 'exclude_keywords')
ORDER BY column_name;

-- Check automation_logs.details
SELECT
    'automation_logs.details' as column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'automation_logs' AND column_name = 'details';

-- Check activity_logs.changes
SELECT
    'activity_logs.changes' as column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'activity_logs' AND column_name = 'changes';

-- Check settings.allowed_file_types
SELECT
    'settings.allowed_file_types' as column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'settings' AND column_name = 'allowed_file_types';

SELECT '============================================================' as separator;
SELECT '✓ ALL JSON COLUMNS CONVERTED TO JSONB!' as final_status;
SELECT '============================================================' as separator;

-- ============================================================================
-- EXPECTED RESULTS:
-- All columns should show:
-- - data_type: jsonb
-- - column_default: '[]'::jsonb or '{}'::jsonb
-- ============================================================================
