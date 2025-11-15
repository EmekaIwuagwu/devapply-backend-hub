# DevApply Backend Integration Guide

## Backend Configuration

**Production Backend URL:** `https://devapply-backend.onrender.com`

**API Base URL:** `https://devapply-backend.onrender.com/api`

**Health Check:** `https://devapply-backend.onrender.com/health`

---

## Integration Steps

### Step 1: Configure API Base URL

Update your frontend configuration/environment file:

```javascript
// .env or config file
VITE_API_BASE_URL=https://devapply-backend.onrender.com/api
# or
REACT_APP_API_BASE_URL=https://devapply-backend.onrender.com/api
# or
NEXT_PUBLIC_API_BASE_URL=https://devapply-backend.onrender.com/api
```

In your API client/service:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://devapply-backend.onrender.com/api';
```

---

### Step 2: API Response Format

All backend responses follow this standard structure:

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Your data here
  },
  "message": "Operation successful"
}
```

**Error Response:**
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

**Update your API client to handle this:**
```javascript
async function apiCall(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    const result = await response.json();

    if (!result.success) {
      throw new Error(result.error?.message || 'Request failed');
    }

    return result.data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}
```

---

### Step 3: Authentication Integration

#### JWT Token Storage and Management

**After successful login/registration, store tokens:**
```javascript
// Login/Register response structure
{
  "success": true,
  "data": {
    "user": { /* user object */ },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}

// Store tokens
localStorage.setItem('access_token', data.access_token);
localStorage.setItem('refresh_token', data.refresh_token);
localStorage.setItem('user', JSON.stringify(data.user));
```

**Add token to all authenticated requests:**
```javascript
const token = localStorage.getItem('access_token');

fetch(`${API_BASE_URL}/endpoint`, {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  }
});
```

**Implement token refresh on 401:**
```javascript
async function apiCallWithAuth(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');

  let response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  // If 401, try to refresh token
  if (response.status === 401) {
    const refreshToken = localStorage.getItem('refresh_token');

    const refreshResponse = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${refreshToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (refreshResponse.ok) {
      const { data } = await refreshResponse.json();
      localStorage.setItem('access_token', data.access_token);

      // Retry original request
      response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
          'Authorization': `Bearer ${data.access_token}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
    } else {
      // Refresh failed, redirect to login
      localStorage.clear();
      window.location.href = '/login';
      throw new Error('Session expired');
    }
  }

  const result = await response.json();

  if (!result.success) {
    throw new Error(result.error?.message || 'Request failed');
  }

  return result.data;
}
```

**On logout:**
```javascript
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

---

### Step 4: API Endpoint Mapping

Map your frontend functions to these backend endpoints:

#### Authentication Endpoints

```javascript
// Register
POST /api/auth/register
Body: { email, password, full_name, phone }
Response: { user, access_token, refresh_token }

// Login
POST /api/auth/login
Body: { email, password }
Response: { user, access_token, refresh_token }

// Google OAuth
POST /api/auth/google
Body: { oauth_id, email, full_name }
Response: { user, access_token, refresh_token }

// GitHub OAuth
POST /api/auth/github
Body: { oauth_id, email, full_name }
Response: { user, access_token, refresh_token }

// Get Profile
GET /api/auth/me
Headers: Authorization: Bearer {token}
Response: { user }

// Update Profile
PUT /api/auth/me
Headers: Authorization: Bearer {token}
Body: { full_name, phone, location, linkedin_url, github_url, portfolio_url, current_role, years_experience, preferred_job_type, salary_expectations, professional_bio, skills }
Response: { user }

// Upload Avatar
POST /api/auth/upload-avatar
Headers: Authorization: Bearer {token}
Body: { avatar_base64: "data:image/png;base64,..." }
Response: { user }

// Change Password
POST /api/auth/change-password
Headers: Authorization: Bearer {token}
Body: { current_password, new_password }

// Forgot Password
POST /api/auth/forgot-password
Body: { email }

// Reset Password
POST /api/auth/reset-password
Body: { token, new_password }

// Verify Email
POST /api/auth/verify-email
Body: { token }

// Delete Account
DELETE /api/auth/delete-account
Headers: Authorization: Bearer {token}
Body: { password }
```

