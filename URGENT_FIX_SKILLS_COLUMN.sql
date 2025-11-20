-- ============================================================================
-- URGENT FIX: Skills Column Type Mismatch
-- ============================================================================
-- Run this immediately in your Render PostgreSQL database shell
-- ============================================================================

BEGIN;

-- Drop the skills column completely and recreate with correct type
ALTER TABLE users DROP COLUMN IF EXISTS skills;

-- Add skills column as JSONB with proper default
ALTER TABLE users ADD COLUMN skills JSONB DEFAULT '[]'::jsonb NOT NULL;

-- Verify the change
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name = 'skills';

COMMIT;

-- ============================================================================
-- Expected Result:
-- column_name | data_type | is_nullable | column_default
-- skills      | jsonb     | NO          | '[]'::jsonb
-- ============================================================================

SELECT '✓ Skills column fixed! Type is now JSONB.' as status;
