# DevApply Frontend Integration Guide

This document provides everything needed to build a frontend application that integrates with the DevApply backend API.

## Backend Overview

**DevApply Backend** is an AI-powered job application automation platform that:
- Automatically scrapes jobs from LinkedIn and Indeed
- Uses AI (TF-IDF) to match jobs with user preferences
- Applies to jobs automatically using browser automation
- Tracks all applications and sends email notifications
- Manages user accounts, resumes, and preferences

**Tech Stack:**
- Flask 3.0 REST API
- PostgreSQL database
- Celery + Redis for background jobs
- JWT authentication
- Selenium browser automation

**Deployment:** Render.com (Docker-based)

---

## Base URL

```
Development: http://localhost:5000
Production: https://your-app.onrender.com
```

All API endpoints are prefixed with `/api/`.

---

## Authentication

### JWT Token-Based Auth

The API uses JWT (JSON Web Tokens) for authentication.

**Token Types:**
- **Access Token**: Valid for 1 hour, used for API requests
- **Refresh Token**: Valid for 30 days, used to get new access tokens

**How to Use:**
1. User registers or logs in → Receive both tokens
2. Store tokens securely (localStorage or httpOnly cookies)
3. Include access token in request headers:
   ```
   Authorization: Bearer <access_token>
   ```
4. When access token expires → Use refresh token to get new access token

---

## API Endpoints

### 1. Authentication (`/api/auth`)

#### Register New User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "user@example.com",
      "email_verified": false,
      "full_name": "John Doe",
      "phone": "+1234567890",
      "created_at": "2025-11-15T07:21:14Z",
      ...
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "message": "User registered successfully"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):** Same as register

#### Get Current User Profile
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Update User Profile
```http
PUT /api/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Updated",
  "location": "New York, NY",
  "current_role": "Software Engineer",
  "years_experience": 5,
  "skills": ["Python", "JavaScript", "React"],
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "professional_bio": "Experienced software engineer..."
}
```

#### Upload Avatar
```http
POST /api/auth/upload-avatar
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "avatar_base64": "data:image/png;base64,iVBORw0KGgoAAAANS..."
}
```

#### Change Password
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

#### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```
**Note:** Always returns success to prevent user enumeration

#### Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "NewPassword789!"
}
```

#### Send Email Verification
```http
POST /api/auth/send-verification-email
Authorization: Bearer <access_token>
```

#### Verify Email
```http
POST /api/auth/verify-email
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```

#### Delete Account
```http
DELETE /api/auth/delete-account
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "password": "CurrentPassword123!"
}
```

#### Refresh Access Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "new-access-token"
  }
}
```

---

### 2. User Preferences (`/api/preferences`)

#### Get Preferences
```http
GET /api/preferences
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "preferences": {
      "email_notifications_enabled": true,
      "daily_summary_enabled": true,
      "application_updates_enabled": true,
      "job_matches_enabled": true,
      "marketing_emails_enabled": false,
      "auto_apply_enabled": true,
      "max_applications_per_day": 20,
      "min_match_score": 70,
      "timezone": "UTC",
      "language": "en",
      "currency": "USD"
    }
  }
}
```

#### Update Preferences
```http
PUT /api/preferences
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "daily_summary_enabled": false,
  "auto_apply_enabled": true,
  "max_applications_per_day": 30,
  "min_match_score": 80,
  "timezone": "America/New_York"
}
```

#### Reset Preferences to Defaults
```http
POST /api/preferences/reset
Authorization: Bearer <access_token>
```

---

### 3. Resumes (`/api/resumes`)

#### Upload Resume
```http
POST /api/resumes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "file_base64": "data:application/pdf;base64,JVBERi0xLjQ...",
  "filename": "John_Doe_Resume.pdf",
  "job_type": "Software Engineering",
  "is_default": true
}
```

**Supported formats:** PDF, DOC, DOCX

#### List All Resumes
```http
GET /api/resumes
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "id": "resume-uuid",
        "filename": "John_Doe_Resume.pdf",
        "file_type": "pdf",
        "file_size": 245678,
        "job_type": "Software Engineering",
        "is_default": true,
        "uploaded_at": "2025-11-15T07:21:14Z"
      }
    ]
  }
}
```

