# How to Check If Background Workers Are Running

## Quick Check Method

### Option 1: Visit System Status Endpoint

Open your browser and go to:
```
https://devapply-backend.onrender.com/api/system/status
```

**If workers are NOT running, you'll see:**
```json
{
  "success": true,
  "data": {
    "overall_status": "critical",
    "services": {
      "web_api": {
        "status": "running"
      },
      "celery_worker": {
        "status": "not_running",
        "message": "⚠️ NO CELERY WORKERS DETECTED - Background processing will not work!",
        "action_required": "Deploy devapply-worker service in Render"
      },
      "celery_beat": {
        "status": "not_running",
        "message": "⚠️ NO CELERY BEAT SCHEDULER DETECTED - Scheduled tasks will not run!"
      }
    },
    "recommendations": [
      "Check Render dashboard for devapply-worker service",
      "Check Render dashboard for devapply-beat service"
    ]
  }
}
```

**If workers ARE running, you'll see:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "services": {
      "web_api": {
        "status": "running"
      },
      "database": {
        "status": "connected"
      },
      "redis": {
        "status": "connected"
      },
      "celery_worker": {
        "status": "running",
        "message": "1 worker(s) active",
        "workers": ["celery@devapply-worker-xxxx"]
      },
      "celery_beat": {
        "status": "running",
        "message": "Celery beat scheduler is active"
      }
    }
  }
}
```

### Option 2: Check Render Dashboard

1. Go to https://dashboard.render.com
2. Sign in to your account
3. Look at your services list

**What you should see:**

✅ **5 Services Total:**
- `devapply-db` (PostgreSQL) - Blue/Purple database icon
- `devapply-redis` (Redis) - Red Redis icon
- `devapply-api` (Web Service) - Green "Web Service" label
- `devapply-worker` (Background Worker) - Purple "Background Worker" label
- `devapply-beat` (Background Worker) - Purple "Background Worker" label

**What you probably have now (the problem):**

❌ **Only 3 Services:**
- `devapply-db` ✅
- `devapply-redis` ✅
- `devapply-api` ✅
- `devapply-worker` ❌ **MISSING**
- `devapply-beat` ❌ **MISSING**

## If Worker Services Are Missing

You need to create them! Here's how:

### Quick Method: Use Blueprint

1. In Render Dashboard, click **"New"** → **"Blueprint"**
2. Connect to: `EmekaIwuagwu/devapply-backend-hub`
3. Select branch: `main` or your current branch
4. Click **"Apply"**

Render will create ALL services defined in `render.yaml`.

### After Creation: Set Environment Variables

For **devapply-worker** service:
1. Click on the service
2. Go to "Environment" tab
3. Add these variables:
   - `CREDENTIALS_ENCRYPTION_KEY` - Copy from devapply-api
   - `SMTP_USER` - Your Gmail address
   - `SMTP_PASS` - Your Gmail app password

For **devapply-beat** service:
1. Click on the service
2. Go to "Environment" tab
3. Add this variable:
   - `CREDENTIALS_ENCRYPTION_KEY` - Same value as above

4. Click **"Save Changes"** on each service

## How to View Worker Logs

Once services are created:

### View Worker Service Logs
1. In Render Dashboard, click on **"devapply-worker"**
2. Click **"Logs"** tab
3. You should see:
```
===============================================================================
STARTING CELERY WORKER - Background Process Starting
===============================================================================
CELERY WORKER STARTING
===============================================================================
Registered tasks: [
  'app.tasks.immediate_applicator.start_immediate_applications',
  'app.tasks.job_scraper.scrape_jobs_all_users',
  'app.tasks.job_applicator.process_job_queue',
  ...
]
===============================================================================
[2025-11-20 20:00:00,000: INFO/MainProcess] celery@worker-hostname ready.
```

### View Beat Scheduler Logs
1. Click on **"devapply-beat"**
2. Click **"Logs"** tab
3. You should see:
```
===============================================================================
STARTING CELERY BEAT SCHEDULER - Periodic Task Scheduler Starting
===============================================================================
[2025-11-20 20:00:00,000: INFO/MainProcess] beat: Starting...
[2025-11-20 20:00:00,000: INFO/MainProcess] Scheduler: Sending due task scrape-jobs-every-6-hours
```

## What Each Service Does

| Service | Purpose | Signs It's Working |
|---------|---------|-------------------|
| **devapply-api** | Handles HTTP requests | Returns 200 OK on /health |
| **devapply-worker** | Processes background jobs | Logs show "celery@worker ready" |
| **devapply-beat** | Schedules periodic tasks | Logs show "beat: Starting..." |
| **devapply-db** | Stores data | Web service connects successfully |
| **devapply-redis** | Message queue | Worker can connect to Redis |

## Test If It's Actually Working

### Test 1: Check System Status
```bash
curl https://devapply-backend.onrender.com/api/system/status
```

Look for `"overall_status": "healthy"` and both workers showing `"status": "running"`.

### Test 2: Trigger Immediate Application

1. Register a test user via API
2. Upload a resume
3. Add platform credentials
4. Save job search config

Then check **devapply-worker** logs - you should see:
```
================================================================================
IMMEDIATE APPLICATION TASK STARTED
User ID: 1, Config ID: 1
================================================================================
```

### Test 3: Check Scheduled Tasks

Wait a few minutes and check **devapply-beat** logs for:
```
[INFO] Scheduler: Sending due task scrape-jobs-every-6-hours
```

Then check **devapply-worker** logs for task execution.

## Common Issues

### "I created the services but they keep crashing"

**Check the logs for error messages. Common causes:**
- Missing environment variables (especially `CREDENTIALS_ENCRYPTION_KEY`)
- Wrong Redis URL
- Wrong Database URL
- Python import errors

### "I don't see worker or beat in my Render dashboard"

**You need to create them!** They don't exist yet. Use the Blueprint method above.

### "System status shows 'not_running'"

**The services exist but aren't running.** Check their logs:
1. Click on the service
2. Go to Logs tab
3. Look for error messages
4. Fix the errors (usually missing env vars)
5. Click "Manual Deploy" to restart

## Expected Behavior When Everything Works

1. **Web service starts** → You see Gunicorn logs
2. **Worker service starts** → You see Celery worker logs
3. **Beat service starts** → You see Celery beat logs
4. **User saves config** → Worker logs show task execution
5. **Every 6 hours** → Beat triggers job scraping
6. **Every 30 min** → Beat triggers job queue processing

## Still Not Working?

Share:
1. Screenshot of your Render dashboard showing ALL services
2. Output from `/api/system/status` endpoint
3. Logs from devapply-worker (if it exists)
4. Logs from devapply-beat (if it exists)
5. Any error messages you see
