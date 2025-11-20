# API Endpoints Reference - Quick Integration Guide

This is a **quick reference** for the actual backend implementation. Use this for frontend integration.

## Base URL

```
Development: http://localhost:5000
Production: https://devapply-backend.onrender.com
```

All endpoints use `/api` prefix.

---

## Authentication Endpoints

### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",      // optional
  "phone": "+1234567890"         // optional
}
```

### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Update Profile
```http
PUT /api/auth/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "New York, NY",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "portfolio_url": "https://johndoe.com",
  "current_role": "Software Engineer",
  "years_experience": 5,
  "preferred_job_type": "full-time",
  "salary_expectations": "$100k-$150k",
  "professional_bio": "Experienced developer...",
  "skills": ["Python", "JavaScript", "React"]  // Array of strings
}
```

### Upload Avatar
```http
POST /api/auth/upload-avatar
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "avatar_base64": "data:image/png;base64,iVBORw0KGgo..."
}
```

### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

---

## Resume Endpoints

### ⚠️ IMPORTANT: Upload Resume

**Correct Endpoint:** `POST /api/resumes` (NOT `/api/resumes/upload`)

**Correct Request Format:**
```http
POST /api/resumes
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "filename": "John_Doe_Resume.pdf",           // REQUIRED
  "file_base64": "data:application/pdf;base64,JVBERi0xLjQ...",  // REQUIRED (NOT "content")
  "is_default": true,                          // OPTIONAL (default: false)
  "job_type_tag": "Software Engineering"       // OPTIONAL
}
```

**❌ Common Mistakes:**
```json
// DON'T send this:
{
  "filename": "resume.pdf",
  "content": "base64...",      // ❌ Wrong! Use "file_base64"
  "contentType": "application/pdf"  // ❌ Not used, determined from filename
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "resume": {
      "id": "uuid",
      "filename": "John_Doe_Resume.pdf",
      "file_type": "pdf",
      "file_size": 245678,
      "is_default": true,
      "job_type_tag": "Software Engineering",
      "uploaded_at": "2025-11-15T10:00:00Z"
    }
  },
  "message": "Resume uploaded successfully"
}
```

**Validation Rules:**
- **Max file size:** 5MB
- **Allowed types:** pdf, doc, docx
- **Base64 format:** Must include data URI prefix (e.g., `data:application/pdf;base64,`)

### List Resumes
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
        "id": "uuid",
        "filename": "resume.pdf",
        "file_type": "pdf",
        "file_size": 245678,
        "is_default": true,
        "job_type_tag": "Software Engineering",
        "uploaded_at": "2025-11-15T10:00:00Z"
      }
    ],
    "count": 1
  }
}
```

### Get Specific Resume
```http
GET /api/resumes/{resume_id}
Authorization: Bearer <access_token>
```

### Download Resume (with base64)
```http
GET /api/resumes/{resume_id}/download
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "resume": {
      "id": "uuid",
      "filename": "resume.pdf",
      "file_base64": "data:application/pdf;base64,JVBERi0xLjQ...",
      "file_type": "pdf",
      "file_size": 245678,
      "is_default": true,
      "uploaded_at": "2025-11-15T10:00:00Z"
    }
  }
}
```

### Set as Default
```http
PUT /api/resumes/{resume_id}/default
Authorization: Bearer <access_token>
```

### Delete Resume
```http
DELETE /api/resumes/{resume_id}
Authorization: Bearer <access_token>
```

---

## Job Search Config Endpoints

### Create/Update Search Config
```http
POST /api/search-config
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "is_primary": true,
  "platforms": ["LinkedIn", "Indeed"],               // Array (NOT JSON string)
  "job_title": "Software Engineer",
  "keywords": ["Python", "Backend", "API"],          // Array (NOT JSON string)
  "location": "San Francisco, CA",
  "job_type": "full-time",
  "experience_level": "mid-level",
  "salary_min": 100000,
  "salary_max": 150000,
  "remote_preference": "hybrid",
  "resume_id": "resume-uuid"
}
```

**⚠️ IMPORTANT:** `platforms` and `keywords` must be sent as **arrays**, not JSON strings:
```javascript
// ✅ Correct
{ "platforms": ["LinkedIn", "Indeed"] }

// ❌ Wrong
{ "platforms": '["LinkedIn", "Indeed"]' }
{ "platforms": "LinkedIn,Indeed" }
```

### Get User's Configs
```http
GET /api/search-config
Authorization: Bearer <access_token>
```

### Update Config
```http
PUT /api/search-config/{config_id}
Authorization: Bearer <access_token>
```

### Delete Config
```http
DELETE /api/search-config/{config_id}
Authorization: Bearer <access_token>
```

---

## Applications Endpoints

