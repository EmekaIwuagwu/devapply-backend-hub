# DevApply Backend - Automation System Guide

## Overview

The DevApply automation system enables **background job processing** to automatically discover jobs and apply on behalf of users even when they're offline.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DevApply Automation                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │  Flask   │───▶│  Celery  │───▶│  Redis   │              │
│  │  API     │    │  Worker  │    │  Broker  │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│                         │                                     │
│                         ▼                                     │
│              ┌─────────────────────┐                         │
│              │  Background Tasks   │                         │
│              ├─────────────────────┤                         │
│              │ • Job Scraping      │                         │
│              │ • Auto-Application  │                         │
│              │ • Status Monitoring │                         │
│              │ • Notifications     │                         │
│              │ • Cleanup           │                         │
│              └─────────────────────┘                         │
│                         │                                     │
│                         ▼                                     │
│              ┌─────────────────────┐                         │
│              │  Browser Automation │                         │
│              │ (Selenium/Playwright)│                         │
│              └─────────────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Database Models

#### JobQueue
Manages the queue of jobs to apply to:
- **Status**: pending, processing, applied, failed, skipped
- **Priority**: 1-10 (higher = more urgent)
- **Match Score**: 0-100 (how well job matches user preferences)
- **Retry Logic**: Max 3 retries with exponential backoff

#### JobListing
Cached job postings from various platforms:
- Stores scraped job data
- Prevents duplicate applications
- Tracks active/inactive status

#### AutomationLog
Audit trail of all automation activities:
- Job searches
- Applications submitted
- Status updates
- Errors and retries

### 2. Celery Tasks

#### Job Scraping (`app/tasks/job_scraper.py`)
- **Schedule**: Every 6 hours
- **Function**: Scrape jobs from configured platforms
- **Logic**:
  1. Get user's job search configuration
  2. Scrape each platform for matching jobs
  3. Calculate match scores using AI algorithm
  4. Add high-scoring jobs to queue

#### Job Application (`app/tasks/job_applicator.py`)
- **Schedule**: Every 30 minutes
- **Function**: Process pending jobs in queue
- **Logic**:
  1. Check subscription limits
  2. Verify rate limits
  3. Launch browser automation
  4. Fill and submit application
  5. Create application record

#### Status Checking (`app/tasks/status_checker.py`)
- **Schedule**: Daily at 10 AM
- **Function**: Monitor application statuses
- **Logic**:
  1. Check recent applications (< 30 days)
  2. Scrape platform for status updates
  3. Notify user of changes

#### Notifications (`app/tasks/notifications.py`)
- **Schedule**: Daily at 8 AM
- **Function**: Send daily summaries
- **Includes**:
  - Applications submitted yesterday
  - Pending jobs in queue
  - Status updates

#### Cleanup (`app/tasks/cleanup.py`)
- **Schedule**: Daily at 2 AM
- **Function**: Database maintenance
- **Actions**:
  - Delete job listings > 30 days old
  - Remove failed queue items > 7 days old
  - Archive old automation logs

### 3. Job Matching Algorithm

Located in `app/utils/job_matcher.py`:

```python
def calculate_match_score(job_listing, user_config, user_skills):
    """
    Weights:
    - Keywords: 40%
    - Location: 20%
    - Salary: 20%
    - Experience: 10%
    - Job Type: 10%

    Returns: 0-100 score
    """
```

**Threshold**: Jobs with score ≥ 70% are queued for application.

### 4. Rate Limiting

Located in `app/utils/rate_limiter.py`:

**Default Limits** (configurable per platform):
- **Per Hour**: 5 applications
- **Per Day**: 20 applications
- **Delay Between**: 3 minutes

**Platform-Specific**:
- LinkedIn: 5/hour, 20/day, 3min delay
- Indeed: 10/hour, 40/day, 2min delay
- Glassdoor: 5/hour, 15/day, 4min delay

### 5. Browser Automation

**Base Class**: `app/automation/bot_base.py`

Each platform extends `JobApplicationBot` and implements:
- `login()` - Authenticate with platform
- `navigate_to_job()` - Open job posting
- `fill_application_form()` - Fill form fields
- `upload_resume()` - Attach resume
- `submit_application()` - Submit application

**Technologies**:
- Selenium (headless Chrome)
- Playwright (alternative)
- Proxy support for IP rotation

## API Endpoints

### Automation Control

```
GET    /api/automation/queue             - Get pending jobs
POST   /api/automation/queue/:id/skip    - Skip a queued job
PUT    /api/automation/queue/:id/priority - Update priority
DELETE /api/automation/queue/:id         - Remove from queue

GET    /api/automation/status            - Get automation stats
GET    /api/automation/logs              - Get activity logs

GET    /api/automation/discovered-jobs   - Get scraped jobs
POST   /api/automation/discovered-jobs/:id/queue - Manually queue job
```

## Running the System

### Requirements

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:latest
```

### Start Services

**Terminal 1: Flask API**
```bash
python run.py
# or
flask run
```

**Terminal 2: Celery Worker**
```bash
celery -A celery_worker.celery worker --loglevel=info
```

**Terminal 3: Celery Beat (Scheduler)**
```bash
celery -A celery_worker.celery beat --loglevel=info
```

**Terminal 4: Flower (Monitoring - Optional)**
```bash
celery -A celery_worker.celery flower
# Access at http://localhost:5555
```

### Production Deployment

**Using Supervisor** (`supervisord.conf`):
```ini
[program:devapply_api]
command=gunicorn run:app -w 4 -b 0.0.0.0:5000
directory=/path/to/devapply-backend
user=www-data
autostart=true
autorestart=true

