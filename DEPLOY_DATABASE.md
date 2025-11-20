# Deploy Database - Quick Start Guide

## 🎯 What This Does

The `FULL_DATABASE_SCHEMA_FIXED.sql` file creates your **complete DevApply database** with all 15 tables in one go.

---

## ✅ All Issues Fixed

✓ Reserved keyword `current_role` properly escaped
✓ Platform credentials columns corrected
✓ Admin features included (role, videos, settings, activity_logs)
✓ All foreign keys, indexes, and triggers configured
✓ Seed data included (LinkedIn, Indeed platforms)

---

## 🚀 Deployment Steps

### Step 1: Access Your Render Database

Go to **Render Dashboard** → Your PostgreSQL Service → **Shell** tab

### Step 2: Copy and Run SQL

```bash
# In the Render database shell, copy-paste the entire contents of:
FULL_DATABASE_SCHEMA_FIXED.sql
```

Press Enter and wait for execution to complete.

### Step 3: Verify Success

You should see output like:
```
✓ DATABASE SCHEMA CREATED SUCCESSFULLY!
TOTAL TABLES: 15
```

---

## 📊 What Gets Created

| Table | Purpose |
|-------|---------|
| users | User accounts (with role column) |
| user_preferences | User settings |
| platforms | Job platforms (LinkedIn, Indeed) |
| resumes | User resume storage |
| job_search_config | Job search preferences |
| subscriptions | User subscription plans |
| payments | Payment transactions |
| applications | Job applications tracking |
| job_listings | Scraped job listings |
| job_queue | Jobs queued for application |
| platform_credentials | Encrypted LinkedIn/Indeed credentials |
| automation_logs | Automation event logs |
| videos | Admin tutorial videos |
| settings | System-wide configuration (singleton) |
| activity_logs | Admin action audit trail |

---

## 🔐 Create First Admin User

After database is created, run:

```sql
-- Option 1: Create admin directly
INSERT INTO users (
    id,
    email,
    password_hash,
    full_name,
    role,
    email_verified,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid()::text,
    'admin@devapply.com',
    'SET_PASSWORD_HASH_HERE',  -- Use bcrypt hash
    'Admin User',
    'admin',
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Option 2: Upgrade existing user to admin
UPDATE users
SET role = 'admin', email_verified = true
WHERE email = 'your@email.com';
```

---

## 🧪 Test Admin Login

```bash
# Test admin authentication
curl -X POST https://devapply-backend.onrender.com/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@devapply.com",
    "password": "your_password"
  }'
```

Expected response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ...",
    "user": {
      "id": "...",
      "email": "admin@devapply.com",
      "role": "admin"
    }
  }
}
```

---

## 📝 Admin Endpoints Available

Once logged in, you can access:

**Dashboard:**
- `GET /api/admin/dashboard` - Statistics & analytics

**User Management:**
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/<id>` - View user details
- `PUT /api/admin/users/<id>` - Update user
- `POST /api/admin/users/<id>/send-email` - Send email to user

**Video Management:**
- `GET /api/admin/videos` - List videos
- `POST /api/admin/videos` - Upload video (max 50MB)
- `GET /api/admin/videos/<id>` - View video
- `DELETE /api/admin/videos/<id>` - Delete video

**Payment Management:**
- `GET /api/admin/payments` - List payments
- `GET /api/admin/payments/<id>` - View payment

**Settings:**
- `GET /api/admin/settings` - Get system settings
- `PUT /api/admin/settings` - Update settings
- `GET /api/admin/settings/logs` - View activity logs

---

## ⚠️ Important Notes

1. **Backup First**: If you have existing data, back it up before running this SQL
2. **One-Time Run**: This script uses `CREATE TABLE IF NOT EXISTS`, safe to run multiple times
3. **Admin Access**: Only users with `role = 'admin'` can access admin endpoints
4. **Rate Limiting**: Admin login is limited to 5 attempts per minute
5. **Activity Logging**: All admin actions are automatically logged

---

## 🔍 Troubleshooting

### Error: "relation already exists"
This is normal - the script uses `IF NOT EXISTS` and will skip existing tables.

### Error: "permission denied"
Ensure your database user has CREATE TABLE permissions.

### Error: "syntax error"
Ensure you copied the **entire** SQL file including BEGIN and COMMIT.

### Tables Not Created
Check the output for specific errors. Common issues:
- Connection timeout (try again)
- Insufficient permissions
- Database full (check Render plan limits)

---

## ✅ Success Indicators

After running the script, you should see:

```
============================================================
✓ DATABASE SCHEMA CREATED SUCCESSFULLY!
============================================================
TOTAL TABLES: 15

TABLE LIST:
activity_logs          10 columns
applications           11 columns
automation_logs         9 columns
job_listings           12 columns
job_queue              10 columns
job_search_config      11 columns
payments               10 columns
platform_credentials    9 columns
platforms               4 columns
resumes                 7 columns
settings               32 columns
subscriptions           9 columns
user_preferences       12 columns
users                  23 columns
videos                 12 columns

SEED DATA:
Platforms: 2
Settings: 1

✓ MIGRATION COMPLETE - YOUR DATABASE IS READY!
============================================================
```

---

## 🎉 Next Steps

1. ✅ Run `FULL_DATABASE_SCHEMA_FIXED.sql` in Render database
2. ✅ Create first admin user
3. ✅ Test admin login
4. ✅ Deploy backend to Render (if not already deployed)
5. ✅ Share backend URL with frontend team

---

**All issues from previous attempts have been resolved in this final version!**