#### Resume Endpoints

```javascript
// Upload Resume
POST /api/resumes
Headers: Authorization: Bearer {token}
Body: { filename, file_base64, is_default, job_type_tag }
Response: { resume }

// Get All Resumes
GET /api/resumes
Headers: Authorization: Bearer {token}
Response: { resumes: [...], count: number }

// Get Single Resume
GET /api/resumes/{resume_id}
Headers: Authorization: Bearer {token}
Response: { resume }

// Download Resume
GET /api/resumes/{resume_id}/download
Headers: Authorization: Bearer {token}
Response: { resume: { ...resume, file_base64 } }

// Set Default Resume
PUT /api/resumes/{resume_id}/default
Headers: Authorization: Bearer {token}
Response: { resume }

// Delete Resume
DELETE /api/resumes/{resume_id}
Headers: Authorization: Bearer {token}
```

#### Application Endpoints

```javascript
// Create Application
POST /api/applications
Headers: Authorization: Bearer {token}
Body: { company_name, job_title, job_type, location, salary_range, status, platform, job_url, resume_used_id, cover_letter, notes }
Response: { application }

// Get All Applications (with filters)
GET /api/applications?status={status}&platform={platform}&search={query}&sort={sort}&page={page}&limit={limit}
Headers: Authorization: Bearer {token}
Response: { applications: [...], pagination: { page, limit, total, pages } }

// Get Single Application
GET /api/applications/{application_id}
Headers: Authorization: Bearer {token}
Response: { application }

// Update Application
PUT /api/applications/{application_id}
Headers: Authorization: Bearer {token}
Body: { status, notes, cover_letter, job_type, location, salary_range }
Response: { application }

// Delete Application
DELETE /api/applications/{application_id}
Headers: Authorization: Bearer {token}

// Get Application Statistics
GET /api/applications/stats
Headers: Authorization: Bearer {token}
Response: { total_applications, status_breakdown, platform_breakdown, recent_applications }
```

#### Platform Credentials

```javascript
// Get All Credentials
GET /api/credentials
Headers: Authorization: Bearer {token}
Response: { credentials: [...] }

// Add/Update Credential
POST /api/credentials
Headers: Authorization: Bearer {token}
Body: { platform, username, password }
Response: { credential }

// Delete Credential
DELETE /api/credentials/{platform}
Headers: Authorization: Bearer {token}

// Verify Credential
POST /api/credentials/{platform}/verify
Headers: Authorization: Bearer {token}
Response: { credential }
```

#### Search Configuration

```javascript
// Get Configuration
GET /api/search-config
Headers: Authorization: Bearer {token}
Response: { config }

// Create/Update Configuration
POST /api/search-config
Headers: Authorization: Bearer {token}
Body: { platforms, primary_job_title, primary_location, primary_min_salary, primary_experience_level, primary_keywords, primary_resume_id, secondary_job_title, secondary_location, secondary_min_salary, secondary_experience_level, secondary_keywords, secondary_resume_id, is_active }
Response: { config }

// Update Configuration
PUT /api/search-config/{config_id}
Headers: Authorization: Bearer {token}
Body: { /* any config fields */ }
Response: { config }

// Delete Configuration
DELETE /api/search-config/{config_id}
Headers: Authorization: Bearer {token}
```

#### Automation & Queue

