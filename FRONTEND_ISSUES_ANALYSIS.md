# Frontend Integration Issues - Analysis and Solutions

This document addresses the 6 issues reported by the frontend team and provides solutions.

---

## Issue #1: Resume Persistence - Resumes Not Showing After Logout/Login

### **Status: ✅ Backend Working Correctly - Frontend Integration Issue**

### Backend Analysis:
The backend is working perfectly:
- ✅ Resumes are stored in database with user_id foreign key
- ✅ GET `/api/resumes` endpoint returns all user resumes
- ✅ Data includes: id, filename, file_type, file_size, is_default, uploaded_at
- ✅ Authentication middleware validates JWT token correctly

### Backend Endpoint:
```http
GET /api/resumes
Authorization: Bearer <access_token>
```

### Response:
```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "id": "resume-uuid",
        "user_id": "user-uuid",
        "filename": "John_Doe_Resume.pdf",
        "file_type": "pdf",
        "file_size": 245678,
        "is_default": true,
        "job_type_tag": "Software Engineering",
        "uploaded_at": "2025-11-15T10:00:00Z",
        "last_used_at": null
      }
    ],
    "count": 1
  }
}
```

### Frontend Requirements:
1. **On page load** (`/resumes`), call `GET /api/resumes` with Authorization header
2. **Access data correctly**: `response.data.data.resumes` (not `response.resumes`)
3. **Store auth token** in localStorage and include in all requests
4. **Handle empty state**: Check if `resumes` array is empty

### Frontend Code Example:
```javascript
// On page load or component mount
useEffect(() => {
  const fetchResumes = async () => {
    try {
      const response = await apiClient.get('/api/resumes');
      const resumes = response.data.data.resumes;  // Access nested data
      setResumes(resumes);  // Store in state
    } catch (error) {
      console.error('Failed to fetch resumes:', error);
    }
  };

  fetchResumes();
}, []);
```

### Testing:
```bash
# Get token from login
TOKEN="your-access-token"

# Test resume fetch
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/resumes
```

---

## Issue #2: Resume Name Not Showing

### **Status: ✅ Backend Working Correctly - Frontend Display Issue**

### Backend Analysis:
The `Resume.to_dict()` method (line 24-39 in `app/models/resume.py`) includes the `filename` field:

```python
def to_dict(self, include_file=False):
    data = {
        'id': self.id,
        'filename': self.filename,  # ✅ This is included!
        'file_type': self.file_type,
        'file_size': self.file_size,
        # ... other fields
    }
    return data
```

### Backend Response:
```json
{
  "success": true,
  "data": {
    "resumes": [
      {
        "filename": "John_Doe_Resume.pdf"  // ✅ This is returned!
      }
    ]
  }
}
```

### Frontend Requirements:
Display `resume.filename` in the UI:

```javascript
{resumes.map(resume => (
  <div key={resume.id}>
    <h3>{resume.filename}</h3>  {/* ✅ Show filename */}
    <p>Type: {resume.file_type}</p>
    <p>Size: {(resume.file_size / 1024).toFixed(2)} KB</p>
    <p>Uploaded: {new Date(resume.uploaded_at).toLocaleDateString()}</p>
  </div>
))}
```

---

## Issue #3: AI Config Saved Application Data (View/Edit/Delete)

### **Status: ✅ FIXED - Enhanced GET endpoint to handle empty state**

### What Was Changed:
Previously, `GET /api/search-config` returned **404 error** if no config existed.
Now it returns a **friendly empty state** with helpful message.

### Backend Endpoints:

#### **GET - Fetch Saved Config**
```http
GET /api/search-config
Authorization: Bearer <access_token>
```

**Response (When Config Exists):**
```json
{
  "success": true,
  "data": {
    "config": {
      "id": "config-uuid",
      "platforms": ["LinkedIn", "Indeed"],
      "primary_job_title": "Software Engineer",
      "primary_location": "San Francisco, CA",
      "primary_min_salary": 100000,
      "primary_experience_level": "mid-level",
      "primary_keywords": ["Python", "Backend", "API"],
      "primary_resume_id": "resume-uuid",
      "secondary_job_title": null,
      // ... other fields
      "is_active": true,
      "created_at": "2025-11-15T10:00:00Z",
      "updated_at": "2025-11-15T10:00:00Z"
    },
    "has_config": true
  }
}
```

**Response (When No Config):**
```json
{
  "success": true,
  "data": {
    "config": null,
    "has_config": false,
    "message": "No configuration found. Create one to get started."
  }
}
```

#### **PUT - Update Config**
```http
PUT /api/search-config/{config_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "primary_job_title": "Senior Software Engineer",
  "primary_min_salary": 150000,
  "platforms": ["LinkedIn"],
  "is_active": true
}
```

#### **DELETE - Delete Config**
```http
DELETE /api/search-config/{config_id}
Authorization: Bearer <access_token>
```

### Frontend Implementation for `/saved-applicationdata` Page:

```javascript
// Fetch saved config on page load
useEffect(() => {
  const fetchConfig = async () => {
    try {
      const response = await apiClient.get('/api/search-config');
      const { config, has_config } = response.data.data;

      if (has_config) {
        setConfig(config);
        setHasConfig(true);
      } else {
        // Show empty state - no config yet
        setHasConfig(false);
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
    }
  };

  fetchConfig();
}, []);

// Edit config
const handleEdit = async (configId, updates) => {
  try {
    const response = await apiClient.put(`/api/search-config/${configId}`, updates);
    setConfig(response.data.data.config);
    toast.success('Configuration updated successfully');
  } catch (error) {
    toast.error('Failed to update configuration');
  }
};

// Delete config
const handleDelete = async (configId) => {
  try {
    await apiClient.delete(`/api/search-config/${configId}`);
    setConfig(null);
    setHasConfig(false);
    toast.success('Configuration deleted successfully');
  } catch (error) {
    toast.error('Failed to delete configuration');
  }
};
```

---

## Issue #4: Profile Data Disappears on Refresh

### **Status: ✅ ENHANCED - Profile endpoint now includes subscription**

### What Was Changed:
Enhanced `GET /api/auth/me` to return user profile **AND** subscription info in one call.

### Backend Endpoint:
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

### Response:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "phone": "+1234567890",
      "location": "New York, NY",
      "linkedin_url": "https://linkedin.com/in/johndoe",
      "github_url": "https://github.com/johndoe",
      "portfolio_url": "https://johndoe.com",
      "current_role": "Software Engineer",
      "years_experience": 5,
      "preferred_job_type": "full-time",
      "salary_expectations": 120000,
      "professional_bio": "Experienced developer...",
      "skills": ["Python", "JavaScript", "React"],
      "avatar_base64": "data:image/png;base64,...",
      "oauth_provider": null,
      "email_verified": false,
      "created_at": "2025-11-15T10:00:00Z",
      "updated_at": "2025-11-15T10:00:00Z"
    },
    "subscription": {
      "id": "sub-uuid",
      "plan_type": "free",
      "status": "active",
      "applications_limit": 10,
      "applications_used": 5,
      "billing_cycle": null,
      "amount": null,
      "currency": "USD",
      "started_at": "2025-11-15T10:00:00Z"
    }
  }
}
```

### Frontend Requirements:
1. **On page load** (`/profile`), call `GET /api/auth/me`
2. **Populate form fields** with the returned user data
3. **Access nested data**: `response.data.data.user` and `response.data.data.subscription`

### Frontend Code Example:
```javascript
// On component mount - fetch user profile
useEffect(() => {
  const fetchProfile = async () => {
    try {
      const response = await apiClient.get('/api/auth/me');
      const { user, subscription } = response.data.data;

      // Set form values
      setFormData({
        full_name: user.full_name || '',
        phone: user.phone || '',
        location: user.location || '',
        linkedin_url: user.linkedin_url || '',
        github_url: user.github_url || '',
        portfolio_url: user.portfolio_url || '',
        current_role: user.current_role || '',
        years_experience: user.years_experience || 0,
        preferred_job_type: user.preferred_job_type || '',
        salary_expectations: user.salary_expectations || 0,
        professional_bio: user.professional_bio || '',
        skills: user.skills || []
      });

      // Store subscription info
      setSubscription(subscription);

    } catch (error) {
      console.error('Failed to fetch profile:', error);
    }
  };

  fetchProfile();
}, []);

// Save profile
const handleSave = async () => {
  try {
    const response = await apiClient.put('/api/auth/me', formData);
    const updatedUser = response.data.data.user;

    // Update local state
    setFormData(updatedUser);
    toast.success('Profile updated successfully');
  } catch (error) {
    toast.error('Failed to update profile');
  }
};
```

---

## Issue #5: Change Password Not Working

### **Status: ✅ Backend Working Correctly - Verify Frontend Request Format**

### Backend Analysis:
The change password endpoint is correctly implemented with:
- ✅ Current password validation
- ✅ New password strength validation
- ✅ Secure password hashing (PBKDF2-SHA256)
- ✅ Database commit

### Backend Endpoint:
```http
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456!"
}
```

### Password Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Success Response:
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

### Error Responses:
```json
// Wrong current password
{
  "success": false,
  "error": {
    "code": "INVALID_PASSWORD",
    "message": "Current password is incorrect"
  }
}