#### Get Specific Resume
```http
GET /api/resumes/{id}
Authorization: Bearer <access_token>
```

#### Download Resume (Base64)
```http
GET /api/resumes/{id}/download
Authorization: Bearer <access_token>
```

#### Set as Default Resume
```http
PUT /api/resumes/{id}/default
Authorization: Bearer <access_token>
```

#### Delete Resume
```http
DELETE /api/resumes/{id}
Authorization: Bearer <access_token>
```

---

### 4. Job Search Configuration (`/api/search-config`)

#### Create/Update Job Search Config
```http
POST /api/search-config
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_primary": true,
  "platforms": ["LinkedIn", "Indeed"],
  "job_title": "Software Engineer",
  "keywords": ["Python", "Backend", "API"],
  "location": "San Francisco, CA",
  "job_type": "full-time",
  "experience_level": "mid-level",
  "salary_min": 100000,
  "salary_max": 150000,
  "remote_preference": "hybrid",
  "resume_id": "resume-uuid"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "search_config": {
      "id": "config-uuid",
      "is_primary": true,
      "platforms": ["LinkedIn", "Indeed"],
      "job_title": "Software Engineer",
      ...
    }
  }
}
```

#### Get User's Search Configurations
```http
GET /api/search-config
Authorization: Bearer <access_token>
```

#### Update Search Config
```http
PUT /api/search-config/{id}
Authorization: Bearer <access_token>
```

#### Delete Search Config
```http
DELETE /api/search-config/{id}
Authorization: Bearer <access_token>
```

---

### 5. Applications (`/api/applications`)