```javascript
// Get Job Queue
GET /api/automation/queue?status={status}&page={page}&limit={limit}
Headers: Authorization: Bearer {token}
Response: { jobs: [...], pagination }

// Skip Job
POST /api/automation/queue/{job_id}/skip
Headers: Authorization: Bearer {token}
Response: { job }

// Update Job Priority
PUT /api/automation/queue/{job_id}/priority
Headers: Authorization: Bearer {token}
Body: { priority: 1-10 }
Response: { job }

// Remove from Queue
DELETE /api/automation/queue/{job_id}
Headers: Authorization: Bearer {token}

// Get Automation Status
GET /api/automation/status
Headers: Authorization: Bearer {token}
Response: { queue_stats, rate_limits, next_scheduled_job, is_active }

// Get Automation Logs
GET /api/automation/logs?action_type={type}&status={status}&page={page}&limit={limit}
Headers: Authorization: Bearer {token}
Response: { logs: [...], pagination }

// Get Discovered Jobs
GET /api/automation/discovered-jobs?platform={platform}&page={page}&limit={limit}
Headers: Authorization: Bearer {token}
Response: { jobs: [...], pagination }

// Queue Discovered Job
POST /api/automation/discovered-jobs/{job_id}/queue
Headers: Authorization: Bearer {token}
Response: { queue_item }
```

#### Subscription

```javascript
// Get Current Subscription
GET /api/subscription
Headers: Authorization: Bearer {token}
Response: { subscription }

// Get Available Plans
GET /api/subscription/plans
Response: { plans: { free, pro, max } }

// Upgrade Plan
POST /api/subscription/upgrade
Headers: Authorization: Bearer {token}
Body: { plan_type: "pro"|"max", billing_cycle: "monthly"|"yearly" }
Response: { subscription }

// Downgrade Plan
POST /api/subscription/downgrade
Headers: Authorization: Bearer {token}
Body: { plan_type: "free" }
Response: { subscription }

// Cancel Subscription
POST /api/subscription/cancel
Headers: Authorization: Bearer {token}
Response: { subscription }

// Add Payment Method
POST /api/subscription/payment/method
Headers: Authorization: Bearer {token}
Body: { last4, expiry, brand }
Response: { payment_method }

// Get Payment History
GET /api/subscription/payment/history?page={page}&limit={limit}
Headers: Authorization: Bearer {token}
Response: { payments: [...], pagination }

// Get Invoice
GET /api/subscription/payment/invoice/{invoice_id}
Headers: Authorization: Bearer {token}
Response: { payment }
```

#### Preferences

```javascript
// Get Preferences
GET /api/preferences
Headers: Authorization: Bearer {token}
Response: { preferences }

// Update Preferences
PUT /api/preferences
Headers: Authorization: Bearer {token}
Body: { email_notifications_enabled, daily_summary_enabled, application_updates_enabled, job_matches_enabled, marketing_emails_enabled, auto_apply_enabled, max_applications_per_day, min_match_score, timezone, language, currency }
Response: { preferences }

// Reset Preferences
POST /api/preferences/reset
Headers: Authorization: Bearer {token}
Response: { preferences }
```

#### Platforms

```javascript
// Get Available Platforms
GET /api/platforms
Response: { popular: [...], others: [...], all: [...] }
```

---

### Step 5: File Upload Integration

**For Resume and Avatar uploads, convert files to base64:**

```javascript
async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });
}

// Usage for Resume Upload
async function uploadResume(file, isDefault = false, jobTypeTag = '') {
  // Validate file size (max 10MB)
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('File size exceeds 10MB');
  }

  // Validate file type
  const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Only PDF, DOC, and DOCX files are allowed');
  }

  const base64 = await fileToBase64(file);

  return apiCallWithAuth('/resumes', {
    method: 'POST',
    body: JSON.stringify({
      filename: file.name,
      file_base64: base64,
      is_default: isDefault,
      job_type_tag: jobTypeTag
    })
  });
}

// Usage for Avatar Upload
async function uploadAvatar(file) {
  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    throw new Error('File size exceeds 5MB');
  }

  // Validate file type
  const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg'];
  if (!allowedTypes.includes(file.type)) {
    throw new Error('Only JPG and PNG images are allowed');
  }

  const base64 = await fileToBase64(file);

  return apiCallWithAuth('/auth/upload-avatar', {
    method: 'POST',
    body: JSON.stringify({
      avatar_base64: base64
    })
  });
}
```

---

### Step 6: Error Handling

**Map backend error codes to user-friendly messages:**

