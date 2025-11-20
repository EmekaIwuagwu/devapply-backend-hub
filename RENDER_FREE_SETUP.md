# Free Render Setup & Migration Guide

## 🆓 Free Render Plan - What You Need to Know

Free Render web services:
- ✅ Automatically run your startup scripts (`start-web.sh`)
- ✅ Support background jobs via Shell access
- ✅ Auto-deploy on git push (if enabled)
- ⚠️ Spin down after 15 minutes of inactivity
- ⚠️ Cold starts take ~30 seconds

---

## 🚀 Automatic Migrations on Free Render

### How It Works

Your `scripts/start-web.sh` now runs migrations automatically on **every deployment**:

```bash
# This runs automatically when Render starts your service
python scripts/run_migrations.py
```

**What happens:**
1. Render detects new push → Starts deployment
2. Builds Docker image
3. Runs `start-web.sh`
4. **Migrations run automatically** ← You're here!
5. Server starts
6. App is live ✅

### No Manual Action Required!

Just push your code and Render handles the rest.

---

## 📝 Three Ways to Run Migrations

### Option 1: Automatic (Recommended) ✅

**Push code → Render deploys → Migrations run automatically**

```bash
git add .
git commit -m "Your changes"
git push origin main  # or your branch
```

Render will:
1. Auto-deploy (if enabled)
2. Run migrations via `start-web.sh`
3. Start your app

**No manual steps needed!**

---

### Option 2: Manual via Render Shell

If you need to run migrations manually:

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Select your `devapply-api` service

2. **Open Shell**
   - Click "Shell" tab at the top
   - Wait for shell to connect (~5 seconds)

3. **Run Migration**
   ```bash
   python migrate.py
   ```

   Or:
   ```bash
   python scripts/run_migrations.py
   ```

   Or:
   ```bash
   flask db upgrade
   ```

**That's it!** Tables will be created.

---

### Option 3: Manual Redeploy

Force Render to redeploy (migrations run automatically):

1. **Go to Render Dashboard**
2. **Select your service**
3. **Click "Manual Deploy"**
4. **Select "Clear build cache & deploy"** or "Deploy latest commit"
5. **Wait 2-5 minutes**

Migrations run automatically during deployment!

---

## 🔍 Verify Migrations Ran Successfully

### Check Render Logs

1. Render Dashboard → Your service → **Logs** tab
2. Look for:
   ```
   🚀 DevApply Database Migration Script
   Step 1: Checking database connection...
   ✅ Database connection successful!
   Step 2: Running migrations...
   INFO  [alembic.runtime.migration] Running upgrade  -> 20251115_000000
   INFO  [alembic.runtime.migration] Running upgrade 20251115_000000 -> 20251115_072114
   ✅ Migrations completed successfully!
   Step 3: Verifying tables...
   ✅ Found 13 tables in database:
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
   ✅ Migration process completed successfully!
   ```

### Test Registration

```bash
curl -X POST https://devapply-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
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

✅ If you get this, migrations worked!

---

## 🐛 Troubleshooting Free Render

### Issue: Service is sleeping

**Symptom:** First request takes 30+ seconds

**Cause:** Free services spin down after 15 min inactivity

**Solution:** This is normal! Just wait for cold start.

**Tip:** Use a service like [UptimeRobot](https://uptimerobot.com) (free) to ping your health endpoint every 5 minutes to keep it awake.

---

### Issue: "relation users does not exist"

**Symptom:** Registration fails with database error

**Cause:** Migrations haven't run yet

**Solution:**

**Quick Fix (2 minutes):**
1. Render Dashboard → Shell
2. Run: `python migrate.py`
3. Wait for success message
4. Test registration again

**Permanent Fix:**
1. Trigger manual redeploy
2. Check logs to verify migrations ran
3. Migrations will run on every future deployment

---

### Issue: Logs don't show migration output

**Symptom:** Can't see migration logs

**Cause:** Logs scrolled too fast or service restarted

**Solution:**
1. Render Dashboard → Logs tab
2. Scroll to the top (deployment start)
3. Look for "Running database migrations..."

Or run manually in Shell to see output:
```bash
python migrate.py
```

---

### Issue: Migration script not found

**Symptom:** `scripts/run_migrations.py: No such file or directory`

**Cause:** Code not deployed yet

**Solution:**
1. Ensure latest code is pushed to git
2. Verify Render is watching correct branch
3. Trigger manual deploy
4. Check deployment logs

---

### Issue: Database connection fails

**Symptom:** "Could not connect to database"

**Cause:** DATABASE_URL not set or database not ready

**Solution:**
1. Check Render Dashboard → Environment variables
2. Verify `DATABASE_URL` is set (from database service)
3. Verify database service is running
4. Wait 30 seconds and retry

---

## 📊 Migration Status Commands

Run these in Render Shell:

```bash
# Check current migration version
flask db current

# List all migrations
flask db history

# Verify tables exist
python -c "
import os, psycopg2
from urllib.parse import urlparse
url = urlparse(os.environ['DATABASE_URL'])
conn = psycopg2.connect(database=url.path[1:], user=url.username, password=url.password, host=url.hostname, port=url.port)
cur = conn.cursor()
cur.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\' ORDER BY table_name;')
for t in cur.fetchall(): print(t[0])
"

# Run migrations with full output
python migrate.py
```

---

## 🎯 Quick Start for New Deployment

1. **Push latest code**
   ```bash
   git push origin main
   ```

2. **Wait for deployment** (2-5 minutes)

3. **Check logs**
   - Look for migration success messages

4. **Test health endpoint**
   ```bash
   curl https://devapply-backend.onrender.com/health
   ```

5. **Test registration**
   ```bash
   curl -X POST https://devapply-backend.onrender.com/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"test@test.com","password":"Test123!@#","full_name":"Test"}'
   ```

✅ Done!

---

## 💡 Free Render Tips

### Enable Auto-Deploy
1. Render Dashboard → Your service → Settings
2. Scroll to "Build & Deploy"
3. Enable "Auto-Deploy" for your branch
4. Now every push triggers automatic deployment (and migrations!)

### Add Health Check URL
1. Settings → Health Check Path
2. Set to: `/health`
3. Render will verify your app is running

### Set Environment Variables
Required variables:
- ✅ `DATABASE_URL` - Auto-set from database service
- ✅ `JWT_SECRET_KEY` - Auto-generated
- ⚠️ `CREDENTIALS_ENCRYPTION_KEY` - **Set this manually!**
- ⚠️ `SMTP_USER` - Set if using email
- ⚠️ `SMTP_PASS` - Set if using email

### Monitor Logs
- Enable "Live tail" in Logs tab
- See real-time deployment and migration output

### Use Shell for Debugging
- Shell tab gives you terminal access
- Run Python commands, check database, etc.
- Useful for troubleshooting

---

## 🔥 Current Status

✅ **Automatic migrations enabled** in `start-web.sh`

✅ **Python migration script** (`scripts/run_migrations.py`)

✅ **Simple migration runner** (`migrate.py`)

✅ **All migration files** in place

✅ **Ready for deployment!**

---

## 📞 Need Help?

If migrations still fail after trying the above:

1. **Check Render logs** - Most errors are visible here
2. **Run migration manually** via Shell - See exact error
3. **Verify database service** is running and connected
4. **Check environment variables** are set correctly

---

**Next Step:** Push your latest code and let Render deploy automatically! 🚀
