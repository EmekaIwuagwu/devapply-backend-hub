# DevApply Quick Start - Fix Missing Background Workers

## Problem
Your web service is running, but background workers are NOT running.
This means no job applications are being processed.

## Immediate Diagnostic

Visit this URL in your browser:
```
https://devapply-backend.onrender.com/api/system/status
```

You will see which services are missing. Expected output:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-11-20T20:00:00",
    "overall_status": "critical",
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
        "status": "not_running",
        "message": "⚠️ NO CELERY WORKERS DETECTED",
        "action_required": "Deploy devapply-worker service in Render"
      },
      "celery_beat": {
        "status": "not_running",
        "message": "⚠️ NO CELERY BEAT SCHEDULER DETECTED",
        "action_required": "Deploy devapply-beat service in Render"
      }
    },
    "recommendations": [
      "Check Render dashboard for devapply-worker service",
      "Check Render dashboard for devapply-beat service"
    ]
  }
}
```

## Solution: Deploy Missing Services

### Step 1: Check Your Render Dashboard

1. Go to https://dashboard.render.com
2. Look at your services list

**You should have 5 services:**
- ✅ devapply-db (PostgreSQL)
- ✅ devapply-redis (Redis)
- ✅ devapply-api (Web Service) - This one is running
- ❌ devapply-worker (Background Worker) - **MISSING**
- ❌ devapply-beat (Background Worker) - **MISSING**

### Step 2: Create Missing Worker Services

#### Option A: Use Blueprint (Fast & Automatic)

1. In Render Dashboard, click **"New"** → **"Blueprint"**
2. Connect your GitHub repository
3. Select the repository (EmekaIwuagwu/devapply-backend-hub)
4. Render will read `render.yaml` and create ALL services
5. Set environment variables (see below)

#### Option B: Manual Creation

##### Create Celery Worker

1. Click **"New"** → **"Background Worker"**
2. Connect repository: `EmekaIwuagwu/devapply-backend-hub`
3. Settings:
   - **Name**: `devapply-worker`
   - **Environment**: Docker
   - **Region**: Oregon (same as your web service)
   - **Branch**: `main`
   - **Docker Command**: `sh scripts/start-worker.sh`
   - **Plan**: Free

4. **Environment Variables** - Click "Add Environment Variable" for each:
   ```
   DATABASE_URL
   → Link to devapply-db → connectionString

   REDIS_URL
   → Link to devapply-redis → connectionString

   CELERY_BROKER_URL
   → Link to devapply-redis → connectionString

   CELERY_RESULT_BACKEND
   → Link to devapply-redis → connectionString

   CREDENTIALS_ENCRYPTION_KEY
   → (copy from your devapply-api service)

   SMTP_HOST
   → smtp.gmail.com

   SMTP_PORT
   → 587

   SMTP_USER
   → your-email@gmail.com

   SMTP_PASS
   → your-gmail-app-password

   SMTP_FROM
   → noreply@devapply.com

   MAX_APPLICATIONS_PER_HOUR
   → 5

   MAX_APPLICATIONS_PER_DAY
   → 20
   ```

5. Click **"Create Background Worker"**

##### Create Celery Beat Scheduler

1. Click **"New"** → **"Background Worker"**
2. Connect same repository
3. Settings:
   - **Name**: `devapply-beat`
   - **Environment**: Docker
   - **Region**: Oregon
   - **Branch**: `main`
   - **Docker Command**: `sh scripts/start-beat.sh`
   - **Plan**: Free

4. **Environment Variables**:
   ```
   DATABASE_URL
   → Link to devapply-db → connectionString

   REDIS_URL
   → Link to devapply-redis → connectionString

   CELERY_BROKER_URL
   → Link to devapply-redis → connectionString

   CELERY_RESULT_BACKEND
   → Link to devapply-redis → connectionString

   CREDENTIALS_ENCRYPTION_KEY
   → (same as web service)
   ```

5. Click **"Create Background Worker"**

### Step 3: Verify Services Are Running

Wait 2-3 minutes for services to deploy, then:

#### Check Worker Logs

1. Go to Render Dashboard
2. Click on **"devapply-worker"**
3. Click **"Logs"** tab

**You should see:**
```
===============================================================================
STARTING CELERY WORKER - Background Process Starting
===============================================================================
Worker Configuration:
  - Concurrency: 2
  - Max tasks per child: 1000
===============================================================================
CELERY WORKER STARTING
===============================================================================
Registered tasks: [...'app.tasks.immediate_applicator.start_immediate_applications'...]
===============================================================================
[INFO] celery@<hostname> ready.
```

#### Check Beat Logs

1. Click on **"devapply-beat"**
2. Click **"Logs"** tab

**You should see:**
```
===============================================================================
STARTING CELERY BEAT SCHEDULER - Periodic Task Scheduler Starting
===============================================================================
[INFO] beat: Starting...
[INFO] Scheduler: Sending due task scrape-jobs-every-6-hours
```

#### Check System Status Again

Visit: `https://devapply-backend.onrender.com/api/system/status`

**Now you should see:**
```json
{
  "overall_status": "healthy",
  "services": {
    "web_api": { "status": "running" },
    "database": { "status": "connected" },
    "redis": { "status": "connected" },
    "celery_worker": {
      "status": "running",
      "message": "1 worker(s) active"
    },
    "celery_beat": {
      "status": "running",
      "message": "Celery beat scheduler is active"
    }
  }
}
```

## How It Works After Fix

### Automatic Background Processing

Once worker services are running, the system will:

1. **Every 6 hours**: Automatically scrape jobs for all active users
2. **Every 30 minutes**: Process job queue and submit applications
3. **Every day at 10 AM**: Check status of submitted applications
4. **Every day at 8 AM**: Send daily summary emails

### Immediate Application Processing

When a user saves their job search config:
```
User saves config → API endpoint called → Celery task queued → Worker picks up task → Applications submitted immediately
```

**Before fix**: Task is queued but never processed (no worker)
**After fix**: Task is processed within seconds

## Testing

### Test Immediate Application

1. Create a user account
2. Upload a resume
3. Add platform credentials (LinkedIn, Indeed)
4. Save job search configuration

Check worker logs - you should see:
```
================================================================================
IMMEDIATE APPLICATION TASK STARTED
User ID: 1, Config ID: 1
================================================================================
Starting immediate job applications for user 1
```

### Test Scheduled Tasks

Wait for scheduled time (or manually trigger):
- Check beat logs for "Scheduler: Sending due task"
- Check worker logs for task execution

## Still Having Issues?

### Worker Won't Start
- Check all environment variables are set
- Check Redis URL is correct
- Check database URL is correct
- Look for Python errors in logs

### Worker Starts Then Crashes
- Check CREDENTIALS_ENCRYPTION_KEY is set correctly
- Check SMTP credentials
- Share full error logs from worker service

### Tasks Not Executing
- Verify worker shows "ready" in logs
- Check Redis connection from worker
- Verify tasks are registered (see "Registered tasks" in worker logs)

## Get Help

1. Share logs from ALL services (web, worker, beat)
2. Share system status JSON output
3. Share screenshot of Render dashboard showing all services
4. Check TROUBLESHOOTING.md for detailed diagnostics

## Summary

✅ Web service alone = NO background processing
✅ Web + Worker + Beat = FULL automation working

The issue is simple: **You need to deploy the worker services!**