```javascript
const ERROR_MESSAGES = {
  'VALIDATION_ERROR': 'Please check your input and try again',
  'USER_EXISTS': 'An account with this email already exists',
  'INVALID_CREDENTIALS': 'Invalid email or password',
  'USER_NOT_FOUND': 'User not found',
  'INVALID_TOKEN': 'Invalid or expired token',
  'FILE_TOO_LARGE': 'File size is too large',
  'INVALID_FILE_TYPE': 'Invalid file type',
  'APPLICATION_NOT_FOUND': 'Application not found',
  'RESUME_NOT_FOUND': 'Resume not found',
  'SUBSCRIPTION_NOT_FOUND': 'Subscription not found',
  // Add more as needed
};

function handleApiError(error) {
  const errorCode = error.error?.code;
  const errorMessage = ERROR_MESSAGES[errorCode] || error.error?.message || 'An error occurred';

  // Show toast/notification
  showNotification('error', errorMessage);

  return errorMessage;
}
```

**Rate Limiting Handling:**

The backend has rate limits on certain endpoints:
- Registration: 5 per 15 minutes
- Login: 5 per 15 minutes
- Forgot Password: 3 per hour
- Reset Password: 5 per hour

Handle 429 (Too Many Requests) responses:
```javascript
if (response.status === 429) {
  showNotification('error', 'Too many requests. Please try again later.');
}
```

---

### Step 7: Data Structure Reference

**User Object:**
```javascript
{
  id: "uuid",
  email: "user@example.com",
  full_name: "John Doe",
  phone: "+1234567890",
  location: "San Francisco, CA",
  linkedin_url: "https://linkedin.com/in/johndoe",
  github_url: "https://github.com/johndoe",
  portfolio_url: "https://johndoe.com",
  current_role: "Software Engineer",
  years_experience: 5,
  preferred_job_type: "remote",
  salary_expectations: "$100,000 - $150,000",
  professional_bio: "Experienced developer...",
  skills: ["JavaScript", "Python", "React"],
  avatar_base64: "data:image/png;base64,...",
  email_verified: true,
  created_at: "2025-11-15T00:00:00Z"
}
```

**Application Object:**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  company_name: "Tech Corp",
  job_title: "Senior Software Engineer",
  job_type: "Full-time",
  location: "San Francisco, CA",
  salary_range: "$120,000 - $160,000",
  status: "sent", // sent, interviewing, rejected, accepted
  platform: "linkedin",
  job_url: "https://linkedin.com/jobs/123",
  resume_used_id: "uuid",
  cover_letter: "Dear hiring manager...",
  notes: "Applied through referral",
  applied_at: "2025-11-15T00:00:00Z",
  last_status_update: "2025-11-15T00:00:00Z"
}
```

**Resume Object:**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  filename: "John_Doe_Resume.pdf",
  file_type: "pdf",
  file_size: 1024000,
  file_base64: "base64_string...", // Only in download response
  is_default: true,
  job_type_tag: "Software Engineer",
  uploaded_at: "2025-11-15T00:00:00Z"
}
```

**Subscription Object:**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  plan_type: "free", // free, pro, max
  status: "active", // active, cancelled, expired
  applications_limit: 10,
  applications_used: 5,
  billing_cycle: "monthly", // monthly, yearly, null for free
  amount: 29.99,
  currency: "USD",
  next_billing_date: "2025-12-15",
  created_at: "2025-11-15T00:00:00Z",
  cancelled_at: null
}
```

**Credential Object:**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  platform: "linkedin",
  username: "user@example.com",
  is_active: true,
  last_verified: "2025-11-15T00:00:00Z",
  created_at: "2025-11-15T00:00:00Z"
  // password is never returned
}
```

**Preferences Object:**
```javascript
{
  id: "uuid",
  user_id: "uuid",
  email_notifications_enabled: true,
  daily_summary_enabled: true,
  application_updates_enabled: true,
  job_matches_enabled: true,
  marketing_emails_enabled: false,
  auto_apply_enabled: false,
  max_applications_per_day: 10,
  min_match_score: 70,
  timezone: "America/New_York",
  language: "en",
  currency: "USD"
}
```

