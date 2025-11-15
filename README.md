# DevApply Backend API

AI-powered job application automation platform backend built with Flask, PostgreSQL, Celery, and JWT authentication.

## Features

### Core Features

- **User Authentication & Management**
  - Email/password registration and login
  - OAuth support (Google, GitHub)
  - JWT token-based authentication
  - Profile management with avatar upload

- **Resume Management**
  - Upload multiple resumes (PDF, DOC, DOCX)
  - Base64 file storage
  - Set default resumes
  - Tag resumes by job type

- **Job Search Configuration**
  - Configure primary and secondary job searches
  - Select from 16+ job platforms
  - Set preferences (location, salary, experience level)
  - Attach specific resumes to searches

- **Application Tracking**
  - Track all job applications
  - Status management (sent, viewed, interview, rejected)
  - Filter and search applications
  - Dashboard statistics

- **Subscription & Billing**
  - Three-tier plans (Free, Pro, Max)
  - Monthly and yearly billing cycles
  - Payment history tracking
  - Application limits based on plan

### Automation Features

- **Background Job Processing**
  - Celery-based task queue with Redis broker
  - Automated job scraping every 6 hours
  - Automated application submission every 30 minutes
  - Daily email summaries at 8 AM
  - Status monitoring and cleanup tasks

- **AI-Powered Job Matching**
  - TF-IDF based job matching algorithm
  - Weighted scoring (keywords 40%, location 20%, salary 20%, etc.)
  - Automatic filtering of duplicate jobs
  - Match score calculation (0-100)

- **Web Scraping**
  - LinkedIn job scraper (Selenium-based for dynamic content)
  - Indeed job scraper (BeautifulSoup-based for speed)
  - Proxy support for reliable scraping
  - Job listing deduplication

- **Browser Automation**
  - LinkedIn Easy Apply bot
  - Indeed application bot
  - Multi-step form handling
  - Secure credential storage with Fernet encryption
  - Rate limiting to avoid detection

- **Email Notifications**
  - Daily application summaries
  - Status update alerts
  - Welcome emails
  - Application limit warnings
  - SMTP-based with HTML templates

## Tech Stack

### Core Backend
- **Framework**: Flask 3.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **CORS**: Flask-CORS
- **Rate Limiting**: Flask-Limiter

### Background Processing
- **Task Queue**: Celery 5.3.4
- **Message Broker**: Redis 5.0
- **Task Scheduler**: Celery Beat
- **Monitoring**: Flower (optional)

### Automation & Scraping
- **Browser Automation**: Selenium 4.15.2
- **Web Scraping**: BeautifulSoup4 4.12.2, lxml 4.9.3
- **HTTP Client**: Requests 2.31.0
- **Headless Browser**: Chrome/Chromium (via Selenium)

### AI & Matching
- **NLP**: Scikit-learn 1.3.2 (TF-IDF)
- **Numerical Computing**: NumPy 1.26.2

### Security & Utilities
- **Encryption**: Cryptography 41.0.7 (Fernet)
- **Email**: SMTP with Jinja2 templates
- **Date/Time**: python-dateutil, pytz

## Project Structure