// Weak new password
{
  "success": false,
  "error": {
    "code": "INVALID_PASSWORD",
    "message": "Password must be at least 8 characters and contain uppercase, lowercase, number, and special character"
  }
}
```

### Frontend Requirements:
1. **Field names must match**: `current_password` and `new_password` (not `currentPassword`)
2. **Include Authorization header** with valid access token
3. **Validate new password** on frontend before sending
4. **Handle errors** and show appropriate messages

### Frontend Code Example:
```javascript
const handleChangePassword = async (e) => {
  e.preventDefault();

  // Frontend validation
  if (newPassword.length < 8) {
    toast.error('Password must be at least 8 characters');
    return;
  }

  if (newPassword !== confirmPassword) {
    toast.error('Passwords do not match');
    return;
  }

  try {
    const response = await apiClient.post('/api/auth/change-password', {
      current_password: currentPassword,  // ✅ Exact field name
      new_password: newPassword            // ✅ Exact field name
    });

    toast.success('Password changed successfully');

    // Clear form
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');

  } catch (error) {
    if (error.response?.data?.error) {
      const errorMessage = error.response.data.error.message;
      toast.error(errorMessage);
    } else {
      toast.error('Failed to change password');
    }
  }
};
```

### Testing:
```bash
# Get token from login
TOKEN="your-access-token"

# Test password change
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Test123!@#",
    "new_password": "NewPass123!@#"
  }'
```

---

## Issue #6: Free Plan Default for New Users

### **Status: ✅ Already Implemented Correctly**

### Backend Analysis:
The registration flow already creates a **Free subscription** for all new users.

### Code Location:
`app/routes/auth.py` lines 49-58 (register endpoint):

```python
# Create free subscription for new user
subscription = Subscription(
    user_id=user.id,
    plan_type='free',      # ✅ Default to free
    status='active',        # ✅ Active immediately
    applications_limit=10,  # ✅ Free tier limit
    applications_used=0
)
db.session.add(subscription)
db.session.commit()
```

### This Happens Automatically When:
- User registers with email/password
- User signs up with Google OAuth
- User signs up with GitHub OAuth

### Subscription Plans:

| Plan | Limit | Price | Features |
|------|-------|-------|----------|
| Free | 10 apps/month | $0 | Basic tracking |
| Pro | 100 apps/month | $29/mo | Auto-apply, AI matching |
| Max | 500 apps/month | $99/mo | Everything + priority support |

### Frontend Implementation:
The subscription is now returned in `GET /api/auth/me`:

```javascript
// After login or on page load
const response = await apiClient.get('/api/auth/me');
const { user, subscription } = response.data.data;

// Display subscription info
console.log('Plan:', subscription.plan_type);  // "free"
console.log('Limit:', subscription.applications_limit);  // 10
console.log('Used:', subscription.applications_used);  // 0-10
```

### For `/settings/subscription` Page:
```javascript
// Show current plan
<div className="current-plan">
  <h3>Current Plan: {subscription.plan_type.toUpperCase()}</h3>
  <p>Applications: {subscription.applications_used} / {subscription.applications_limit}</p>
  <p>Status: {subscription.status}</p>
</div>

// Upgrade buttons
{subscription.plan_type === 'free' && (
  <div className="upgrade-options">
    <button onClick={() => handleUpgrade('pro')}>
      Upgrade to Pro - $29/month
    </button>
    <button onClick={() => handleUpgrade('max')}>
      Upgrade to Max - $99/month
    </button>
  </div>
)}
```

### Upgrade Endpoint:
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

## Summary of Changes Made

### Backend Fixes:
1. ✅ **Fixed AI Config GET** - Returns empty state instead of 404
2. ✅ **Enhanced Profile GET** - Now includes subscription data

### Backend Already Working:
1. ✅ **Resume Persistence** - Fully functional, returns all user resumes
2. ✅ **Resume Filename** - Included in response
3. ✅ **Change Password** - Fully functional with validation
4. ✅ **Free Plan** - Automatically assigned to new users

### Frontend Action Items:
1. ❗ **Resume Persistence** - Call `GET /api/resumes` on page load
2. ❗ **Resume Name** - Display `resume.filename` in UI
3. ✅ **AI Config** - Use enhanced GET endpoint (fixed)
4. ❗ **Profile Persistence** - Call `GET /api/auth/me` on page load and populate form
5. ❗ **Change Password** - Verify field names and error handling
6. ✅ **Subscription** - Already working, display from `/api/auth/me`

---

## Complete Testing Checklist

### Test Resume Endpoints:
```bash
TOKEN="your-access-token"

# Upload resume
curl -X POST http://localhost:5000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test.pdf",
    "file_base64": "data:application/pdf;base64,JVBERi...",
    "is_default": true
  }'

# List resumes
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/resumes
```

### Test Profile Endpoints:
```bash
# Get profile with subscription
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/auth/me

# Update profile
curl -X PUT http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Updated",
    "skills": ["Python", "JavaScript"]
  }'
```

### Test AI Config:
```bash
# Get config (returns empty state if none)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/search-config

# Create config
curl -X POST http://localhost:5000/api/search-config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["LinkedIn"],
    "primary_job_title": "Software Engineer",
    "primary_keywords": ["Python", "API"]
  }'
```

### Test Password Change:
```bash
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPass123!",
    "new_password": "NewPass123!"
  }'
```

---

## Need Help?

- Check `API_ENDPOINTS_REFERENCE.md` for complete API documentation
- Check `FRONTEND_TROUBLESHOOTING.md` for integration issues
- All endpoints tested and working correctly
- Most issues are frontend integration problems (not calling endpoints on page load)
