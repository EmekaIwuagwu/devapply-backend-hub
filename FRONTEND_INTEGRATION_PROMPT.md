# DevApply Frontend Integration Guide

## Backend Information

**Production Backend URL:** `https://devapply-backend.onrender.com`

**API Base URL:** `https://devapply-backend.onrender.com/api`

## Important Integration Requirements

### 1. Authentication System
All authenticated endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

### 2. Standard Response Format
All API responses follow this structure:

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  }
}
```

---

## API Endpoints Documentation

### Authentication Endpoints (`/api/auth`)

#### 1. User Registration
- **Endpoint:** `POST /api/auth/register`
- **Rate Limit:** 5 per 15 minutes
- **Public Access:** Yes
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+1234567890"
}
```
- **Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "email_verified": false,
      "created_at": "2025-11-15T00:00:00Z"
    },
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  },
  "message": "User registered successfully"
}
```

#### 2. User Login
- **Endpoint:** `POST /api/auth/login`
- **Rate Limit:** 5 per 15 minutes
- **Public Access:** Yes
- **Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### 3. Google OAuth Login
- **Endpoint:** `POST /api/auth/google`
- **Public Access:** Yes
- **Request Body:**
```json
{
  "oauth_id": "google_oauth_id",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### 4. GitHub OAuth Login
- **Endpoint:** `POST /api/auth/github`
- **Public Access:** Yes
- **Request Body:**
```json
{
  "oauth_id": "github_oauth_id",
  "email": "user@example.com",
  "full_name": "John Doe"
}
```

#### 5. Get User Profile
- **Endpoint:** `GET /api/auth/me`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "phone": "+1234567890",
      "location": "New York, NY",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "github_url": "https://github.com/johndoe",
      "portfolio_url": "https://johndoe.com",
      "current_role": "Software Engineer",
      "years_experience": 5,
      "preferred_job_type": "remote",
      "salary_expectations": "$100,000 - $150,000",
      "professional_bio": "Experienced developer...",
      "skills": ["JavaScript", "Python", "React"],
      "avatar_base64": "data:image/png;base64,...",
      "email_verified": true,
      "created_at": "2025-11-15T00:00:00Z"
    }
  }
}
```

#### 6. Update User Profile
- **Endpoint:** `PUT /api/auth/me`
- **Authentication:** Required
- **Request Body:** (all fields optional)
```json
{
  "full_name": "John Doe",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "linkedin_url": "https://linkedin.com/in/johndoe",
  "github_url": "https://github.com/johndoe",
  "portfolio_url": "https://johndoe.com",
  "current_role": "Senior Software Engineer",
  "years_experience": 5,
  "preferred_job_type": "hybrid",
  "salary_expectations": "$120,000 - $160,000",
  "professional_bio": "Senior developer with 5+ years...",
  "skills": ["JavaScript", "TypeScript", "React", "Node.js"]
}
```

#### 7. Upload Avatar
- **Endpoint:** `POST /api/auth/upload-avatar`
- **Authentication:** Required
- **Request Body:**
```json
{
  "avatar_base64": "data:image/png;base64,iVBORw0KGgo..."
}
```
- **Note:** Max file size: 5MB

#### 8. Change Password
- **Endpoint:** `POST /api/auth/change-password`
- **Authentication:** Required
- **Request Body:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword123!"
}
```

#### 9. Forgot Password
- **Endpoint:** `POST /api/auth/forgot-password`
- **Rate Limit:** 3 per hour
- **Public Access:** Yes
- **Request Body:**
```json
{
  "email": "user@example.com"
}
```

