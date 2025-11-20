# Platform Credentials Fix Guide

## Issues Identified

Your platform_credentials table has column name mismatches that prevent users from connecting their LinkedIn/Indeed accounts:

| Issue | Database Has | Backend Expects | Impact |
|-------|--------------|-----------------|--------|
| **Issue 1** | `last_verified` | `last_verified_at` | GET /api/credentials fails |
| **Issue 2** | `is_active` (no default) | `is_verified` | POST /api/credentials fails with NULL constraint |
| **Issue 3** | `password` | `encrypted_password` | POST /api/credentials fails with NULL constraint |

---

## Fix Options

### **Option 1: Direct SQL Fix (Fastest - Recommended for Production)**

Run this SQL directly in your Render database:

#### **Step 1: Access Your Database**

```bash
# Go to Render Dashboard > Your Database > Shell tab
# OR use psql:
psql postgresql://user:password@host:port/database
```

#### **Step 2: Copy and Paste This SQL**

```sql
-- ============================================================================
-- COMPREHENSIVE FIX: Platform Credentials Column Name Mismatches
-- ============================================================================

BEGIN;

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

        RAISE NOTICE '✓ Set is_active default and updated NULL values';
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

    -- Ensure encrypted_password is NOT NULL
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

-- Fix 5: Add is_verified column (backend uses this)
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
            RAISE NOTICE '✓ Added is_verified and copied from is_active';
        END IF;
    END IF;
END $$;

COMMIT;

-- Verify the fixes
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;
```

#### **Step 3: Verify Success**

You should see output showing all columns are now correctly named:

```
column_name         | data_type | is_nullable | column_default
--------------------|-----------|-------------|---------------
id                  | text      | NO          |
user_id             | text      | NO          |
platform            | text      | NO          |
username_encrypted  | text      | YES         |
encrypted_password  | text      | NO          |
is_verified         | boolean   | YES         | false
last_verified_at    | timestamp | YES         |
created_at          | timestamp | YES         | now()
updated_at          | timestamp | YES         | now()
```

---

### **Option 2: Flask Migration (For Development/Staging)**

If you have access to run Flask commands:

#### **Step 1: Pull Latest Code**

```bash
git pull origin claude/devapply-backend-setup-01KPhFDUoudY1C8VZoq9Bc8W
```

#### **Step 2: Run Migration**

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run the migration
flask db upgrade
```

This will apply migration `20251120_130652_fix_platform_credentials_columns.py`

---

## Testing the Fix

After applying either fix, test the credentials endpoint:

### **Test 1: Add LinkedIn Credentials**

```bash
curl -X POST https://your-backend.onrender.com/api/credentials \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "username": "your@email.com",
    "password": "your_password"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "credential": {
      "id": "...",
      "user_id": "...",
      "platform": "linkedin",
      "username": "your@email.com",
      "is_verified": false,
      "last_verified_at": null,
      "created_at": "2025-11-20T13:00:00.000000",
      "updated_at": "2025-11-20T13:00:00.000000"
    }
  },
  "message": "Credential added successfully"
}
```

### **Test 2: Get All Credentials**

```bash
curl -X GET https://your-backend.onrender.com/api/credentials \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "credentials": [
      {
        "id": "...",
        "platform": "linkedin",
        "username": "your@email.com",
        "is_verified": false
      }
    ]
  }
}
```

---

## Troubleshooting

### Error: "column still doesn't exist"

Check which columns actually exist:

```sql
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'platform_credentials'
ORDER BY ordinal_position;
```

Then manually rename the mismatched ones:

```sql
-- Example: If database has 'pwd' instead of 'encrypted_password'
ALTER TABLE platform_credentials RENAME COLUMN pwd TO encrypted_password;
```

### Error: "cannot drop column ... because other objects depend on it"

This means there are views or constraints. Drop them first:

```sql
-- Find dependent objects
SELECT *
FROM information_schema.constraint_column_usage
WHERE table_name = 'platform_credentials';

-- Drop constraint (example)
ALTER TABLE platform_credentials DROP CONSTRAINT constraint_name;
```

---

## Backend Code Changes

The backend model has been updated to match the corrected database schema:

### **PlatformCredential Model Changes**

```python
# OLD (mismatched)
username = db.Column(db.String(255), nullable=False)
password_encrypted = db.Column(db.Text, nullable=False)
is_active = db.Column(db.Boolean, default=True)

# NEW (correct)
username_encrypted = db.Column(db.Text)
encrypted_password = db.Column(db.Text, nullable=False)
is_verified = db.Column(db.Boolean, default=False)
last_verified_at = db.Column(db.DateTime)
```

### **New Methods Added**

- `set_username(username)` - Encrypts and stores username
- `get_username()` - Decrypts and returns username
- `set_password(password)` - Encrypts and stores password (updated)
- `get_password()` - Decrypts and returns password

---

## Files Updated

- ✅ `app/models/platform_credential.py` - Model updated
- ✅ `app/routes/credentials.py` - Routes updated to use new methods
- ✅ `app/tasks/job_applicator.py` - Tasks updated to use `get_username()`
- ✅ `migrations/versions/20251120_130652_fix_platform_credentials_columns.py` - Migration created
- ✅ `HOTFIX_COMPREHENSIVE_platform_credentials.sql` - Direct SQL fix

---

## After Applying the Fix

1. ✅ Restart your backend server on Render
2. ✅ Test credentials endpoints
3. ✅ Users should now be able to connect LinkedIn/Indeed accounts
4. ✅ Automation will be able to access encrypted credentials

---

## Quick Reference

**Files to use:**
- Production (SQL): `HOTFIX_COMPREHENSIVE_platform_credentials.sql`
- Development (Migration): `migrations/versions/20251120_130652_fix_platform_credentials_columns.py`

**Commands:**
- SQL: Copy-paste SQL into database shell
- Migration: `flask db upgrade`

**Priority:** CRITICAL - Blocks all platform connections

---

**Need Help?** Check the verification query results and compare with expected structure above.