#### List Applications
```http
GET /api/applications?status=sent&platform=LinkedIn&page=1&per_page=20
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: sent, viewed, interview, rejected, accepted
- `platform`: LinkedIn, Indeed, Glassdoor, etc.
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

**Response:**
```json
{
  "success": true,
  "data": {
    "applications": [
      {
        "id": "app-uuid",
        "job_title": "Senior Software Engineer",
        "company_name": "Tech Corp",
        "platform": "LinkedIn",
        "job_url": "https://linkedin.com/jobs/...",
        "location": "San Francisco, CA",
        "salary_range": "$120k - $180k",
        "status": "sent",
        "applied_at": "2025-11-15T07:21:14Z",
        "updated_at": "2025-11-15T07:21:14Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total_items": 45,
      "total_pages": 3
    }
  }
}
```

#### Get Dashboard Statistics
```http
GET /api/applications/stats
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "stats": {
      "total_applications": 45,
      "pending": 12,
      "sent": 20,
      "viewed": 8,
      "interview": 3,
      "rejected": 2,
      "this_week": 15,
      "this_month": 45,
      "avg_response_time": "3 days"
    }
  }
}
```

#### Create Manual Application
```http
POST /api/applications
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_title": "Software Engineer",
  "company_name": "Tech Startup",
  "platform": "Company Website",
  "job_url": "https://techstartup.com/careers/...",
  "location": "Remote",
  "status": "sent"
}
```

#### Update Application Status
```http
PUT /api/applications/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "interview",
  "notes": "Phone screen scheduled for next week"
}
```

#### Delete Application
```http
DELETE /api/applications/{id}
Authorization: Bearer <access_token>
```

---

### 6. Platform Credentials (`/api/credentials`)

**Note:** These are encrypted credentials for LinkedIn/Indeed automation.

#### Add Platform Credentials
```http
POST /api/credentials
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform": "linkedin",
  "username": "user@example.com",
  "password": "LinkedInPassword123"
}
```
**Supported platforms:** `linkedin`, `indeed`

#### List User Credentials
```http
GET /api/credentials
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "credentials": [
      {
        "id": "cred-uuid",
        "platform": "linkedin",
        "username": "user@example.com",
        "created_at": "2025-11-15T07:21:14Z"
      }
    ]
  }
}
```
**Note:** Password is never returned in responses

#### Update Credentials
```http
PUT /api/credentials/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "username": "newemail@example.com",
  "password": "NewPassword123"
}
```

#### Delete Credentials
```http
DELETE /api/credentials/{id}
Authorization: Bearer <access_token>
```

---

### 7. Automation Control (`/api/automation`)

#### View Job Queue
```http
GET /api/automation/queue?status=pending&page=1
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "queue_items": [
      {
        "id": "queue-uuid",
        "job_title": "Backend Engineer",
        "company_name": "Tech Company",
        "platform": "LinkedIn",
        "job_url": "https://...",
        "match_score": 85,
        "status": "pending",
        "priority": 8,
        "retry_count": 0,
        "created_at": "2025-11-15T07:21:14Z"
      }
    ]
  }
}
```

#### Get Automation Status
```http
GET /api/automation/status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": {
      "auto_apply_enabled": true,
      "pending_jobs": 12,
      "processing_jobs": 2,
      "applications_today": 5,
      "daily_limit": 20,
      "applications_this_hour": 2,
      "hourly_limit": 5,
      "last_run": "2025-11-15T07:00:00Z",
      "next_run": "2025-11-15T07:30:00Z"
    }
  }
}
```

#### List Discovered Jobs
```http
GET /api/automation/discovered-jobs?page=1&min_score=70
Authorization: Bearer <access_token>
```

#### Retry Failed Job
```http
POST /api/automation/queue/{id}/retry
Authorization: Bearer <access_token>
```

#### Remove from Queue
```http
DELETE /api/automation/queue/{id}
Authorization: Bearer <access_token>
```

#### View Automation Logs
```http
GET /api/automation/logs?limit=50&action=job_apply
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "id": "log-uuid",
        "action": "job_apply",
        "platform": "LinkedIn",
        "status": "success",
        "details": {
          "job_title": "Software Engineer",
          "company": "Tech Corp"
        },
        "created_at": "2025-11-15T07:21:14Z"
      }
    ]
  }
}
```

---

### 8. Subscription & Billing (`/api/subscription`)

#### Get Current Subscription
```http
GET /api/subscription
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "subscription": {
      "id": "sub-uuid",
      "plan_type": "free",
      "status": "active",
      "applications_limit": 10,
      "applications_used": 5,
      "billing_cycle": "monthly",
      "current_period_start": "2025-11-01T00:00:00Z",
      "current_period_end": "2025-12-01T00:00:00Z"
    }
  }
}
```

#### Get Available Plans
```http
GET /api/subscription/plans
```

**Response:**
```json
{
  "success": true,
  "data": {
    "plans": [
      {
        "name": "Free",
        "price": 0,
        "applications_limit": 10,
        "features": ["Manual tracking", "Basic analytics"]
      },
      {
        "name": "Pro",
        "price": 29,
        "applications_limit": 100,
        "features": ["Auto-apply", "AI matching", "Email notifications"]
      },
      {
        "name": "Max",
        "price": 99,
        "applications_limit": 500,
        "features": ["Everything in Pro", "Priority support", "Multiple resumes"]
      }
    ]
  }
}
```

#### Upgrade Plan
```http
POST /api/subscription/upgrade
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan_type": "pro",
  "billing_cycle": "monthly",
  "payment_method_id": "pm_123456789"
}
```

---

### 9. Job Platforms (`/api/platforms`)

#### List All Platforms
```http
GET /api/platforms
```

**Response:**
```json
{
  "success": true,
  "data": {
    "platforms": [
      {
        "id": "platform-uuid",
        "name": "LinkedIn",
        "website_url": "https://linkedin.com",
        "logo_url": "https://...",
        "is_supported": true,
        "supports_auto_apply": true,
        "category": "popular"
      },
      {
        "id": "platform-uuid-2",
        "name": "Indeed",
        "website_url": "https://indeed.com",
        "is_supported": true,
        "supports_auto_apply": true,
        "category": "popular"
      }
    ]
  }
}
```

---

### 10. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-15T07:21:14Z",
  "version": "1.0.0"
}
```

---

## Error Handling

All errors follow this format:

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

**Common Error Codes:**
- `VALIDATION_ERROR` (400): Invalid request data
- `INVALID_CREDENTIALS` (401): Wrong email/password
- `UNAUTHORIZED` (401): Missing or invalid token
- `FORBIDDEN` (403): Insufficient permissions
- `USER_NOT_FOUND` (404): User doesn't exist
- `RESOURCE_NOT_FOUND` (404): Requested resource not found
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error

