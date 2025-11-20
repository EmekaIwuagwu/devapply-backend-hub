# Database Setup Guide

## Quick Setup (Using SQL File)

Follow these steps to create your database schema directly in PostgreSQL:

### Step 1: Access Your Render Database

1. Go to your Render Dashboard
2. Navigate to your PostgreSQL database
3. Click "Connect" and choose one of these methods:

**Option A: Using psql command line**
```bash
# Copy the External Database URL from Render
psql postgresql://user:password@host:port/database
```

**Option B: Using Render's Web Shell**
- Click "Shell" tab in your database dashboard
- You'll get a psql prompt directly

### Step 2: Run the Schema SQL

Once connected to your database, run:

```sql
\i database_schema.sql
```

Or copy and paste the entire contents of `database_schema.sql` into the psql prompt.

### Step 3: Verify Tables Were Created

Run these verification queries:

```sql
-- List all tables
\dt

-- Check users table structure
\d users

-- Verify role column exists
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'users' AND column_name = 'role';

-- Check settings table
SELECT * FROM settings;

-- Check platforms
SELECT * FROM platforms;
```

You should see:
- ✅ 15 tables created
- ✅ Users table has `role` column
- ✅ 1 row in settings table
- ✅ 2 rows in platforms table (LinkedIn, Indeed)

### Step 4: Create Your First Admin User

```sql
-- Method 1: Create a new admin user
INSERT INTO users (
    id, email, password_hash, role, email_verified, created_at
) VALUES (
    gen_random_uuid()::text,
    'admin@yourcompany.com',
    '$pbkdf2-sha256$...',  -- You'll need to generate this via the API
    'admin',
    true,
    CURRENT_TIMESTAMP
);

-- Method 2: Upgrade existing user to admin
UPDATE users
SET role = 'admin'
WHERE email = 'your.email@example.com';

-- Verify admin user
SELECT id, email, role FROM users WHERE role = 'admin';
```

### Step 5: Test the Backend

```bash
# Test health check
curl https://your-backend.onrender.com/health

# Test admin login
curl -X POST https://your-backend.onrender.com/api/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "your_password"
  }'
```

---

## Tables Created

### Core Tables:
1. **users** - User accounts with authentication
2. **user_preferences** - User notification and automation preferences
3. **platforms** - Job platforms (LinkedIn, Indeed)
4. **resumes** - User resume files (base64)
5. **job_search_config** - User job search criteria
6. **subscriptions** - User subscription plans
7. **payments** - Payment transactions
8. **applications** - Job applications tracking
9. **job_listings** - Scraped job postings
10. **job_queue** - Automation job queue
11. **platform_credentials** - Encrypted platform credentials

### Admin Tables:
12. **videos** - Tutorial/help videos
13. **settings** - System configuration (singleton)
14. **activity_logs** - Admin action audit trail
15. **automation_logs** - Automation event logs

---

## Important Notes

### Password Hash Generation

You cannot directly insert a password. You need to:

**Option 1: Use the registration endpoint**
```bash
curl -X POST https://your-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@yourcompany.com",
    "password": "YourSecurePassword123",
    "full_name": "Admin User"
  }'

# Then upgrade to admin
UPDATE users SET role = 'admin' WHERE email = 'admin@yourcompany.com';
```

**Option 2: Generate hash in Python**
```python
from werkzeug.security import generate_password_hash

password = "YourSecurePassword123"
hashed = generate_password_hash(password, method='pbkdf2:sha256')
print(hashed)

# Then insert the hashed password into the database
```

### Database Migrations

If you use the SQL file, you **don't need to run Flask migrations**. The SQL file creates everything.

However, if you want to use migrations in the future:

```bash
# Mark migrations as applied (so Flask doesn't try to recreate tables)
flask db stamp head
```

---

## Troubleshooting

### Error: "relation already exists"

This means the table is already created. It's safe to ignore - the SQL uses `CREATE TABLE IF NOT EXISTS`.

### Error: "column already exists"

The SQL checks before adding the role column. If you see this, the column already exists.

### No platforms showing up

```sql
-- Re-run platform insert
INSERT INTO platforms (id, name, is_active, created_at) VALUES
    (gen_random_uuid()::text, 'LinkedIn', true, CURRENT_TIMESTAMP),
    (gen_random_uuid()::text, 'Indeed', true, CURRENT_TIMESTAMP)
ON CONFLICT (name) DO NOTHING;
```

### Settings table is empty

```sql
-- Insert default settings
INSERT INTO settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;
```

---

## Alternative: Using Flask Migrations

If you prefer to use Flask migrations instead of SQL:

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run migrations
flask db upgrade

# Seed platforms
flask seed_platforms
```

---

## Next Steps

After database setup:

1. ✅ Create admin user (see Step 4)
2. ✅ Test admin login endpoint
3. ✅ Access admin dashboard via frontend
4. ✅ Upload tutorial videos
5. ✅ Configure system settings

---

## Database Connection String

Your database connection string format:

```
postgresql://user:password@host:port/database?sslmode=require
```

**For Render:**
- Host: `dpg-xxxxx-a.oregon-postgres.render.com`
- Port: `5432`
- Database: Your database name
- Add `?sslmode=require` at the end

---

## Security Checklist

- [ ] Change default admin password immediately
- [ ] Set strong SECRET_KEY in environment variables
- [ ] Enable SSL for database connections
- [ ] Configure CORS_ORIGINS properly
- [ ] Set up Redis for rate limiting (currently in-memory)
- [ ] Review allowed_file_types in settings
- [ ] Set up regular database backups

---

**Need Help?**

Check the test report: `ADMIN_BACKEND_TEST_REPORT.md`
