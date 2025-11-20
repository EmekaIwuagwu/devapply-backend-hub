# Complete Database Migration Guide

## Prerequisites

You need to install all Python dependencies before running migrations.

---

## Method 1: Run Flask Migration (Recommended)

### Step 1: Install Dependencies

```powershell
# Make sure you're in the project directory
cd C:\Users\HP\Desktop\devapply-backend-hub

# Install all requirements
pip install -r requirements.txt
```

This will install:
- Flask-SQLAlchemy
- Flask-Migrate
- All other dependencies

### Step 2: Set Database URL

```powershell
# Set your PostgreSQL database URL
$env:DATABASE_URL="postgresql://user:password@host:port/database"

# Example for Render:
# $env:DATABASE_URL="postgresql://devapply_user:password@dpg-xxxxx-a.oregon-postgres.render.com:5432/devapply_db"
```

### Step 3: Run All Migrations

```powershell
# This will run ALL pending migrations in order
flask db upgrade
```

This will apply:
1. `20251115_072114_add_user_verification_preferences.py`
2. `20251120_061515_add_admin_features.py`
3. `20251120_130652_fix_platform_credentials_columns.py`

### Step 4: Verify Success

```powershell
# Check migration status
flask db current

# List all tables
flask db history
```

---

## Method 2: Run SQL Files Directly (Alternative)

If you can't install Python dependencies or prefer SQL:

### Step 1: Access Your Database

**Option A: Using psql (if installed)**
```powershell
# Install PostgreSQL client tools if needed
# Download from: https://www.postgresql.org/download/windows/

# Connect to database
psql "postgresql://user:password@host:port/database"
```

**Option B: Use Render Dashboard**
1. Go to Render Dashboard
2. Navigate to your PostgreSQL service
3. Click "Shell" tab
4. You'll get a psql prompt

### Step 2: Run SQL Files in Order

**File 1: Main Schema** (if not already created)
```sql
-- Copy and paste contents of: database_schema.sql
-- This creates all base tables
```

**File 2: Add Role Column**
```sql
-- Copy and paste contents of: HOTFIX_add_role_column.sql
ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user' NOT NULL;
CREATE INDEX ix_users_role ON users(role);
```

**File 3: Fix Platform Credentials**
```sql
-- Copy and paste contents of: HOTFIX_COMPREHENSIVE_platform_credentials.sql
-- This fixes all column name mismatches
```

---

## Method 3: Quick Single SQL Script (Fastest)

I'll create one complete SQL file that does everything:

### Copy This Complete SQL:

```sql
-- ============================================================================
-- COMPLETE DATABASE MIGRATION - Run Everything
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

RAISE NOTICE '✓ Created admin tables (videos, settings, activity_logs)';

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

        RAISE NOTICE '✓ Fixed is_active column';
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
    END IF;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'platform_credentials' AND column_name = 'encrypted_password'
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

        IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'platform_credentials' AND column_name = 'is_active'
        ) THEN
            UPDATE platform_credentials
            SET is_verified = is_active;
            RAISE NOTICE '✓ Added is_verified column';
        END IF;
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Check users table has role
SELECT 'USERS TABLE:' as check_name;
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'role';

-- Check admin tables exist
SELECT 'ADMIN TABLES:' as check_name;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('videos', 'settings', 'activity_logs')
ORDER BY table_name;

-- Check platform_credentials structure
SELECT 'PLATFORM_CREDENTIALS COLUMNS:' as check_name;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;

-- Summary
SELECT 'MIGRATION COMPLETE!' as status;
```

### Step 3: Run in Database

**Using Render Shell:**
1. Go to Render Dashboard → Database → Shell
2. Copy the entire SQL above
3. Paste and press Enter
4. Check for success messages

**Using psql:**
```powershell
psql $DATABASE_URL
# Then paste the SQL
```

---

## Method 4: Use Python Script (If pip install fails)

If you can't install dependencies, create a simple script:

```python
# run_migration.py
import psycopg2
import os

# Set your database URL
DATABASE_URL = "postgresql://user:password@host:port/database"

# Read SQL file
with open('COMPLETE_MIGRATION.sql', 'r') as f:
    sql = f.read()

# Connect and execute
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
cur.execute(sql)
conn.commit()
print("✓ Migration complete!")
```

Run it:
```powershell
pip install psycopg2-binary
python run_migration.py
```

---

## Troubleshooting

### Error: "No module named 'flask_sqlalchemy'"

```powershell
pip install flask-sqlalchemy flask-migrate
```

### Error: "pip not found"

```powershell
# Use python -m pip instead
python -m pip install -r requirements.txt
```

### Error: "Access denied"

Make sure your DATABASE_URL is correct:
```powershell
# Test connection
psql $DATABASE_URL
```

### Error: "flask: command not found"

```powershell
# Use python -m flask instead
python -m flask db upgrade
```

---

## Recommended: Method 1 (Flask Migration)

**This is the cleanest approach:**

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set database URL
$env:DATABASE_URL="your_database_url_here"

# 3. Run migrations
flask db upgrade

# Done! ✓
```

---

## After Migration Success

Verify everything worked:

```sql
-- Count tables
SELECT COUNT(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
-- Should return 15+ tables

-- Check users.role exists
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'role';
-- Should return 'role'

-- Check platform_credentials columns
SELECT column_name FROM information_schema.columns
WHERE table_name = 'platform_credentials'
  AND column_name IN ('encrypted_password', 'username_encrypted', 'is_verified', 'last_verified_at');
-- Should return all 4 columns
```

---

**Which method do you prefer?** I recommend Method 1 (Flask Migration) if you can install dependencies, or Method 3 (Single SQL) if you want to run SQL directly.