---

### Step 8: Integration Checklist

**Update these in your frontend code:**

- [ ] Update API base URL to `https://devapply-backend.onrender.com/api`
- [ ] Update response handler to expect `{ success, data, message, error }` structure
- [ ] Add Authorization header with Bearer token to all authenticated requests
- [ ] Implement token refresh logic on 401 responses
- [ ] Store tokens in localStorage after login/register
- [ ] Clear tokens on logout
- [ ] Update all endpoint URLs to match backend routes
- [ ] Convert files to base64 before upload
- [ ] Handle error responses and show user-friendly messages
- [ ] Test all CRUD operations (Create, Read, Update, Delete)
- [ ] Test file uploads (resumes and avatars)
- [ ] Test filters and pagination on list endpoints
- [ ] Test authentication flow (register, login, logout, password reset)
- [ ] Test OAuth flows (Google, GitHub)
- [ ] Handle rate limiting (429 responses)
- [ ] Test with network errors
- [ ] Test token expiration and refresh

---

### Step 9: Testing Your Integration

**1. Test Backend Connectivity:**
```javascript
fetch('https://devapply-backend.onrender.com/health')
  .then(res => res.json())
  .then(data => console.log(data))
  // Should return: { success: true, data: { status: "healthy", service: "DevApply Backend" } }
```

**2. Test Registration:**
```javascript
fetch('https://devapply-backend.onrender.com/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'test@test.com',
    password: 'Test123!@#',
    full_name: 'Test User'
  })
})
  .then(res => res.json())
  .then(data => {
    console.log(data);
    // Store tokens
    localStorage.setItem('access_token', data.data.access_token);
    localStorage.setItem('refresh_token', data.data.refresh_token);
  })
```

**3. Test Authenticated Endpoint:**
```javascript
const token = localStorage.getItem('access_token');

fetch('https://devapply-backend.onrender.com/api/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
  .then(res => res.json())
  .then(data => console.log(data))
```

**4. Test Application Creation:**
```javascript
const token = localStorage.getItem('access_token');

fetch('https://devapply-backend.onrender.com/api/applications', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    company_name: 'Test Company',
    job_title: 'Software Engineer',
    platform: 'linkedin',
    status: 'sent'
  })
})
  .then(res => res.json())
  .then(data => console.log(data))
```

---

### Step 10: Common Integration Issues & Solutions

**Issue 1: CORS Errors**
- **Solution:** The backend has CORS enabled. Ensure you're making requests from your allowed origin.

**Issue 2: 401 Unauthorized**
- **Solution:** Verify the token is valid and included in the Authorization header as `Bearer {token}`

**Issue 3: 404 Not Found**
- **Solution:** Check that the endpoint URL is correct and includes `/api` prefix

**Issue 4: File Upload Fails**
- **Solution:** Ensure file is converted to base64 and includes the data URL prefix (e.g., `data:application/pdf;base64,`)

**Issue 5: Token Expired**
- **Solution:** Implement token refresh logic using the refresh token at `/api/auth/refresh`

**Issue 6: Rate Limit Exceeded (429)**
- **Solution:** Show user-friendly message and implement retry with exponential backoff

---

## Quick Reference

**Backend URL:** `https://devapply-backend.onrender.com`

**API Base:** `https://devapply-backend.onrender.com/api`

**Auth Header:** `Authorization: Bearer {access_token}`

**Response Format:** `{ success: boolean, data: object, message: string, error: object }`

**Token Storage:** `localStorage` (access_token, refresh_token)

**File Upload:** Convert to base64 before sending

**Pagination:** Use `page` and `limit` query parameters

**Filtering:** Use query parameters (e.g., `?status=sent&platform=linkedin`)

---

## Next Steps

1. Update your frontend API client configuration
2. Test each endpoint individually
3. Update response handlers to match backend format
4. Implement authentication token management
5. Test file uploads
6. Test error handling
7. Perform end-to-end testing of all features

The backend is fully deployed, tested, and ready for integration! 🚀