[program:devapply_worker]
command=celery -A celery_worker.celery worker -l info -c 4
directory=/path/to/devapply-backend
user=www-data
autostart=true
autorestart=true

[program:devapply_beat]
command=celery -A celery_worker.celery beat -l info
directory=/path/to/devapply-backend
user=www-data
autostart=true
autorestart=true
```

**Using Docker Compose**:
```yaml
version: '3.8'

services:
  api:
    build: .
    command: gunicorn run:app -w 4 -b 0.0.0.0:5000
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  worker:
    build: .
    command: celery -A celery_worker.celery worker -l info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  beat:
    build: .
    command: celery -A celery_worker.celery beat -l info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
```

## Environment Variables

```bash
# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Rate Limits
MAX_APPLICATIONS_PER_HOUR=5
MAX_APPLICATIONS_PER_DAY=20
APPLICATION_DELAY_SECONDS=180

# Proxy (for scraping)
PROXY_SERVICE_URL=
PROXY_SERVICE_KEY=

# Email Notifications
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Implementing Platform Scrapers

Create `app/scrapers/linkedin_scraper.py`:

```python
from app.scrapers.base_scraper import BaseJobScraper
from datetime import datetime

class LinkedInScraper(BaseJobScraper):
    def scrape(self, job_title, location, keywords=None):
        # Build search URL
        url = f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}"

        # Make request
        response = self.make_request(url)
        soup = self.parse_html(response.text)

        jobs = []
        # Parse job cards
        for job_card in soup.select('.job-card'):
            jobs.append({
                'platform': 'LinkedIn',
                'external_id': job_card.get('data-job-id'),
                'company_name': job_card.select_one('.company-name').text,
                'job_title': job_card.select_one('.job-title').text,
                'location': job_card.select_one('.location').text,
                'job_url': job_card.find('a')['href'],
                # ... more fields
            })

        return jobs
```

## Implementing Platform Bots

Create `app/automation/linkedin_bot.py`:

```python
from app.automation.bot_base import JobApplicationBot
from selenium import webdriver
from selenium.webdriver.common.by import By

class LinkedInBot(JobApplicationBot):
    def initialize_browser(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)

    def login(self):
        self.driver.get('https://www.linkedin.com/login')
        # Enter credentials and login
        return True

    def navigate_to_job(self, job_url):
        self.driver.get(job_url)
        return True

    def fill_application_form(self):
        # Fill form fields from user profile
        return True

    def upload_resume(self):
        resume_path = self.save_resume_to_file()
        upload_btn = self.driver.find_element(By.ID, 'resume-upload')
        upload_btn.send_keys(resume_path)
        return True

    def submit_application(self):
        submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_btn.click()
        return True
```

## Monitoring & Debugging

### Check Celery Tasks
```bash
# View active tasks
celery -A celery_worker.celery inspect active

# View scheduled tasks
celery -A celery_worker.celery inspect scheduled

# View registered tasks
celery -A celery_worker.celery inspect registered
```

### View Automation Logs
```bash
# Via API
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/automation/logs

# Via Database
flask shell
>>> AutomationLog.query.order_by(AutomationLog.created_at.desc()).limit(10).all()
```

### Monitor with Flower
```bash
celery -A celery_worker.celery flower
# Access: http://localhost:5555
```

## Testing

```bash
# Test job scraping
celery -A celery_worker.celery call app.tasks.job_scraper.scrape_jobs_for_user --args='["user-id"]'

# Test job application
celery -A celery_worker.celery call app.tasks.job_applicator.apply_to_job --args='["job-queue-id"]'

# Test rate limiter
flask shell
>>> from app.utils.rate_limiter import ApplicationRateLimiter
>>> ApplicationRateLimiter.can_apply('user-id', 'linkedin')
```

## Security Considerations

1. **Credentials**: Store platform credentials encrypted
2. **Proxies**: Use rotating proxies to avoid IP bans
3. **Rate Limiting**: Respect platform limits
4. **User Agents**: Rotate user agents
5. **CAPTCHAs**: Implement CAPTCHA solving service
6. **Stealth**: Use stealth plugins to avoid detection

## Troubleshooting

### Worker not processing tasks
```bash
# Check Redis connection
redis-cli ping

# Check Celery can connect
celery -A celery_worker.celery inspect ping

# Restart worker
celery -A celery_worker.celery control shutdown
celery -A celery_worker.celery worker --loglevel=info
```

### Tasks stuck in queue
```bash
# Purge all tasks
celery -A celery_worker.celery purge

# Or specific queue
celery -A celery_worker.celery purge -Q default
```

### Database migrations
```bash
flask db migrate -m "Add automation models"
flask db upgrade
```

## Next Steps

1. **Implement Platform Scrapers**: Add scrapers for each platform
2. **Implement Automation Bots**: Add bots for automated applications
3. **Add Email Notifications**: Configure SMTP and templates
4. **Set up Monitoring**: Deploy Flower and logging
5. **Configure Proxies**: Set up proxy service
6. **Scale Workers**: Add more Celery workers as needed

---

**Questions?** Check the main README or create an issue in the repository.