```
devapply-backend/
├── app/
│   ├── __init__.py              # App factory and configuration
│   ├── config.py                # Configuration settings
│   ├── celery_config.py         # Celery configuration & Beat schedule
│   ├── models/                  # Database models
│   │   ├── user.py              # User accounts
│   │   ├── resume.py            # Resume storage
│   │   ├── application.py       # Application tracking
│   │   ├── job_search_config.py # Job search preferences
│   │   ├── subscription.py      # Subscription plans
│   │   ├── platform.py          # Job platforms
│   │   ├── platform_credential.py # Encrypted credentials
│   │   ├── job_queue.py         # Application queue
│   │   ├── job_listing.py       # Discovered jobs
│   │   └── automation_log.py    # Audit trail
│   ├── routes/                  # API endpoints
│   │   ├── auth.py              # Authentication
│   │   ├── resumes.py           # Resume management
│   │   ├── applications.py      # Application tracking
│   │   ├── search_config.py     # Job search config
│   │   ├── subscription.py      # Billing & plans
│   │   ├── platforms.py         # Job platforms
│   │   ├── credentials.py       # Platform credentials
│   │   └── automation.py        # Automation control
│   ├── tasks/                   # Celery background tasks
│   │   ├── job_scraper.py       # Job scraping tasks
│   │   ├── job_applicator.py    # Application tasks
│   │   ├── status_checker.py    # Status monitoring
│   │   ├── notifications.py     # Email notifications
│   │   └── cleanup.py           # Database cleanup
│   ├── scrapers/                # Web scrapers
│   │   ├── base_scraper.py      # Base scraper class
│   │   ├── linkedin_scraper.py  # LinkedIn scraper
│   │   └── indeed_scraper.py    # Indeed scraper
│   ├── automation/              # Browser automation bots
│   │   ├── bot_base.py          # Base bot class
│   │   ├── linkedin_bot.py      # LinkedIn automation
│   │   └── indeed_bot.py        # Indeed automation
│   ├── utils/                   # Utility functions
│   │   ├── validators.py        # Input validation
│   │   ├── auth_utils.py        # Auth helpers
│   │   ├── file_utils.py        # File handling
│   │   ├── email_service.py     # Email sending
│   │   ├── job_matcher.py       # AI matching
│   │   └── rate_limiter.py      # Rate limiting
│   └── middleware/              # Custom middleware
│       └── auth_middleware.py   # JWT authentication
├── migrations/                  # Database migrations
├── tests/                       # Unit tests
├── run.py                       # Flask app entry point
├── celery_worker.py             # Celery worker entry point
├── generate_key.py              # Encryption key generator
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── .env.example                 # Environment template
├── Procfile                     # Deployment configuration
├── README.md                    # This file
└── AUTOMATION_GUIDE.md          # Automation documentation
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL database
- Redis server (for Celery)
- Chrome/Chromium browser (for Selenium automation)
- pip package manager

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd devapply-backend-hub
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install system dependencies:**

For Ubuntu/Debian:
```bash
# Install Redis
sudo apt-get update
sudo apt-get install redis-server

# Install Chrome for Selenium
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

# Install ChromeDriver (match your Chrome version)
sudo apt-get install chromium-chromedriver
```

For macOS:
```bash
# Install Redis
brew install redis

# Install Chrome
brew install --cask google-chrome

# ChromeDriver will be installed with Selenium
```

5. **Configure environment variables:**

Copy the example file and customize it:
```bash
cp .env.example .env
```

Generate encryption key:
```bash
python3 generate_key.py
```

Edit `.env` with your values:
```env
DATABASE_URL=postgresql://username:password@host:port/database
JWT_SECRET_KEY=your-random-secret-key-here
CREDENTIALS_ENCRYPTION_KEY=<key-from-generate_key.py>
CELERY_BROKER_URL=redis://localhost:6379/0
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

6. **Initialize the database:**
```bash
flask db upgrade
flask seed_platforms
```

7. **Start Redis server:**
```bash
# Linux/macOS
redis-server

# Or as a service
sudo systemctl start redis
```

8. **Start Celery worker (in a new terminal):**
```bash
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

9. **Start Celery Beat scheduler (in another terminal):**
```bash
source venv/bin/activate
celery -A celery_worker.celery beat --loglevel=info
```

10. **Run the Flask development server:**
```bash
flask run
# Or
python run.py
```

The API will be available at `http://localhost:5000`

### Quick Start (All Services)

You can run all services with these commands in separate terminals:

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A celery_worker.celery worker --loglevel=info

# Terminal 3: Celery Beat
celery -A celery_worker.celery beat --loglevel=info

# Terminal 4: Flask API
flask run
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/google` - OAuth login with Google
- `POST /api/auth/github` - OAuth login with GitHub
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/upload-avatar` - Upload user avatar
- `POST /api/auth/change-password` - Change password
- `POST /api/auth/refresh` - Refresh access token

### Resumes
- `POST /api/resumes` - Upload new resume
- `GET /api/resumes` - List all user resumes
- `GET /api/resumes/:id` - Get specific resume
- `GET /api/resumes/:id/download` - Download resume (base64)
- `PUT /api/resumes/:id/default` - Set as default resume
- `DELETE /api/resumes/:id` - Delete resume

### Applications
- `POST /api/applications` - Create new application
- `GET /api/applications` - List applications (with filters)
- `GET /api/applications/:id` - Get specific application
- `PUT /api/applications/:id` - Update application
- `DELETE /api/applications/:id` - Delete application
- `GET /api/applications/stats` - Get dashboard statistics

### Job Search Configuration
- `POST /api/search-config` - Create/update configuration
- `GET /api/search-config` - Get user configuration
- `PUT /api/search-config/:id` - Update configuration
- `DELETE /api/search-config/:id` - Delete configuration

### Subscription
- `GET /api/subscription` - Get current subscription
- `GET /api/subscription/plans` - Get available plans
- `POST /api/subscription/upgrade` - Upgrade plan
- `POST /api/subscription/downgrade` - Downgrade plan
- `POST /api/subscription/cancel` - Cancel subscription
- `POST /api/subscription/payment/method` - Add payment method
- `GET /api/subscription/payment/history` - Get billing history
- `GET /api/subscription/payment/invoice/:id` - Download invoice