#### 10. Reset Password
- **Endpoint:** `POST /api/auth/reset-password`
- **Rate Limit:** 5 per hour
- **Public Access:** Yes
- **Request Body:**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewPassword123!"
}
```

#### 11. Send Email Verification
- **Endpoint:** `POST /api/auth/send-verification-email`
- **Authentication:** Required

#### 12. Verify Email
- **Endpoint:** `POST /api/auth/verify-email`
- **Public Access:** Yes
- **Request Body:**
```json
{
  "token": "verification_token_from_email"
}
```

#### 13. Refresh Access Token
- **Endpoint:** `POST /api/auth/refresh`
- **Authentication:** Required (using refresh token)
- **Headers:**
```
Authorization: Bearer <refresh_token>
```

#### 14. Delete Account
- **Endpoint:** `DELETE /api/auth/delete-account`
- **Authentication:** Required
- **Request Body:**
```json
{
  "password": "CurrentPassword123!"
}
```

---

### Resume Management (`/api/resumes`)

#### 1. Upload Resume
- **Endpoint:** `POST /api/resumes`
- **Authentication:** Required
- **Request Body:**
```json
{
  "filename": "John_Doe_Resume.pdf",
  "file_base64": "base64_encoded_file_data",
  "is_default": true,
  "job_type_tag": "Software Engineer"
}
```
- **Supported formats:** PDF, DOC, DOCX
- **Max file size:** 10MB

#### 2. Get All Resumes
- **Endpoint:** `GET /api/resumes`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "id": "uuid",
        "filename": "John_Doe_Resume.pdf",
        "file_type": "pdf",
        "file_size": 1024000,
        "is_default": true,
        "job_type_tag": "Software Engineer",
        "uploaded_at": "2025-11-15T00:00:00Z"
      }
    ],
    "count": 1
  }
}
```

#### 3. Get Single Resume
- **Endpoint:** `GET /api/resumes/<resume_id>`
- **Authentication:** Required

#### 4. Download Resume
- **Endpoint:** `GET /api/resumes/<resume_id>/download`
- **Authentication:** Required
- **Response:** Includes `file_base64` field with full base64 data

#### 5. Set Default Resume
- **Endpoint:** `PUT /api/resumes/<resume_id>/default`
- **Authentication:** Required

#### 6. Delete Resume
- **Endpoint:** `DELETE /api/resumes/<resume_id>`
- **Authentication:** Required

---

### Job Applications (`/api/applications`)

#### 1. Create Application
- **Endpoint:** `POST /api/applications`
- **Authentication:** Required
- **Request Body:**
```json
{
  "company_name": "Tech Corp",
  "job_title": "Senior Software Engineer",
  "job_type": "Full-time",
  "location": "San Francisco, CA",
  "salary_range": "$120,000 - $160,000",
  "status": "sent",
  "platform": "linkedin",
  "job_url": "https://linkedin.com/jobs/123",
  "resume_used_id": "resume_uuid",
  "cover_letter": "Dear hiring manager...",
  "notes": "Applied through referral"
}
```

#### 2. Get All Applications
- **Endpoint:** `GET /api/applications`
- **Authentication:** Required
- **Query Parameters:**
  - `status` - Filter by status (sent, interviewing, rejected, accepted)
  - `platform` - Filter by platform (linkedin, indeed, glassdoor, etc.)
  - `search` - Search company name or job title
  - `sort` - Sort by (most_recent, oldest)
  - `page` - Page number (default: 1)
  - `limit` - Items per page (default: 20, max: 100)

**Example:** `GET /api/applications?status=interviewing&page=1&limit=20`

#### 3. Get Single Application
- **Endpoint:** `GET /api/applications/<application_id>`
- **Authentication:** Required

#### 4. Update Application
- **Endpoint:** `PUT /api/applications/<application_id>`
- **Authentication:** Required
- **Request Body:** (all fields optional)
```json
{
  "status": "interviewing",
  "notes": "First round interview scheduled for next week",
  "cover_letter": "Updated cover letter...",
  "job_type": "Remote",
  "location": "Remote",
  "salary_range": "$130,000 - $170,000"
}
```

#### 5. Delete Application
- **Endpoint:** `DELETE /api/applications/<application_id>`
- **Authentication:** Required

#### 6. Get Application Statistics
- **Endpoint:** `GET /api/applications/stats`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "total_applications": 42,
    "status_breakdown": {
      "sent": 20,
      "interviewing": 10,
      "rejected": 8,
      "accepted": 4
    },
    "platform_breakdown": {
      "linkedin": 25,
      "indeed": 10,
      "glassdoor": 7
    },
    "recent_applications": [...]
  }
}
```

---

### Platform Credentials (`/api/credentials`)

#### 1. Get All Credentials
- **Endpoint:** `GET /api/credentials`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "credentials": [
      {
        "id": "uuid",
        "platform": "linkedin",
        "username": "user@example.com",
        "is_active": true,
        "last_verified": "2025-11-15T00:00:00Z",
        "created_at": "2025-11-15T00:00:00Z"
      }
    ]
  }
}
```

