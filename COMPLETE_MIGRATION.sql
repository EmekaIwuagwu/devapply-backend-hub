-- ============================================================================
-- COMPLETE DATABASE MIGRATION - Run Everything At Once
-- ============================================================================
-- This script applies ALL pending migrations:
-- 1. Adds role column to users table
-- 2. Creates admin tables (videos, settings, activity_logs)
-- 3. Fixes platform_credentials column names
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Add role column to users (if not exists)
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;
        CREATE INDEX ix_users_role ON users(role);
        RAISE NOTICE '✓ Added role column to users';
    ELSE
        RAISE NOTICE '  Role column already exists';
    END IF;
END $$;

-- ============================================================================
-- STEP 2: Create admin tables (if not exist)
-- ============================================================================

-- Videos table
CREATE TABLE IF NOT EXISTS videos (
    id VARCHAR(36) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_base64 TEXT NOT NULL,
    thumbnail_base64 TEXT,
    file_size INTEGER,
    duration INTEGER,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    view_count INTEGER DEFAULT 0,
    uploaded_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_videos_created_at ON videos(created_at);
CREATE INDEX IF NOT EXISTS ix_videos_category ON videos(category);

-- Settings table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    site_name VARCHAR(255) DEFAULT 'DevApply',
    site_description TEXT,
    contact_email VARCHAR(255),
    support_phone VARCHAR(20),
    logo_base64 TEXT,
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    system_alerts_enabled BOOLEAN DEFAULT TRUE,
    admin_notification_email VARCHAR(255),
    low_balance_threshold INTEGER DEFAULT 100,
    session_timeout_minutes INTEGER DEFAULT 1440,
    max_login_attempts INTEGER DEFAULT 5,
    password_min_length INTEGER DEFAULT 8,
    require_email_verification BOOLEAN DEFAULT TRUE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    maintenance_mode BOOLEAN DEFAULT FALSE,
    maintenance_message TEXT,
    api_rate_limit_per_hour INTEGER DEFAULT 1000,
    max_file_upload_mb INTEGER DEFAULT 50,
    allowed_file_types JSON DEFAULT '[]',
    max_applications_per_user_per_day INTEGER DEFAULT 50,
    auto_cleanup_days INTEGER DEFAULT 90,
    linkedin_integration_enabled BOOLEAN DEFAULT TRUE,
    indeed_integration_enabled BOOLEAN DEFAULT TRUE,
    ai_matching_enabled BOOLEAN DEFAULT TRUE,
    video_tutorials_enabled BOOLEAN DEFAULT TRUE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(36),
    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT settings_singleton CHECK (id = 1)
);

INSERT INTO settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;

-- Activity Logs table
CREATE TABLE IF NOT EXISTS activity_logs (
    id VARCHAR(36) PRIMARY KEY,
    admin_id VARCHAR(36) NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id VARCHAR(36),
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    changes JSON DEFAULT '{}',
    status VARCHAR(20) DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS ix_activity_logs_admin_id ON activity_logs(admin_id);
CREATE INDEX IF NOT EXISTS ix_activity_logs_action ON activity_logs(action);
CREATE INDEX IF NOT EXISTS ix_activity_logs_created_at ON activity_logs(created_at);

DO $$
BEGIN
    RAISE NOTICE '✓ Created admin tables (videos, settings, activity_logs)';
END $$;

-- ============================================================================
-- STEP 3: Fix platform_credentials columns
-- ============================================================================

-- Fix 1: Rename last_verified to last_verified_at
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'last_verified'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN last_verified TO last_verified_at;
        RAISE NOTICE '✓ Renamed last_verified to last_verified_at';
    ELSE
        RAISE NOTICE '  last_verified_at already correct';
    END IF;
END $$;

-- Fix 2: Set default for is_active and update nulls
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

        RAISE NOTICE '✓ Fixed is_active column (set default and updated NULLs)';
    ELSE
        RAISE NOTICE '  is_active column not found (may not exist yet)';
    END IF;
END $$;

-- Fix 3: Rename password to encrypted_password
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'password'
    ) THEN
        ALTER TABLE platform_credentials
        RENAME COLUMN password TO encrypted_password;
        RAISE NOTICE '✓ Renamed password to encrypted_password';
    ELSE
        RAISE NOTICE '  encrypted_password already correct';
    END IF;

    -- Ensure encrypted_password is NOT NULL
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_password'
        AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE platform_credentials
        ALTER COLUMN encrypted_password SET NOT NULL;
        RAISE NOTICE '✓ Set encrypted_password to NOT NULL';
    END IF;
END $$;

-- Fix 4: Ensure username_encrypted exists
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
            RAISE NOTICE '✓ Renamed username to username_encrypted';
        ELSE
            ALTER TABLE platform_credentials
            ADD COLUMN username_encrypted TEXT;
            RAISE NOTICE '✓ Added username_encrypted column';
        END IF;
    ELSE
        RAISE NOTICE '  username_encrypted already correct';
    END IF;
END $$;

-- Fix 5: Add is_verified column
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
            SET is_verified = is_active
            WHERE is_verified IS NULL;
            RAISE NOTICE '✓ Added is_verified column and copied from is_active';
        ELSE
            RAISE NOTICE '✓ Added is_verified column';
        END IF;
    ELSE
        RAISE NOTICE '  is_verified already exists';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check users table has role
SELECT '=== USERS TABLE CHECK ===' as info;
SELECT column_name, data_type, column_default, is_nullable
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'role';

-- Check admin tables exist
SELECT '=== ADMIN TABLES CHECK ===' as info;
SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('videos', 'settings', 'activity_logs')
ORDER BY table_name;

-- Check platform_credentials structure
SELECT '=== PLATFORM_CREDENTIALS CHECK ===' as info;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;

-- Final count
SELECT '=== FINAL TABLE COUNT ===' as info;
SELECT COUNT(*) as total_tables
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

SELECT '=== ✓ MIGRATION COMPLETE! ===' as status;