### Platforms
- `GET /api/platforms` - List all job platforms

### Platform Credentials
- `POST /api/credentials` - Add platform credentials
- `GET /api/credentials` - List user's credentials
- `GET /api/credentials/:id` - Get specific credential
- `PUT /api/credentials/:id` - Update credential
- `DELETE /api/credentials/:id` - Delete credential

### Automation Control
- `GET /api/automation/queue` - View job queue
- `GET /api/automation/status` - Get automation status
- `GET /api/automation/discovered-jobs` - List discovered jobs
- `POST /api/automation/queue/:id/retry` - Retry failed job
- `DELETE /api/automation/queue/:id` - Remove from queue
- `GET /api/automation/logs` - View automation logs

### Health Check
- `GET /health` - API health check

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2024-01-01T00:00:00"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## Security Features

- **Password Hashing**: PBKDF2-SHA256
- **JWT Tokens**: 1-hour access tokens, 30-day refresh tokens
- **Rate Limiting**: 5 attempts per 15 minutes on auth endpoints
- **File Validation**: Size and type validation for uploads
- **Input Sanitization**: Email, password, and data validation
- **CORS**: Configurable allowed origins

## Docker Deployment

### Using Docker Compose (Local Development)

The easiest way to run the entire stack locally:

```bash
# 1. Set environment variables
export CREDENTIALS_ENCRYPTION_KEY=$(python3 generate_key.py | grep -oP '(?<=CREDENTIALS_ENCRYPTION_KEY=).*')
export SMTP_USER=your-email@gmail.com
export SMTP_PASS=your-app-password

# 2. Start all services
docker-compose up -d

# 3. Check logs
docker-compose logs -f web

# 4. Stop all services
docker-compose down
```

Services started:
- **PostgreSQL** (port 5432)
- **Redis** (port 6379)
- **Flask API** (port 5000)
- **Celery Worker**
- **Celery Beat**
- **Flower** (port 5555) - Celery monitoring

### Using Docker (Production)

Build and run individual services:

```bash
# Build the image
docker build -t devapply-backend .

# Run the web server
docker run -p 5000:5000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379/0 \
  -e JWT_SECRET_KEY=your-secret-key \
  -e CREDENTIALS_ENCRYPTION_KEY=your-encryption-key \
  devapply-backend

# Run Celery worker
docker run \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e CELERY_BROKER_URL=redis://host:6379/0 \
  -e CREDENTIALS_ENCRYPTION_KEY=your-encryption-key \
  devapply-backend \
  celery -A celery_worker.celery worker --loglevel=info

# Run Celery beat
docker run \
  -e CELERY_BROKER_URL=redis://host:6379/0 \
  devapply-backend \
  celery -A celery_worker.celery beat --loglevel=info
```

### Deploying to Render with Docker

Render will automatically detect and use the `render.yaml` configuration:

**Option 1: Using render.yaml (Recommended)**

1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically read `render.yaml` and create:
   - PostgreSQL database
   - Redis instance
   - Web service (Flask API)
   - Worker service (Celery worker)
   - Beat service (Celery beat)

4. Set these environment variables in Render dashboard:
   ```
   CREDENTIALS_ENCRYPTION_KEY=<from generate_key.py>
   SMTP_USER=<your-email>
   SMTP_PASS=<your-app-password>
   ```

**Option 2: Manual Setup**

1. Create a new Web Service in Render
2. Select "Docker" as the environment
3. Set the Docker Command:
   ```
   sh scripts/start-web.sh
   ```
4. Add environment variables (see Environment Variables Required below)
5. Repeat for worker and beat services with their respective commands:
   - Worker: `sh scripts/start-worker.sh`
   - Beat: `sh scripts/start-beat.sh`

**Important Notes:**
- Render's free tier may spin down services after inactivity
- Ensure all environment variables are set before deployment
- Check deployment logs if services fail to start
- Database migrations run automatically on web service startup


## Deployment

### Render / Heroku

1. Set environment variables in your hosting platform
2. The app will automatically use `Procfile` for deployment
3. Run migrations after deployment:
```bash
flask db upgrade
flask seed_platforms
```

### Environment Variables Required

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `CREDENTIALS_ENCRYPTION_KEY` - Fernet key for credential encryption
- `CELERY_BROKER_URL` - Redis URL for Celery
- `CELERY_RESULT_BACKEND` - Redis URL for task results