#### 2. Add/Update Credential
- **Endpoint:** `POST /api/credentials`
- **Authentication:** Required
- **Request Body:**
```json
{
  "platform": "linkedin",
  "username": "user@example.com",
  "password": "platform_password"
}
```
- **Note:** Password is encrypted before storage

#### 3. Delete Credential
- **Endpoint:** `DELETE /api/credentials/<platform>`
- **Authentication:** Required

#### 4. Verify Credential
- **Endpoint:** `POST /api/credentials/<platform>/verify`
- **Authentication:** Required

---

### Search Configuration (`/api/search-config`)

#### 1. Create/Update Configuration
- **Endpoint:** `POST /api/search-config`
- **Authentication:** Required
- **Request Body:**
```json
{
  "platforms": ["linkedin", "indeed", "glassdoor"],
  "primary_job_title": "Software Engineer",
  "primary_location": "San Francisco, CA",
  "primary_min_salary": 120000,
  "primary_experience_level": "senior",
  "primary_keywords": ["React", "Node.js", "TypeScript"],
  "primary_resume_id": "resume_uuid",
  "secondary_job_title": "Full Stack Developer",
  "secondary_location": "Remote",
  "secondary_min_salary": 100000,
  "secondary_experience_level": "mid",
  "secondary_keywords": ["JavaScript", "Python"],
  "secondary_resume_id": "resume_uuid",
  "is_active": true
}
```

#### 2. Get Configuration
- **Endpoint:** `GET /api/search-config`
- **Authentication:** Required

#### 3. Update Configuration
- **Endpoint:** `PUT /api/search-config/<config_id>`
- **Authentication:** Required

#### 4. Delete Configuration
- **Endpoint:** `DELETE /api/search-config/<config_id>`
- **Authentication:** Required

---

### Automation & Queue (`/api/automation`)

#### 1. Get Job Queue
- **Endpoint:** `GET /api/automation/queue`
- **Authentication:** Required
- **Query Parameters:**
  - `status` - Filter by status (pending, processing, applied, failed, skipped)
  - `page` - Page number
  - `limit` - Items per page

#### 2. Skip Job in Queue
- **Endpoint:** `POST /api/automation/queue/<job_id>/skip`
- **Authentication:** Required

#### 3. Update Job Priority
- **Endpoint:** `PUT /api/automation/queue/<job_id>/priority`
- **Authentication:** Required
- **Request Body:**
```json
{
  "priority": 8
}
```
- **Note:** Priority range: 1-10

#### 4. Remove Job from Queue
- **Endpoint:** `DELETE /api/automation/queue/<job_id>`
- **Authentication:** Required

#### 5. Get Automation Status
- **Endpoint:** `GET /api/automation/status`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "queue_stats": {
      "pending": 15,
      "processing": 2,
      "applied": 50,
      "failed": 3
    },
    "rate_limits": {
      "daily_limit": 100,
      "daily_used": 25,
      "remaining": 75
    },
    "next_scheduled_job": {...},
    "is_active": true
  }
}
```

#### 6. Get Automation Logs
- **Endpoint:** `GET /api/automation/logs`
- **Authentication:** Required
- **Query Parameters:**
  - `action_type` - Filter by action type
  - `status` - Filter by status
  - `page` - Page number
  - `limit` - Items per page

#### 7. Get Discovered Jobs
- **Endpoint:** `GET /api/automation/discovered-jobs`
- **Authentication:** Required
- **Query Parameters:**
  - `platform` - Filter by platform
  - `page` - Page number
  - `limit` - Items per page

#### 8. Add Discovered Job to Queue
- **Endpoint:** `POST /api/automation/discovered-jobs/<job_id>/queue`
- **Authentication:** Required

---

### Subscription Management (`/api/subscription`)

#### 1. Get Current Subscription
- **Endpoint:** `GET /api/subscription`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "subscription": {
      "id": "uuid",
      "plan_type": "free",
      "status": "active",
      "applications_limit": 10,
      "applications_used": 5,
      "billing_cycle": null,
      "amount": 0,
      "currency": "USD",
      "next_billing_date": null,
      "created_at": "2025-11-15T00:00:00Z"
    }
  }
}
```

