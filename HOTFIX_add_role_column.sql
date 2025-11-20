-- ============================================================================
-- HOTFIX: Add role column to existing users table
-- Run this SQL in your Render database immediately
-- ============================================================================

BEGIN;

-- Add role column to users table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        -- Add the column
        ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;

        -- Create index for performance
        CREATE INDEX ix_users_role ON users(role);

        -- Set all existing users to 'user' role
        UPDATE users SET role = 'user' WHERE role IS NULL;

        RAISE NOTICE 'Successfully added role column to users table';
    ELSE
        RAISE NOTICE 'Role column already exists';
    END IF;
END $$;

COMMIT;

-- Verify it worked
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'role';

-- Check a sample user
SELECT id, email, role, created_at FROM users LIMIT 5;
