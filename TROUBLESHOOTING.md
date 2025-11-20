# DevApply Deployment Troubleshooting

## Issue: Background Process Not Starting

### Symptoms
- Web service (Gunicorn) starts successfully
- No Celery worker logs visible
- No job applications being processed
- System appears idle

### Root Cause
**The Celery worker and beat scheduler services are not running.**

Your deployment should have **5 services**, but you only have **1** (the web service).

### Required Services

| Service | Type | Purpose | Should See in Logs |
|---------|------|---------|-------------------|
| `devapply-db` | PostgreSQL | Database | N/A |
| `devapply-redis` | Redis | Cache/Queue | N/A |
| `devapply-api` | Web | Flask API | ✅ Gunicorn starting |
| `devapply-worker` | Worker | Background jobs | ❌ **MISSING** |
| `devapply-beat` | Worker | Scheduler | ❌ **MISSING** |

### How to Check Your Render Dashboard

1. Go to https://dashboard.render.com
2. Look for **ALL 5 services** listed above
3. Check the status of each service

**What you should see:**
```
✅ devapply-db (PostgreSQL) - Active
✅ devapply-redis (Redis) - Active
✅ devapply-api (Web Service) - Active
❌ devapply-worker (Background Worker) - NOT CREATED or FAILED
❌ devapply-beat (Background Worker) - NOT CREATED or FAILED
```

## Solution

### Option 1: Deploy Using Blueprint (Recommended)

If you haven't already, use the Blueprint deployment which reads `render.yaml`:

1. **Delete existing manual services** (if any)
2. Go to Render Dashboard
3. Click **"New"** → **"Blueprint"**
4. Connect your GitHub repository
5. Select the repository containing `render.yaml`
6. Click **"Apply"**

Render will automatically create ALL 5 services.

7. **Set environment variables** for each service:
   - `devapply-api`: Set `CREDENTIALS_ENCRYPTION_KEY`, `SMTP_USER`, `SMTP_PASS`
   - `devapply-worker`: Set `CREDENTIALS_ENCRYPTION_KEY`, `SMTP_USER`, `SMTP_PASS`
   - `devapply-beat`: Set `CREDENTIALS_ENCRYPTION_KEY`

### Option 2: Manually Create Missing Services

If you want to keep your existing web service:

#### Create Celery Worker Service

1. Click **"New"** → **"Background Worker"**
2. Connect your GitHub repository
3. Configure:
   - Name: `devapply-worker`
   - Environment: **Docker**
   - Region: **Oregon** (same as web service)
   - Branch: `main`
   - Docker Command: `sh scripts/start-worker.sh`
   - Plan: **Free**

4. Add Environment Variables (copy from your web service):
   ```
   DATABASE_URL (from devapply-db)
   REDIS_URL (from devapply-redis)
   CELERY_BROKER_URL (from devapply-redis)
   CELERY_RESULT_BACKEND (from devapply-redis)
   CREDENTIALS_ENCRYPTION_KEY (same as web service)
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER (your Gmail)
   SMTP_PASS (your Gmail app password)
   SMTP_FROM=noreply@devapply.com
   MAX_APPLICATIONS_PER_HOUR=5
   MAX_APPLICATIONS_PER_DAY=20
   ```

5. Click **"Create Background Worker"**

#### Create Celery Beat Service

1. Click **"New"** → **"Background Worker"**
2. Connect your GitHub repository
3. Configure:
   - Name: `devapply-beat`
   - Environment: **Docker**
   - Region: **Oregon**
   - Branch: `main`
   - Docker Command: `sh scripts/start-beat.sh`
   - Plan: **Free**

4. Add Environment Variables:
   ```
   DATABASE_URL (from devapply-db)
   REDIS_URL (from devapply-redis)
   CELERY_BROKER_URL (from devapply-redis)
   CELERY_RESULT_BACKEND (from devapply-redis)
   CREDENTIALS_ENCRYPTION_KEY (same as web service)
   ```

5. Click **"Create Background Worker"**

## Verification

After creating the services, check the logs for each:

### devapply-worker Logs
You should see:
```
===============================================================================
STARTING CELERY WORKER - Background Process Starting
===============================================================================
Worker Configuration:
  - Concurrency: 2
  - Max tasks per child: 1000
  - Time limit: 3600s
  - Soft time limit: 3000s
===============================================================================
CELERY WORKER STARTING
===============================================================================
Registered tasks: ['app.tasks.immediate_applicator.start_immediate_applications', ...]
===============================================================================
[INFO] celery@worker ready.
```

### devapply-beat Logs
You should see:
```
===============================================================================
STARTING CELERY BEAT SCHEDULER - Periodic Task Scheduler Starting
===============================================================================
[INFO] beat: Starting...
[INFO] Scheduler: Sending due task scrape-jobs-every-6-hours
```

## How Background Processing Works

### Automatic Scheduled Tasks (Celery Beat)
- **Every 6 hours**: Scrapes jobs for all active users
- **Every 30 minutes**: Processes job queue and applies to jobs
- **Daily at 10 AM**: Checks application statuses
- **Daily at 8 AM**: Sends daily summaries

### Immediate Application (Triggered by User)
When a user saves their job search config via API:
```
POST /api/search-config
```
The system IMMEDIATELY starts applying to matching jobs (doesn't wait for scheduled tasks).

### Expected Behavior
1. User creates job search config → **Immediate applications start**
2. Celery beat runs every 6 hours → **Scrapes new jobs for all users**
3. Celery beat runs every 30 min → **Processes queue and applies**

## Common Issues

### Worker Service Keeps Crashing
- Check environment variables are set correctly
- Check Redis connection string is correct
- Check DATABASE_URL is correct
- Look for Python import errors in logs

### Beat Service Not Scheduling Tasks
- Ensure only ONE beat instance is running (not multiple)
- Check Redis connection
- Look for "Scheduler: Sending due task" in logs

### Tasks Queued But Not Executing
- Check worker service is running
- Check Redis connection
- Manually trigger: `celery -A celery_worker.celery inspect active`

## Testing

### Test Immediate Application
1. Register a user via API
2. Upload a resume
3. Add platform credentials
4. Save job search config

You should see in worker logs:
```
================================================================================
IMMEDIATE APPLICATION TASK STARTED
User ID: 123, Config ID: 456
================================================================================
```

### Test Scheduled Tasks
Wait for scheduled time or manually trigger:
```bash
# SSH into worker service
celery -A celery_worker.celery call app.tasks.job_scraper.scrape_jobs_all_users
```

## Still Not Working?

1. Share logs from **ALL THREE services** (api, worker, beat)
2. Share screenshot of Render dashboard showing all services
3. Verify environment variables are set for worker services
4. Check if Redis and Database are accessible from worker service

## Quick Diagnostic Commands

### Check if Redis is accessible
```bash
# In worker service shell
python -c "import redis; r=redis.from_url('$REDIS_URL'); print(r.ping())"
```

### Check if Database is accessible
```bash
# In worker service shell
python -c "import psycopg2; conn=psycopg2.connect('$DATABASE_URL'); print('Connected')"
```

### List registered Celery tasks
```bash
celery -A celery_worker.celery inspect registered
```