#### 2. Get Available Plans
- **Endpoint:** `GET /api/subscription/plans`
- **Public Access:** Yes
- **Response:**
```json
{
  "success": true,
  "data": {
    "plans": {
      "free": {
        "name": "Free",
        "applications_limit": 10,
        "price": 0,
        "features": ["10 job applications", "Basic search", "Email notifications"]
      },
      "pro": {
        "name": "Professional",
        "applications_limit": 100,
        "price_monthly": 29.99,
        "price_yearly": 299.99,
        "features": ["100 job applications", "Advanced search", "Priority support", "Resume templates"]
      },
      "max": {
        "name": "Maximum",
        "applications_limit": -1,
        "price_monthly": 49.99,
        "price_yearly": 499.99,
        "features": ["Unlimited applications", "AI-powered matching", "Dedicated support", "Premium templates"]
      }
    }
  }
}
```

#### 3. Upgrade Plan
- **Endpoint:** `POST /api/subscription/upgrade`
- **Authentication:** Required
- **Request Body:**
```json
{
  "plan_type": "pro",
  "billing_cycle": "monthly"
}
```

#### 4. Downgrade Plan
- **Endpoint:** `POST /api/subscription/downgrade`
- **Authentication:** Required
- **Request Body:**
```json
{
  "plan_type": "free"
}
```

#### 5. Cancel Subscription
- **Endpoint:** `POST /api/subscription/cancel`
- **Authentication:** Required

#### 6. Add Payment Method
- **Endpoint:** `POST /api/subscription/payment/method`
- **Authentication:** Required
- **Request Body:**
```json
{
  "last4": "4242",
  "expiry": "12/25",
  "brand": "Visa"
}
```

#### 7. Get Payment History
- **Endpoint:** `GET /api/subscription/payment/history`
- **Authentication:** Required
- **Query Parameters:**
  - `page` - Page number
  - `limit` - Items per page

#### 8. Get Invoice
- **Endpoint:** `GET /api/subscription/payment/invoice/<invoice_id>`
- **Authentication:** Required

---

### User Preferences (`/api/preferences`)

#### 1. Get Preferences
- **Endpoint:** `GET /api/preferences`
- **Authentication:** Required
- **Response:**
```json
{
  "success": true,
  "data": {
    "preferences": {
      "id": "uuid",
      "email_notifications_enabled": true,
      "daily_summary_enabled": true,
      "application_updates_enabled": true,
      "job_matches_enabled": true,
      "marketing_emails_enabled": false,
      "auto_apply_enabled": false,
      "max_applications_per_day": 10,
      "min_match_score": 70,
      "timezone": "America/New_York",
      "language": "en",
      "currency": "USD"
    }
  }
}
```

#### 2. Update Preferences
- **Endpoint:** `PUT /api/preferences`
- **Authentication:** Required
- **Request Body:** (all fields optional)
```json
{
  "email_notifications_enabled": true,
  "daily_summary_enabled": true,
  "application_updates_enabled": true,
  "job_matches_enabled": true,
  "marketing_emails_enabled": false,
  "auto_apply_enabled": true,
  "max_applications_per_day": 20,
  "min_match_score": 80,
  "timezone": "America/Los_Angeles",
  "language": "en",
  "currency": "USD"
}
```

#### 3. Reset Preferences
- **Endpoint:** `POST /api/preferences/reset`
- **Authentication:** Required

---

### Platforms (`/api/platforms`)

#### 1. Get Available Platforms
- **Endpoint:** `GET /api/platforms`
- **Public Access:** Yes
- **Response:**
```json
{
  "success": true,
  "data": {
    "popular": [
      {
        "id": "uuid",
        "name": "LinkedIn",
        "code": "linkedin",
        "logo_url": "https://...",
        "is_enabled": true,
        "is_popular": true,
        "requires_credentials": true
      }
    ],
    "others": [...],
    "all": [...]
  }
}
```