---

## Rate Limiting

**Auth Endpoints:**
- Login: 5 attempts per 15 minutes
- Register: 5 attempts per 15 minutes
- Forgot Password: 3 attempts per hour
- Reset Password: 5 attempts per hour

**Other Endpoints:**
- Generally: 100 requests per minute per user

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699999999
```

---

## WebSocket Support (Future)

Currently not implemented, but planned for:
- Real-time application status updates
- Live automation progress
- Instant notifications

---

## Frontend Requirements

### Must-Have Features

1. **Authentication Flow**
   - Registration page
   - Login page
   - Password reset flow
   - Email verification prompt
   - OAuth buttons (Google, GitHub)

2. **Dashboard**
   - Application statistics (cards/charts)
   - Recent applications list
   - Quick actions (upload resume, configure search)
   - Automation status indicator

3. **User Profile**
   - Edit profile information
   - Upload/change avatar
   - Skills management
   - Social links (LinkedIn, GitHub, Portfolio)

4. **Resume Management**
   - Upload resumes (drag & drop)
   - List all resumes
   - Set default resume
   - Delete resumes
   - Download resumes

5. **Job Search Configuration**
   - Create primary/secondary searches
   - Select platforms (checkboxes)
   - Job preferences (title, location, salary, etc.)
   - Attach resume to search
   - Save/edit configurations

6. **Applications Tracker**
   - List view with filters (status, platform, date)
   - Search functionality
   - Status update (drag-drop or dropdown)
   - Add manual applications
   - Application details modal

7. **Platform Credentials**
   - Add LinkedIn credentials
   - Add Indeed credentials
   - Edit/delete credentials
   - Security warnings

8. **Automation Control**
   - Enable/disable auto-apply toggle
   - View job queue
   - Set application limits
   - View automation logs
   - Discovered jobs list with scores

9. **User Preferences**
   - Notification settings
   - Automation settings
   - Display preferences (timezone, language, currency)

10. **Subscription Management**
    - View current plan
    - Compare plans
    - Upgrade/downgrade
    - Payment method
    - Billing history

### Nice-to-Have Features

1. Calendar view for applications
2. Email integration (read responses)
3. Interview scheduler
4. Job recommendations feed
5. Analytics and insights
6. Export applications to CSV
7. Chrome extension
8. Mobile app

---

## Tech Stack Recommendations

### Frontend Framework
- **React** (recommended) - Most popular, great ecosystem
- **Next.js** - If you need SSR/SEO
- **Vue.js** - Simpler learning curve
- **Svelte** - Lightweight and fast

### UI Library
- **Material-UI (MUI)** - Comprehensive, professional
- **Tailwind CSS** - Utility-first, highly customizable
- **Chakra UI** - Accessible, themeable
- **Ant Design** - Enterprise-grade components

### State Management
- **React Context** - Built-in, good for medium apps
- **Redux Toolkit** - Industry standard, scalable
- **Zustand** - Lightweight, simple API
- **React Query** - Perfect for API state

### Form Handling
- **React Hook Form** - Performant, minimal re-renders
- **Formik** - Popular, well-documented

### HTTP Client
- **Axios** - Feature-rich, interceptors support
- **Fetch API** - Native, no dependencies

### Charts/Visualization
- **Recharts** - Simple, composable
- **Chart.js** - Flexible, lots of chart types
- **ApexCharts** - Modern, interactive

### File Upload
- **React Dropzone** - Drag & drop file uploads
- **Uppy** - Advanced file upload library

### Authentication
- **JWT Decode** - Decode JWT tokens
- **React Router** - Protected routes

---

## Sample API Integration (React)

### Setup Axios Instance

```javascript
// src/api/axios.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: Handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, null, {
          headers: { Authorization: `Bearer ${refreshToken}` },
        });

        const { access_token } = response.data.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### Authentication Service

