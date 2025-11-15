# DevApply Frontend - Loveable.dev Build Prompt

## Project Overview
Build a complete job application automation platform frontend that integrates with the existing backend at `https://devapply-backend.onrender.com`

---

## Backend Integration Details

**Base URL:** `https://devapply-backend.onrender.com/api`

**Authentication:** JWT Bearer tokens in Authorization header
```
Authorization: Bearer <access_token>
```

**Response Format:**
```json
{
  "success": true/false,
  "data": {...},
  "message": "...",
  "error": {...}
}
```

---

## Core Features to Build

### 1. Authentication Pages

#### Registration Page (`/register`)
- Email, password, full name, phone (optional) fields
- Password validation: min 8 chars, uppercase, lowercase, number, special char
- Google OAuth button
- GitHub OAuth button
- Link to login page
- API: `POST /api/auth/register`

#### Login Page (`/login`)
- Email and password fields
- "Remember me" checkbox
- "Forgot password" link
- Google and GitHub OAuth buttons
- Link to registration
- API: `POST /api/auth/login`

#### Forgot Password (`/forgot-password`)
- Email input
- API: `POST /api/auth/forgot-password`

#### Reset Password (`/reset-password?token=...`)
- New password with confirmation
- Token from URL parameter
- API: `POST /api/auth/reset-password`

#### Email Verification (`/verify-email?token=...`)
- Auto-verify on page load
- API: `POST /api/auth/verify-email`

**Store tokens in localStorage:**
- `access_token` - for API requests
- `refresh_token` - for token refresh

---

### 2. Dashboard (`/dashboard`)

**Display:**
- Total applications count
- Status breakdown (sent, interviewing, rejected, accepted) - pie/donut chart
- Platform breakdown - bar chart
- Recent 5 applications list
- Subscription status banner (plan, applications used/limit)
- Quick action buttons: "New Application", "Upload Resume"
- Automation status card (active/paused, queue count)

**APIs:**
- `GET /api/applications/stats`
- `GET /api/subscription`
- `GET /api/automation/status`

---

### 3. User Profile (`/profile`)

**Tabs:**
1. **Personal Info**
   - Avatar upload (base64, max 5MB)
   - Full name, email (readonly), phone
   - Location, LinkedIn URL, GitHub URL, Portfolio URL
   - API: `PUT /api/auth/me`, `POST /api/auth/upload-avatar`

2. **Professional Info**
   - Current role, years of experience
   - Preferred job type (remote/hybrid/onsite)
   - Salary expectations
   - Professional bio (textarea)
   - Skills (tag input - array of strings)
   - API: `PUT /api/auth/me`

3. **Account Security**
   - Change password form (current + new password)
   - Email verification status
   - Delete account button (with confirmation)
   - API: `POST /api/auth/change-password`, `DELETE /api/auth/delete-account`

---

### 4. Resumes (`/resumes`)

**Features:**
- Upload resume (PDF, DOC, DOCX, max 10MB) via drag-drop or file picker
- Convert file to base64 before upload
- List all resumes with: filename, size, upload date, job type tag, default badge
- Actions per resume: Set as Default, Download, Delete
- Empty state when no resumes

**APIs:**
- `POST /api/resumes` - upload
- `GET /api/resumes` - list all
- `GET /api/resumes/<id>/download` - download
- `PUT /api/resumes/<id>/default` - set default
- `DELETE /api/resumes/<id>` - delete

---

### 5. Applications (`/applications`)

**List View:**
- Search bar (company name or job title)
- Filters: Status (all/sent/interviewing/rejected/accepted), Platform (all/linkedin/indeed/glassdoor)
- Sort: Most Recent, Oldest
- Pagination (20 per page)
- Application cards showing: company, job title, status badge, platform badge, applied date
- "Create Application" button
- API: `GET /api/applications?status=&platform=&search=&sort=&page=&limit=`