---

## Frontend Implementation Requirements

### 1. Registration & Authentication Flow

**Please create the following pages:**

#### Registration Page
- Email/password registration form with validation
- Password requirements display (min 8 chars, uppercase, lowercase, number, special char)
- OAuth buttons for Google and GitHub
- Email verification notice after registration
- Link to login page
- Terms of service and privacy policy checkboxes

#### Login Page
- Email/password login form
- "Remember me" checkbox
- "Forgot password" link
- OAuth buttons for Google and GitHub
- Link to registration page
- Error handling for invalid credentials

#### Forgot Password Page
- Email input form
- Success message after submission
- Link back to login

#### Reset Password Page
- Token validation from URL parameter
- New password input with confirmation
- Password requirements display
- Success redirect to login

#### Email Verification Page
- Token validation from URL parameter
- Success/error message display
- Redirect to dashboard after verification

### 2. User Dashboard & Profile

**Dashboard Overview Page:**
- Application statistics cards (total, interviewing, rejected, accepted)
- Recent applications list (last 5)
- Platform breakdown chart
- Status breakdown chart
- Quick actions (create application, upload resume)
- Subscription status banner
- Automation status (active/paused, queue count)

**Profile Page:**
- Personal information section
  - Full name, email (read-only), phone
  - Location, LinkedIn URL, GitHub URL, Portfolio URL
- Professional information
  - Current role, years of experience
  - Preferred job type (remote, hybrid, onsite)
  - Salary expectations
  - Professional bio (textarea)
  - Skills (tag input)
- Avatar upload (drag & drop or file picker)
  - Image preview
  - Max 5MB validation
- Password change section
- Account deletion (with confirmation modal)

**Profile Settings Tabs:**
- Profile Information
- Account Security
- Notification Preferences
- Application Preferences
- Display Settings

### 3. Resume Management

**Resumes Page:**
- List of all uploaded resumes
- Upload new resume button
- Each resume card shows:
  - Filename
  - Upload date
  - File size
  - Job type tag
  - Default badge (if applicable)
  - Actions: Set as default, Download, Delete
- Drag & drop upload area
- File validation (PDF, DOC, DOCX, max 10MB)
- Default resume indicator
- Empty state for no resumes

### 4. Applications Management

**Applications List Page:**
- Search bar (company name or job title)
- Filters:
  - Status dropdown (All, Sent, Interviewing, Rejected, Accepted)
  - Platform dropdown (All, LinkedIn, Indeed, Glassdoor, etc.)
  - Sort by (Most Recent, Oldest)
- Application cards/table with:
  - Company logo placeholder
  - Job title
  - Company name
  - Status badge
  - Platform badge
  - Applied date
  - Quick actions (View, Edit, Delete)
- Pagination controls
- "Create New Application" button
- Export to CSV option

**Application Details Modal/Page:**
- All application information
- Status timeline/history
- Notes section (editable)
- Attached resume information
- Job URL link
- Cover letter display
- Edit mode toggle
- Delete button with confirmation

**Create/Edit Application Form:**
- Company name (required)
- Job title (required)
- Platform selector (required)
- Job type (Full-time, Part-time, Contract, Internship)
- Location
- Salary range
- Job URL
- Status selector
- Resume selector (from uploaded resumes)
- Cover letter textarea
- Notes textarea
- Save and Cancel buttons

### 5. Job Search Configuration

**Search Config Page:**
- Primary search criteria section:
  - Job title
  - Location
  - Minimum salary (currency input)
  - Experience level (Entry, Junior, Mid, Senior, Lead)
  - Keywords (tag input)
  - Resume selector
- Secondary search criteria section (collapsible):
  - Same fields as primary
- Platform selection (multi-select checkboxes)
  - LinkedIn, Indeed, Glassdoor, etc.
- Active/Inactive toggle
- Save configuration button
- Preview matched jobs button

### 6. Automation & Queue

**Automation Dashboard:**
- Status overview cards:
  - Queue statistics (pending, processing, applied, failed)
  - Rate limit status (daily limit, used, remaining)
  - Next scheduled job
  - Active/Paused status toggle