```javascript
// src/services/authService.js
import apiClient from '../api/axios';

export const authService = {
  register: async (userData) => {
    const response = await apiClient.post('/api/auth/register', userData);
    const { access_token, refresh_token, user } = response.data.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  login: async (email, password) => {
    const response = await apiClient.post('/api/auth/login', { email, password });
    const { access_token, refresh_token, user } = response.data.data;

    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    localStorage.setItem('user', JSON.stringify(user));

    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/api/auth/me');
    return response.data.data.user;
  },

  updateProfile: async (userData) => {
    const response = await apiClient.put('/api/auth/me', userData);
    const updatedUser = response.data.data.user;
    localStorage.setItem('user', JSON.stringify(updatedUser));
    return response.data;
  },
};
```

### Resume Service

```javascript
// src/services/resumeService.js
import apiClient from '../api/axios';

export const resumeService = {
  uploadResume: async (file, jobType, isDefault = false) => {
    // Convert file to base64
    const base64 = await fileToBase64(file);

    const response = await apiClient.post('/api/resumes', {
      file_base64: base64,
      filename: file.name,
      job_type: jobType,
      is_default: isDefault,
    });

    return response.data;
  },

  listResumes: async () => {
    const response = await apiClient.get('/api/resumes');
    return response.data.data.resumes;
  },

  deleteResume: async (resumeId) => {
    await apiClient.delete(`/api/resumes/${resumeId}`);
  },

  setDefault: async (resumeId) => {
    const response = await apiClient.put(`/api/resumes/${resumeId}/default`);
    return response.data;
  },
};

// Helper function
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};
```

### Protected Route Component

```javascript
// src/components/ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';

export const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return children;
};
```

---

## UI/UX Recommendations

### Color Scheme
- **Primary**: Blue (#2563eb) - Trustworthy, professional
- **Secondary**: Green (#10b981) - Success, growth
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)
- **Background**: Light gray (#f9fafb)

### Typography
- **Headings**: Inter, SF Pro, or Poppins
- **Body**: System fonts or Inter

### Key Pages

1. **Login/Register**
   - Clean, centered form
   - Social login buttons
   - "Forgot password" link
   - Email verification notice

2. **Dashboard**
   - 4 stat cards at top (total apps, pending, interviews, success rate)
   - Line chart showing applications over time
   - Recent applications table
   - Quick action buttons

3. **Applications List**
   - Filterable table/cards
   - Status badges with colors
   - Search bar
   - Bulk actions

4. **Job Search Config**
   - Multi-step form or accordion
   - Platform selection with logos
   - Keyword chips/tags
   - Salary range slider

5. **Settings**
   - Tabbed interface
   - Profile, Preferences, Credentials, Subscription
   - Save indicator
   - Danger zone (delete account)

### Mobile Responsiveness
- All pages should work on mobile
- Hamburger menu for navigation
- Touch-friendly buttons
- Responsive tables (stack on mobile)

---

## Testing the API

### Using cURL

```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Get profile (replace TOKEN)
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

### Using Postman

1. Import this collection: (Create Postman collection with all endpoints)
2. Set environment variable `base_url` to `http://localhost:5000`
3. After login, set `access_token` from response
4. All protected endpoints will use the token automatically

---

## Common Issues & Solutions

### CORS Errors
Make sure frontend URL is in `CORS_ORIGINS` environment variable on backend.

### Token Expiration
Implement token refresh logic (see axios interceptor example above).

### File Upload Too Large
- Check backend `MAX_CONTENT_LENGTH` setting
- Validate file size on frontend before upload

### Rate Limiting
- Show user-friendly message
- Implement retry with exponential backoff

---

## Support & Resources

- **Backend Repository**: [GitHub Link]
- **API Documentation**: This document
- **Deployment Guide**: See DEPLOYMENT.md
- **Postman Collection**: [Link to collection]
- **Contact**: support@devapply.com

---

## Next Steps

1. **Set up frontend project**
2. **Implement authentication**
3. **Build dashboard**
4. **Add core features** (resumes, applications, job search)
5. **Integrate automation**
6. **Deploy frontend** (Vercel, Netlify, or Render)
7. **Connect to production backend**
8. **Test end-to-end**

Good luck building the DevApply frontend! 🚀
