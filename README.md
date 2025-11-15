# DevApply Backend API

AI-powered job application automation platform backend built with Flask, PostgreSQL, and JWT authentication.

## Features

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

## Tech Stack

- **Framework**: Flask 3.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Flask-Migrate (Alembic)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **CORS**: Flask-CORS
- **Rate Limiting**: Flask-Limiter

## Project Structure

```
devapply-backend/
├── app/
│   ├── __init__.py           # App factory and configuration
│   ├── config.py             # Configuration settings
│   ├── models/               # Database models
│   │   ├── user.py
│   │   ├── resume.py
│   │   ├── application.py
│   │   ├── job_search_config.py
│   │   ├── subscription.py
│   │   └── platform.py
│   ├── routes/               # API endpoints
│   │   ├── auth.py
│   │   ├── resumes.py
│   │   ├── applications.py
│   │   ├── search_config.py
│   │   ├── subscription.py
│   │   └── platforms.py
│   ├── utils/                # Utility functions
│   │   ├── validators.py
│   │   ├── auth_utils.py
│   │   └── file_utils.py
│   └── middleware/           # Custom middleware
│       └── auth_middleware.py
├── migrations/               # Database migrations
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── Procfile                  # Deployment configuration
└── .env                      # Environment variables
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL database
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd devapply-backend-hub
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://username:password@host:port/database
JWT_SECRET_KEY=your-secret-key-change-in-production
FLASK_APP=run.py
FLASK_ENV=development
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

5. Initialize the database:
```bash
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Seed initial data (platforms):
```bash
flask seed_platforms
```

7. Run the development server:
```bash
flask run
# Or
python run.py
```

The API will be available at `http://localhost:5000`

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
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET_KEY` - Secret key for JWT tokens
- `FLASK_ENV` - production
- `CORS_ORIGINS` - Comma-separated list of allowed origins

## Database Models

- **User** - User accounts and profiles
- **Resume** - User resumes with base64 storage
- **Platform** - Job board platforms
- **JobSearchConfig** - User job search preferences
- **Application** - Job application tracking
- **Subscription** - User subscription plans
- **Payment** - Billing history

## Available Job Platforms

Popular:
- LinkedIn
- Indeed
- Glassdoor

Others:
- Monster
- Naukri Gulf
- Jobble
- Dice
- CareerBuilder
- AngelList
- SimplyHired
- Remote.co
- We Work Remotely
- Stack Overflow Jobs
- GitHub Jobs
- ZipRecruiter
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

## License

MIT

## Support

For issues and questions, please create an issue in the repository. 
