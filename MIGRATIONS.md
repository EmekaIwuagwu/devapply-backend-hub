# Database Migrations Guide

## How Migrations Work (Automatic)

### ✅ Migrations Run Automatically on Deployment

Every time your app deploys on Render, the `scripts/start-web.sh` script automatically runs:

```bash
flask db upgrade
```

This means:
1. **You push new migration files** to your repo
2. **Render auto-deploys** (or you manually deploy)
3. **Migrations run automatically** before the server starts
4. **All tables are created/updated** without manual intervention

### Current Migration Files

1. **`20251115_000000_initial_schema.py`** - Creates all base tables
   - users
   - subscriptions
   - payments
   - resumes
   - applications
   - platform_credentials
   - job_search_configs
   - platforms
   - job_listings
   - job_queue
   - automation_logs

2. **`20251115_072114_add_user_verification_preferences.py`** - Adds additional features
   - Email verification fields
   - Password reset fields
   - user_preferences table

---

## Manual Migration (If Needed)

If you need to run migrations manually:

### On Render

**Option 1: Via Render Shell**
1. Go to Render Dashboard → Your Service → **Shell** tab
2. Run:
```bash
flask db upgrade
```

**Option 2: Via Render Manual Deploy**
1. Go to Render Dashboard → Your Service
2. Click **Manual Deploy** → **Deploy latest commit**
3. Migrations run automatically during deployment

### On Local Development

```bash
# Export your database URL
export DATABASE_URL="postgresql://user:password@localhost/dbname"

# Run migrations
flask db upgrade

# Or use the migration script
./scripts/migrate-database.sh
```

---

## Using the Migration Script

The `scripts/migrate-database.sh` script provides a user-friendly way to run migrations with verification:

```bash
# Set your database URL (if not already set)
export DATABASE_URL="postgresql://..."

# Run the script
./scripts/migrate-database.sh
```

**What it does:**
1. ✅ Checks DATABASE_URL is set
2. ✅ Runs `flask db upgrade`
3. ✅ Shows current migration version
4. ✅ Lists all created tables
5. ✅ Reports success or failure

**Example output:**
```
==================================
DevApply Database Migration Script
==================================

Database URL: postgresql://user:...
Running database migrations...
INFO  [alembic.runtime.migration] Running upgrade  -> 20251115_000000, Initial database schema
INFO  [alembic.runtime.migration] Running upgrade 20251115_000000 -> 20251115_072114

✅ Migrations completed successfully!

Current database version:
20251115_072114 (head)

All tables created:
  - alembic_version
  - applications
  - automation_logs
  - job_listings
  - job_queue
  - job_search_configs
  - payments
  - platform_credentials
  - platforms
  - resumes
  - subscriptions
  - user_preferences
  - users

==================================
```

---

## Creating New Migrations

When you add new models or change existing ones:

### Step 1: Generate Migration

```bash
# Auto-generate migration from model changes
flask db migrate -m "Description of changes"

# This creates a new file in migrations/versions/
```

### Step 2: Review Generated Migration

```bash
# Check the newly created file
ls -lt migrations/versions/

# Review the upgrade() and downgrade() functions
# Make sure they're correct
```

### Step 3: Test Migration Locally

```bash
# Run the migration
flask db upgrade

# Test your app
# If there are issues, rollback
flask db downgrade

# Fix the migration file and try again
```

### Step 4: Commit and Push

```bash
git add migrations/versions/
git commit -m "Add migration: description"
git push origin your-branch
```

### Step 5: Deploy

When deployed to Render, migrations run automatically!

---

## Common Migration Commands

```bash
# Show current database version
flask db current

# Show migration history
flask db history

# Upgrade to latest
flask db upgrade

# Upgrade to specific version
flask db upgrade <revision_id>

# Downgrade one version
flask db downgrade -1

# Downgrade to specific version
flask db downgrade <revision_id>

# Show pending migrations
flask db heads
```

---

## Troubleshooting

### Issue: "relation does not exist"

**Cause:** Migrations haven't been run yet

**Solution:**
1. Check Render deployment logs for migration output
2. Manually run `flask db upgrade` in Render Shell
3. Or redeploy to trigger migrations

### Issue: "Can't locate revision identified by '...'"

**Cause:** Migration dependency chain is broken

**Solution:**
1. Check `down_revision` in migration files
2. Ensure they form a proper chain
3. The latest migration's `revision` should match `flask db heads`

### Issue: Migration runs but tables not created

**Cause:** Migration might have errors or wrong database

**Solution:**
1. Check the migration file's `upgrade()` function
2. Verify DATABASE_URL points to correct database
3. Check Render logs for error messages

### Issue: Duplicate migration IDs

**Cause:** Two migration files with same revision ID

**Solution:**
1. Each migration must have unique `revision` value
2. Use format: `YYYYMMDD_HHMMSS` for consistency
3. Delete duplicate and regenerate if needed

---

## Migration Best Practices

### ✅ DO:
- Review auto-generated migrations before committing
- Test migrations locally first
- Use descriptive migration messages
- Keep migrations small and focused
- Commit migration files to git

### ❌ DON'T:
- Edit migrations after they've been deployed
- Delete old migration files
- Skip migration steps manually
- Manually create tables instead of using migrations
- Share databases between dev/staging/prod without migrations

---

## Database Schema Inspection

### View all tables:
```bash
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    print('\\n'.join(db.metadata.tables.keys()))
"
```

### View table structure:
```bash
psql $DATABASE_URL -c "\d+ users"
```

### Count records:
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM users;"
```

---

## Current Deployment Status

✅ **Automatic migrations are enabled** in `scripts/start-web.sh`

✅ **Migration files are in place** under `migrations/versions/`

✅ **On next Render deployment, all tables will be created automatically**

---

## Quick Reference

| Task | Command |
|------|---------|
| Run migrations | `flask db upgrade` |
| Check current version | `flask db current` |
| Create new migration | `flask db migrate -m "message"` |
| Rollback migration | `flask db downgrade` |
| View history | `flask db history` |
| Manual script | `./scripts/migrate-database.sh` |

---

**Note:** You don't need to run migrations manually on Render. They happen automatically on every deployment! 🚀