- Job queue table:
  - Company name
  - Job title
  - Platform
  - Status badge
  - Priority (editable 1-10)
  - Scheduled for (date/time)
  - Match score
  - Actions (Skip, Remove, Change Priority)
- Filters (status, platform)
- Pagination

**Discovered Jobs Page:**
- List of auto-discovered jobs
- Each job card shows:
  - Job title
  - Company name
  - Platform
  - Location
  - Salary (if available)
  - Match score
  - "Add to Queue" button
- Platform filter
- Pagination
- Refresh button

**Automation Logs Page:**
- Activity log table:
  - Timestamp
  - Action type
  - Status
  - Details
  - Platform
- Filters (action type, status, date range)
- Pagination
- Export logs button

### 7. Subscription & Billing

**Subscription Page:**
- Current plan card:
  - Plan name and badge
  - Applications used / limit
  - Price and billing cycle
  - Next billing date
  - Status
- Available plans comparison:
  - Free, Pro, Max plans side-by-side
  - Features list for each
  - Pricing (monthly/yearly toggle)
  - Upgrade/Downgrade buttons
- Payment method section:
  - Card information (masked)
  - Add/Update payment method
- Billing history table:
  - Date
  - Amount
  - Status
  - Invoice download link
- Cancel subscription button (with confirmation)

### 8. Platform Credentials

**Credentials Page:**
- List of saved platform credentials
- Each credential card shows:
  - Platform logo and name
  - Username/email
  - Verification status (Verified badge or Verify button)
  - Last verified date
  - Actions (Edit, Delete, Verify)
- Add new credential button
- Security notice about encryption
- Test connection button

**Add/Edit Credential Modal:**
- Platform selector
- Username/email input
- Password input (with show/hide toggle)
- Save button
- Cancel button
- Security information

### 9. Preferences

**Notification Preferences:**
- Email notifications toggle
- Daily summary emails toggle
- Application updates toggle
- Job matches toggle
- Marketing emails toggle

**Application Preferences:**
- Auto-apply enabled toggle
- Max applications per day slider (1-100)
- Minimum match score slider (0-100)

**Display Preferences:**
- Timezone selector
- Language selector
- Currency selector

### 10. Navigation & Layout

**Main Navigation (Sidebar or Top Nav):**
- Dashboard
- Applications
- Resumes
- Search Config
- Automation
- Credentials
- Subscription
- Preferences
- Profile

**User Menu (Top Right):**
- User avatar and name
- Profile link
- Settings link
- Logout

---

## Testing Checklist

### Authentication Testing
- [ ] Register new user with email/password
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should show error)
- [ ] Register with Google OAuth
- [ ] Register with GitHub OAuth
- [ ] Forgot password flow
- [ ] Reset password with token
- [ ] Email verification flow
- [ ] Refresh token when access token expires
- [ ] Logout and clear tokens

### Profile Testing
- [ ] View profile information
- [ ] Update profile fields
- [ ] Upload avatar (under 5MB)
- [ ] Upload avatar (over 5MB - should fail)
- [ ] Change password
- [ ] Delete account

### Resume Testing
- [ ] Upload PDF resume
- [ ] Upload DOC/DOCX resume
- [ ] Upload oversized file (should fail)
- [ ] Upload unsupported format (should fail)
- [ ] View all resumes
- [ ] Set default resume
- [ ] Download resume
- [ ] Delete resume

### Application Testing
- [ ] Create new application
- [ ] View all applications
- [ ] Filter by status
- [ ] Filter by platform
- [ ] Search by company/job title
- [ ] Update application status
- [ ] Add notes to application
- [ ] Delete application
- [ ] View application statistics

### Search Config Testing
- [ ] Create search configuration
- [ ] Update existing configuration
- [ ] Set primary and secondary criteria
- [ ] Select multiple platforms
- [ ] Activate/deactivate configuration

### Automation Testing
- [ ] View job queue
- [ ] Skip job in queue
- [ ] Change job priority
- [ ] Remove job from queue
- [ ] View automation status
- [ ] View automation logs
- [ ] View discovered jobs
- [ ] Add discovered job to queue