### List Applications
```http
GET /api/applications?status=sent&platform=LinkedIn&page=1&per_page=20
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: sent | viewed | interview | rejected | accepted
- `platform`: LinkedIn | Indeed | Glassdoor | etc.
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)

### Get Dashboard Stats
```http
GET /api/applications/stats
Authorization: Bearer <access_token>
```

### Create Application
```http
POST /api/applications
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "platform": "LinkedIn",
  "job_url": "https://...",
  "location": "Remote",
  "salary_range": "$120k-$180k",
  "status": "sent",
  "resume_used_id": "resume-uuid",  // optional
  "cover_letter": "...",             // optional
  "notes": "..."                     // optional
}
```

### Update Application
```http
PUT /api/applications/{application_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "interview",
  "notes": "Phone screen scheduled"
}
```

### Delete Application
```http
DELETE /api/applications/{application_id}
Authorization: Bearer <access_token>
```

---

## Platform Credentials Endpoints

### Add Credentials
```http
POST /api/credentials
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "platform": "linkedin",  // linkedin | indeed
  "username": "user@example.com",
  "password": "LinkedInPass123"
}
```

### List Credentials
```http
GET /api/credentials
Authorization: Bearer <access_token>
```

**Response (passwords never returned):**
```json
{
  "success": true,
  "data": {
    "credentials": [
      {
        "id": "uuid",
        "platform": "linkedin",
        "username": "user@example.com",
        "created_at": "2025-11-15T10:00:00Z"
      }
    ]
  }
}
```

### Delete Credentials
```http
DELETE /api/credentials/{platform}
Authorization: Bearer <access_token>
```

---

## Automation Endpoints

### View Queue
```http
GET /api/automation/queue?status=pending&page=1
Authorization: Bearer <access_token>
```

### Get Status
```http
GET /api/automation/status
Authorization: Bearer <access_token>
```

### Get Logs
```http
GET /api/automation/logs?limit=50&action=job_apply
Authorization: Bearer <access_token>
```

### Discovered Jobs
```http
GET /api/automation/discovered-jobs?page=1&min_score=70
Authorization: Bearer <access_token>
```

### Skip Job
```http
POST /api/automation/queue/{job_id}/skip
Authorization: Bearer <access_token>
```

### Remove from Queue
```http
DELETE /api/automation/queue/{job_id}
Authorization: Bearer <access_token>
```

---

## User Preferences Endpoints

### Get Preferences
```http
GET /api/preferences
Authorization: Bearer <access_token>
```

### Update Preferences
```http
PUT /api/preferences
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email_notifications_enabled": true,
  "daily_summary_enabled": true,
  "auto_apply_enabled": true,
  "max_applications_per_day": 20,
  "min_match_score": 70,
  "timezone": "America/New_York",
  "language": "en",
  "currency": "USD"
}
```

### Reset to Defaults
```http
POST /api/preferences/reset
Authorization: Bearer <access_token>
```

---

## Subscription Endpoints

### Get Current Subscription
```http
GET /api/subscription
Authorization: Bearer <access_token>
```

### Get Available Plans
```http
GET /api/subscription/plans
```

### Upgrade Plan
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

## Platform Endpoints

### List All Platforms
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
        "id": "uuid",
        "name": "LinkedIn",
        "website_url": "https://linkedin.com",
        "is_supported": true,
        "supports_auto_apply": true
      }
    ]
  }
}
```

---

## Error Response Format

All errors follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` (400) - Invalid request data
- `INVALID_CREDENTIALS` (401) - Wrong email/password
- `UNAUTHORIZED` (401) - Missing/invalid token
- `FORBIDDEN` (403) - Insufficient permissions
- `USER_NOT_FOUND` (404) - User doesn't exist
- `RESUME_NOT_FOUND` (404) - Resume doesn't exist
- `RATE_LIMIT_EXCEEDED` (429) - Too many requests
- `UPLOAD_FAILED` (500) - File upload error
- `INTERNAL_ERROR` (500) - Server error

---

## Success Response Format

All successful responses follow this structure:

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "message": "Operation successful",  // optional
  "meta": {
    "timestamp": "2025-11-15T10:00:00Z"
  }
}
```

---

## Frontend Integration Checklist

### Resume Upload Integration
```javascript
// ✅ Correct Implementation
const uploadResume = async (file, isDefault = false, jobTypeTag = null) => {
  // Convert to base64
  const base64 = await fileToBase64(file);

  // Send to backend
  const response = await apiClient.post('/api/resumes', {  // NOT /api/resumes/upload
    filename: file.name,
    file_base64: base64,      // NOT "content"
    is_default: isDefault,
    job_type_tag: jobTypeTag
  });

  return response.data.data.resume;
};

// Helper function
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
  });
};
```

### Profile Update with Skills
```javascript
// ✅ Correct - Send array directly
await apiClient.put('/api/auth/me', {
  skills: ['Python', 'JavaScript', 'React']  // Array, not string
});

// ❌ Wrong
await apiClient.put('/api/auth/me', {
  skills: 'Python,JavaScript,React'  // String - won't work
});
```

### Job Search Config
```javascript
// ✅ Correct - Arrays for platforms and keywords
await apiClient.post('/api/search-config', {
  platforms: ['LinkedIn', 'Indeed'],
  keywords: ['Python', 'Backend', 'API']
});

// ❌ Wrong
await apiClient.post('/api/search-config', {
  platforms: 'LinkedIn,Indeed',  // String - won't work
  keywords: '["Python", "Backend"]'  // JSON string - won't work
});
```

---

## Testing with cURL

### Test Resume Upload
```bash
# Get token first
TOKEN="your-access-token-here"

# Upload resume (make sure base64 includes data URI prefix)
curl -X POST http://localhost:5000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "resume.pdf",
    "file_base64": "data:application/pdf;base64,JVBERi0xLjQ...",
    "is_default": true,
    "job_type_tag": "Software Engineering"
  }'
```

---

## Need Help?

- **Backend not responding:** Check if server is running on correct port
- **CORS errors:** Set `CORS_ORIGINS` environment variable
- **401 errors:** Token expired, use refresh token
- **400 errors:** Check request payload format matches this guide
- **File upload fails:** Ensure base64 includes data URI prefix

See `FRONTEND_TROUBLESHOOTING.md` for detailed debugging guide.