**Optional:**
- `FLASK_ENV` - development or production
- `CORS_ORIGINS` - Comma-separated list of allowed origins
- `SMTP_USER` - SMTP username for email notifications
- `SMTP_PASS` - SMTP password
- `PROXY_SERVICE_URL` - Proxy service URL for scraping
- `PROXY_SERVICE_KEY` - Proxy service API key
- `MAX_APPLICATIONS_PER_HOUR` - Rate limit (default: 5)
- `MAX_APPLICATIONS_PER_DAY` - Daily limit (default: 20)

## Database Models

### Core Models
- **User** - User accounts and profiles
- **Resume** - User resumes with base64 storage
- **Platform** - Job board platforms
- **JobSearchConfig** - User job search preferences
- **Application** - Job application tracking
- **Subscription** - User subscription plans
- **Payment** - Billing history

### Automation Models
- **PlatformCredential** - Encrypted platform login credentials
- **JobQueue** - Queue of jobs to apply to
- **JobListing** - Cached discovered jobs
- **AutomationLog** - Audit trail of automation activities

## How Automation Works

### Background Job Processing

The automation system runs on a scheduled basis using Celery Beat:

1. **Job Scraping (Every 6 hours)**
   - Scrapes LinkedIn and Indeed for jobs matching user preferences
   - Uses AI-powered TF-IDF matching to score jobs (0-100)
   - Filters out duplicate jobs
   - Adds high-scoring jobs to user's queue

2. **Application Processing (Every 30 minutes)**
   - Processes pending jobs in the queue
   - Checks rate limits and subscription limits
   - Uses browser automation to apply to jobs
   - Updates application status and logs

3. **Status Monitoring (Every 4 hours)**
   - Checks application status updates
   - Sends email notifications for status changes

4. **Daily Summaries (8 AM daily)**
   - Sends email summary to all users
   - Includes yesterday's applications, pending jobs, and updates

5. **Cleanup (Daily at midnight)**
   - Removes old completed/failed queue items (>30 days)
   - Archives old automation logs (>90 days)

### Automation Workflow

```
User → Configure Job Search → System Scrapes Jobs → AI Matches Jobs → Queue High-Scoring Jobs → Bot Applies → Track Applications → Send Notifications
```

### Supported Platforms

**Fully Automated (Scraping + Application):**
- ✅ LinkedIn (Easy Apply only)
- ✅ Indeed

**Coming Soon:**
- Glassdoor
- Monster
- Dice
- ZipRecruiter

**Other Platforms (Manual tracking only):**
- Naukri Gulf
- Jobble
- CareerBuilder
- AngelList
- SimplyHired
- Remote.co
- We Work Remotely
- Stack Overflow Jobs
- GitHub Jobs
- FlexJobs

## Development

### Running Tests
```bash
# Add tests in tests/ directory
pytest
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

### Flask Shell
```bash
flask shell
# Access db, User, Resume, etc. in shell
```

## Security Considerations

### Credential Storage
- Platform credentials (LinkedIn, Indeed passwords) are encrypted using Fernet symmetric encryption
- Encryption key must be kept secret and never committed to version control
- Changing the encryption key will invalidate all stored credentials

### Rate Limiting
- Application submission is rate-limited to avoid detection
- Default: 5 applications per hour, 20 per day
- Configurable via environment variables
- Random delays between applications (3-5 minutes)

### Browser Automation
- Runs in headless mode by default
- User-agent rotation to appear more human
- Respects platform rate limits
- Handles CAPTCHAs gracefully (manual intervention required)

### Best Practices
- Use dedicated email accounts for automation
- Enable 2FA where possible
- Monitor automation logs regularly
- Set reasonable application limits
- Keep browser and drivers updated

## Monitoring

### Celery Flower (Optional)

Monitor Celery tasks with Flower:

```bash
celery -A celery_worker.celery flower --port=5555
```

Access at: `http://localhost:5555`

### Automation Logs

View automation activity:
```bash
# API endpoint
GET /api/automation/logs?limit=100

# Database query
flask shell
>>> AutomationLog.query.order_by(AutomationLog.created_at.desc()).limit(10).all()
```

## Troubleshooting

### Selenium/ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version

# Install matching ChromeDriver
# Download from: https://chromedriver.chromium.org/downloads
```

### Redis Connection Failed
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Restart Redis
sudo systemctl restart redis
```

### Celery Tasks Not Running
```bash
# Check Celery worker logs
celery -A celery_worker.celery worker --loglevel=debug

# Check Beat scheduler
celery -A celery_worker.celery beat --loglevel=debug

# Purge all tasks
celery -A celery_worker.celery purge
```

## License

MIT

## Support

For issues and questions, please create an issue in the repository.

For detailed automation documentation, see [AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md). 