### Subscription Testing
- [ ] View current subscription
- [ ] View available plans
- [ ] Upgrade to Pro plan
- [ ] Upgrade to Max plan
- [ ] Downgrade to Free plan
- [ ] Add payment method
- [ ] View payment history
- [ ] Download invoice
- [ ] Cancel subscription

### Credentials Testing
- [ ] Add platform credential
- [ ] Update existing credential
- [ ] Verify credential
- [ ] Delete credential
- [ ] View all credentials

### Preferences Testing
- [ ] Update notification preferences
- [ ] Update application preferences
- [ ] Update display preferences
- [ ] Reset to defaults

### Error Handling
- [ ] Test with no internet connection
- [ ] Test with expired token
- [ ] Test rate limiting (register 6 times in 15 minutes)
- [ ] Test validation errors
- [ ] Test server errors (500)

### Performance Testing
- [ ] Test with large resume files
- [ ] Test pagination with many applications
- [ ] Test search with many results
- [ ] Test file uploads

---

## Important Notes for Development

### 1. Token Management
- Store `access_token` and `refresh_token` securely (localStorage or secure cookie)
- Include access token in Authorization header for all authenticated requests
- Implement token refresh logic when access token expires (401 response)
- Clear tokens on logout

### 2. Error Handling
- Display user-friendly error messages
- Handle network errors gracefully
- Show loading states during API calls
- Implement retry logic for failed requests

### 3. File Uploads
- Convert files to base64 before sending
- Validate file size and type on frontend before upload
- Show upload progress if possible
- Handle upload errors

### 4. Form Validation
- Validate all forms on frontend before submission
- Show real-time validation feedback
- Match backend validation rules
- Display specific error messages from backend

### 5. Rate Limiting
- Show rate limit warnings to users
- Disable submit buttons when rate limited
- Display countdown until rate limit resets

### 6. Responsive Design
- Ensure all pages work on mobile, tablet, and desktop
- Use responsive navigation
- Optimize tables for mobile (card view)
- Touch-friendly buttons and controls

### 7. Accessibility
- Use semantic HTML
- Include ARIA labels
- Ensure keyboard navigation works
- Sufficient color contrast
- Screen reader friendly

### 8. Security
- Never log sensitive data (passwords, tokens)
- Use HTTPS for all requests
- Sanitize user inputs
- Implement CSRF protection if needed
- Clear sensitive data on logout

### 9. User Experience
- Show loading spinners during API calls
- Provide success/error toast notifications
- Confirm destructive actions (delete, cancel)
- Auto-save when appropriate
- Remember user preferences

### 10. Testing
- Test all user flows end-to-end
- Test error scenarios
- Test with different user roles/plans
- Test file upload edge cases
- Test token expiration handling

---

## API Testing with cURL Examples

### Register User
```bash
curl -X POST https://devapply-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST https://devapply-backend.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }'
```

### Get Profile (Authenticated)
```bash
curl -X GET https://devapply-backend.onrender.com/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Application
```bash
curl -X POST https://devapply-backend.onrender.com/api/applications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Tech Corp",
    "job_title": "Software Engineer",
    "platform": "linkedin",
    "status": "sent"
  }'
```

---

## Support & Questions

If you encounter any issues or have questions about the API:
1. Check the error response for specific error codes and messages
2. Verify authentication tokens are valid and not expired
3. Ensure request format matches the documentation
4. Check rate limits haven't been exceeded

The backend is fully deployed and tested at: `https://devapply-backend.onrender.com`

Health check endpoint: `https://devapply-backend.onrender.com/health`

---

## Quick Start Guide

1. **Test the backend health:**
   ```bash
   curl https://devapply-backend.onrender.com/health
   ```

2. **Register a test user:**
   Use the registration endpoint to create a test account

3. **Get authentication tokens:**
   Login returns both access_token and refresh_token

4. **Start building the frontend:**
   - Create registration/login pages first
   - Implement token storage and management
   - Build the dashboard
   - Add feature pages progressively
   - Test each feature thoroughly

5. **Use the provided testing checklist** to ensure all features work correctly

---

Good luck with the frontend development! The backend is fully functional and ready for integration. 🚀
