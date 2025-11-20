# How to Run SQL Script on Render (Free Tier)

## Step 1: Get Your Database Connection String

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Find your PostgreSQL database** (devapply-db or similar)
3. **Click on the database name**
4. **Scroll down to "Connections"**
5. **Copy the "External Database URL"** (looks like: `postgresql://user:password@host/database`)

## Step 2: Connect to Your Database

### Option A: Using Render's Built-in SQL Editor (Easiest)

1. **In your database dashboard**, scroll down
2. **Find "Execute SQL"** section
3. **Click "Open SQL Editor"**
4. **Copy and paste the entire contents** of `database_schema.sql`
5. **Click "Run SQL"**
6. **Wait for completion** (should take 5-10 seconds)
7. **Check output** - should show "Table created" for each table

### Option B: Using psql Command Line

If you have PostgreSQL installed locally:

```bash
# Copy your database URL from Render
export DATABASE_URL="postgresql://user:password@host/database"

# Run the SQL script
psql $DATABASE_URL < database_schema.sql
```

### Option C: Using Online PostgreSQL Client

1. **Go to**: https://www.pgweb.io/ (or any online PostgreSQL client)
2. **Enter your connection details** from Render
3. **Paste the SQL script** in the query box
4. **Execute**

## Step 3: Verify Tables Were Created

Run this query in the SQL editor:

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
```

You should see these 13 tables:
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

## Step 4: Test Your Backend

After running the SQL script, test registration in Postman:

```
POST https://devapply-backend.onrender.com/api/auth/register

Body (JSON):
{
  "email": "test@example.com",
  "password": "Test123!@#",
  "full_name": "Test User"
}
```

Should return:
```json
{
  "success": true,
  "data": {
    "user": {...},
    "access_token": "...",
    "refresh_token": "..."
  }
}
```

✅ **Done!** Your database is now set up!

---

## Troubleshooting

### Can't find "Execute SQL" on Render

Free Render databases might not have SQL editor. Use Option B or C above.

### "psql: command not found"

You don't have PostgreSQL installed. Use Option C (online client).

### Connection timeout

Your database might be spinning down (free tier). Wait 30 seconds and retry.

### Tables already exist

The script uses `CREATE TABLE IF NOT EXISTS`, so it's safe to run multiple times.

To start fresh (⚠️ **DELETES ALL DATA**):

1. Uncomment the DROP TABLE statements at the top of the SQL file
2. Run the script again

---

## What This Script Does

✅ Creates all 13 database tables
✅ Creates all indexes for performance
✅ Creates all foreign key relationships
✅ Sets up default values
✅ Seeds platform data (LinkedIn, Indeed, etc.)
✅ Sets migration version to prevent conflicts

---

## After Running SQL

Your backend should work immediately! The tables are created and your Flask app can now:
- Register users
- Create applications
- Upload resumes
- Manage subscriptions
- Handle automation
- Everything! ✅

No need to restart Render - it will work on the next request.