**Create/Edit Application Modal:**
- Form fields:
  - Company name* (required)
  - Job title* (required)
  - Platform* (required) - select from platforms API
  - Job type (Full-time, Part-time, Contract, Internship)
  - Location
  - Salary range
  - Job URL
  - Status (sent/interviewing/rejected/accepted)
  - Resume (select from user's resumes)
  - Cover letter (textarea)
  - Notes (textarea)
- APIs: `POST /api/applications`, `PUT /api/applications/<id>`

**Application Details Modal:**
- View all application info
- Edit button opens edit modal
- Delete button with confirmation
- API: `GET /api/applications/<id>`, `DELETE /api/applications/<id>`

---

### 6. Search Configuration (`/search-config`)

**Form with Two Sections:**

**Primary Search Criteria:**
- Job title
- Location
- Minimum salary (number input)
- Experience level (select: Entry, Junior, Mid, Senior, Lead)
- Keywords (tag input - array)
- Resume (select from user's resumes)

**Secondary Search Criteria (Collapsible):**
- Same fields as primary

**Platform Selection:**
- Multi-select checkboxes for platforms (LinkedIn, Indeed, Glassdoor, etc.)
- Get platforms from `GET /api/platforms`

**Active Toggle:**
- Switch to activate/deactivate configuration

**APIs:**
- `GET /api/search-config` - load config
- `POST /api/search-config` - create/update
- `GET /api/platforms` - get available platforms

---

### 7. Automation (`/automation`)

**Queue Tab:**
- Table/cards showing:
  - Company name, Job title, Platform, Status badge
  - Priority (editable dropdown 1-10)
  - Scheduled date/time
  - Match score
  - Actions: Skip, Remove, Change Priority
- Filters: Status (pending/processing/applied/failed/skipped)
- Pagination
- APIs:
  - `GET /api/automation/queue?status=&page=&limit=`
  - `POST /api/automation/queue/<id>/skip`
  - `PUT /api/automation/queue/<id>/priority`
  - `DELETE /api/automation/queue/<id>`

**Discovered Jobs Tab:**
- List of auto-found jobs
- Each job card: title, company, platform, location, salary, match score
- "Add to Queue" button per job
- Platform filter
- APIs:
  - `GET /api/automation/discovered-jobs?platform=&page=&limit=`
  - `POST /api/automation/discovered-jobs/<id>/queue`

**Logs Tab:**
- Activity log table: timestamp, action type, status, details, platform
- Filters: action type, status
- Pagination
- API: `GET /api/automation/logs?action_type=&status=&page=&limit=`

**Status Header (all tabs):**
- Queue stats: pending, processing, applied, failed counts
- Rate limit: daily limit, used, remaining
- Active/Paused toggle
- Next scheduled job info
- API: `GET /api/automation/status`

---

### 8. Platform Credentials (`/credentials`)

**List View:**
- Cards for each saved credential showing:
  - Platform logo and name
  - Username/email
  - Verification status badge
  - Last verified date
  - Actions: Edit, Delete, Verify
- "Add Credential" button
- API: `GET /api/credentials`

**Add/Edit Credential Modal:**
- Platform selector (from platforms API)
- Username/email input
- Password input (with show/hide toggle)
- Security notice: "Passwords are encrypted"
- APIs:
  - `POST /api/credentials` - add/update
  - `DELETE /api/credentials/<platform>`
  - `POST /api/credentials/<platform>/verify`

---

### 9. Subscription (`/subscription`)

**Current Plan Card:**
- Plan name badge (Free/Pro/Max)
- Applications used / limit progress bar
- Price and billing cycle
- Next billing date
- Upgrade/Downgrade button

**Plans Comparison:**
- 3 columns: Free, Pro, Max
- Toggle: Monthly / Yearly pricing
- Features list for each plan
- Upgrade/Downgrade buttons
- **Plans:**
  - **Free:** $0, 10 applications
  - **Pro:** $29.99/month or $299.99/year, 100 applications
  - **Max:** $49.99/month or $499.99/year, Unlimited applications

**Payment Method Section:**
- Card info display (if added)
- "Add/Update Payment Method" button

**Billing History Table:**
- Date, Amount, Status, Invoice download link
- Pagination

**APIs:**
- `GET /api/subscription` - current subscription
- `GET /api/subscription/plans` - available plans
- `POST /api/subscription/upgrade`
- `POST /api/subscription/downgrade`
- `POST /api/subscription/cancel`
- `POST /api/subscription/payment/method`
- `GET /api/subscription/payment/history`
- `GET /api/subscription/payment/invoice/<id>`

---

### 10. Preferences (`/preferences`)

**Notification Preferences:**
- Email notifications (toggle)
- Daily summary emails (toggle)
- Application updates (toggle)
- Job matches (toggle)
- Marketing emails (toggle)

**Application Preferences:**
- Auto-apply enabled (toggle)
- Max applications per day (slider: 1-100)
- Minimum match score (slider: 0-100)

**Display Preferences:**
- Timezone (select)
- Language (select)
- Currency (select)

**APIs:**
- `GET /api/preferences`
- `PUT /api/preferences`
- `POST /api/preferences/reset`

---

## Navigation Structure

**Main Sidebar/Header Navigation:**
1. Dashboard
2. Applications
3. Resumes
4. Search Config
5. Automation
6. Credentials
7. Subscription
8. Preferences

**User Menu (Top Right):**
- User avatar + name
- Profile
- Settings
- Logout

---

## Important Implementation Notes

### Token Management
```javascript
// Store after login/register
localStorage.setItem('access_token', data.access_token)
localStorage.setItem('refresh_token', data.refresh_token)

// Include in all authenticated requests
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
  'Content-Type': 'application/json'
}

// Refresh token on 401 error
if (response.status === 401) {
  // Call POST /api/auth/refresh with refresh_token
  // Update access_token
  // Retry original request
}

// Clear on logout
localStorage.removeItem('access_token')
localStorage.removeItem('refresh_token')
```

### File Upload (Resume, Avatar)
```javascript
// Convert file to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = error => reject(error)
  })
}

// Validate before upload
if (file.size > 10 * 1024 * 1024) {
  alert('File too large (max 10MB)')
  return
}

// Send to API
const base64 = await fileToBase64(file)
await fetch('/api/resumes', {
  method: 'POST',
  headers: {...},
  body: JSON.stringify({
    filename: file.name,
    file_base64: base64
  })
})
```

### Error Handling
```javascript
try {
  const response = await fetch(url, options)
  const data = await response.json()

  if (!data.success) {
    // Show error toast
    toast.error(data.error.message)
    return
  }

  // Handle success
  toast.success(data.message)
  return data.data
} catch (error) {
  toast.error('Network error. Please try again.')
}
```

### Form Validation
- Email: valid email format
- Password: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
- Phone: optional, valid format
- URLs: valid URL format
- File size: max 10MB for resumes, 5MB for avatars
- File types: PDF, DOC, DOCX for resumes; JPG, PNG for avatars

---

## Design Requirements

### Style
- Modern, clean, professional design
- Color scheme: Use blues/purples for primary, greens for success, reds for errors
- Responsive: Mobile, tablet, desktop
- Dark mode support (optional but nice)

### UI Components Needed
- Toast notifications (success, error, info)
- Loading spinners/skeletons
- Modal dialogs
- Confirmation dialogs for destructive actions
- File upload drag-drop areas
- Progress bars
- Charts (pie/donut for status, bar for platforms)
- Tag inputs (for skills, keywords)
- Date pickers (for scheduling)
- Pagination controls
- Search bars with filters
- Tabs
- Toggles/switches
- Sliders (for preferences)
- Empty states (no resumes, no applications)
- Error states (API errors, no connection)

### Accessibility
- Keyboard navigation
- ARIA labels
- Sufficient color contrast
- Focus states
- Screen reader friendly

---

## Testing Requirements

**Please ensure:**

1. **Authentication Flow:**
   - Register works with valid data
   - Login works with correct credentials
   - Login fails with wrong credentials
   - Tokens are stored and used correctly
   - Logout clears tokens
   - Protected routes redirect to login when not authenticated

2. **File Uploads:**
   - Resume upload works with PDF, DOC, DOCX
   - Rejects files over 10MB
   - Rejects unsupported formats
   - Avatar upload works with images
   - Shows upload progress/loading state

3. **CRUD Operations:**
   - Create application works
   - View applications list works
   - Edit application works
   - Delete application works (with confirmation)
   - Same for resumes

4. **Filters & Search:**
   - Status filter works
   - Platform filter works
   - Search by company/title works
   - Pagination works
   - Sort works

5. **Forms:**
   - All validation works
   - Error messages display correctly
   - Success messages display
   - Required fields enforced
   - Cancel buttons work

6. **Error Handling:**
   - Network errors show user-friendly message
   - API errors show specific error from backend
   - Loading states show during requests
   - Retry logic for failed requests

7. **Responsive:**
   - Test on mobile (320px+)
   - Test on tablet (768px+)
   - Test on desktop (1024px+)
   - Navigation adapts (hamburger on mobile)
   - Tables/cards adapt for mobile

---

## Quick Start for Testing

1. **Backend Health Check:**
   ```
   https://devapply-backend.onrender.com/health
   ```
   Should return: `{"success": true, "data": {"status": "healthy", "service": "DevApply Backend"}}`

2. **Test User Registration:**
   ```
   POST https://devapply-backend.onrender.com/api/auth/register
   Body: {
     "email": "test@test.com",
     "password": "Test123!@#",
     "full_name": "Test User"
   }
   ```

3. **Test Login:**
   ```
   POST https://devapply-backend.onrender.com/api/auth/login
   Body: {
     "email": "test@test.com",
     "password": "Test123!@#"
   }
   ```

4. **Use returned tokens for authenticated requests**

---

## Priority Order for Development

1. ✅ Authentication (Register, Login, Profile) - **CRITICAL**
2. ✅ Dashboard - **HIGH**
3. ✅ Applications Management - **HIGH**
4. ✅ Resumes Management - **HIGH**
5. Search Configuration - **MEDIUM**
6. Automation & Queue - **MEDIUM**
7. Credentials Management - **MEDIUM**
8. Subscription & Billing - **LOW**
9. Preferences - **LOW**

---

## Additional Features (Nice to Have)

- Export applications to CSV
- Bulk actions (delete multiple applications)
- Application status timeline/history visualization
- Job match score visualization
- Calendar view for scheduled applications
- Notifications/alerts system
- Keyboard shortcuts
- Command palette (Cmd+K)
- Onboarding tour for new users
- Help tooltips
- Settings import/export

---

## Final Notes

- All endpoints are LIVE and tested at `https://devapply-backend.onrender.com`
- Use the standard response format for all API calls
- Handle rate limiting (registration: 5 per 15 min, forgot password: 3 per hour)
- Store JWT tokens securely
- Clear sensitive data on logout
- Test thoroughly before deploying
- Ensure all user flows work end-to-end

**The backend is fully functional and ready for integration. Build an amazing frontend! 🚀**

For full API documentation with all request/response examples, see `FRONTEND_INTEGRATION_PROMPT.md` in the repository.
