# Complete Frontend Integration Guide - DevApply Backend

**⚠️ IMPORTANT: Restart your backend server to get the latest fixes!**

This guide provides the complete API reference for integrating the DevApply frontend with the backend.

---

## 🔧 **Prerequisites - MUST DO FIRST**

### **1. Restart Backend Server**
The latest fixes require a server restart:
```bash
# If running locally
pkill -f "flask run"  # or pkill -f "python run.py"
flask run
# or
python run.py

# If running on Render/production
# Click "Manual Deploy" > "Deploy latest commit" in Render dashboard
```

### **2. Verify Backend is Running**
```bash
curl http://localhost:5000/health
# Should return: {"success": true, "data": {"status": "healthy", ...}}
```

### **3. Environment Variables**
Ensure `.env` has:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=your-secret-key
```

---

## 📋 **Complete API Endpoints Status**

### ✅ **All Endpoints Are Working!**

| Feature | Endpoint | Method | Status |
|---------|----------|--------|--------|
| **Authentication** ||||
| Register | `/api/auth/register` | POST | ✅ Working |
| Login | `/api/auth/login` | POST | ✅ Working |
| Get Profile | `/api/auth/me` | GET | ✅ Enhanced* |
| Update Profile | `/api/auth/me` | PUT | ✅ Working |
| Change Password | `/api/auth/change-password` | POST | ✅ Working |
| Upload Avatar | `/api/auth/upload-avatar` | POST | ✅ Working |
| **Resumes** ||||
| Upload | `/api/resumes` | POST | ✅ Working |
| List All | `/api/resumes` | GET | ✅ Working |
| Get One | `/api/resumes/{id}` | GET | ✅ Working |
| Download | `/api/resumes/{id}/download` | GET | ✅ Working |
| Set Default | `/api/resumes/{id}/default` | PUT | ✅ Working |
| Delete | `/api/resumes/{id}` | DELETE | ✅ Working |
| **AI Search Config** ||||
| Create | `/api/search-config` | POST | ✅ Working |
| Get | `/api/search-config` | GET | ✅ Fixed* |
| Update | `/api/search-config/{id}` | PUT | ✅ Working |
| Delete | `/api/search-config/{id}` | DELETE | ✅ Working |
| **Applications** ||||
| Create | `/api/applications` | POST | ✅ Working |
| List All | `/api/applications` | GET | ✅ Working |
| Get One | `/api/applications/{id}` | GET | ✅ Working |
| Update | `/api/applications/{id}` | PUT | ✅ Working |
| Delete | `/api/applications/{id}` | DELETE | ✅ Working |
| Get Stats | `/api/applications/stats` | GET | ✅ Working |
| **Subscription** ||||
| Get Current | `/api/subscription` | GET | ✅ Working |
| Get Plans | `/api/subscription/plans` | GET | ✅ Working |

**\*Enhanced = Improved in latest fixes**

---

## 🎯 **Page-by-Page Integration Guide**

### **1. Dashboard (`/dashboard`)**

**Endpoints to Call:**
```javascript
// On page load
useEffect(() => {
  const fetchDashboardData = async () => {
    try {
      // Get application stats
      const statsRes = await apiClient.get('/api/applications/stats');
      const stats = statsRes.data.data;

      // Get subscription info
      const subRes = await apiClient.get('/api/subscription');
      const subscription = subRes.data.data.subscription;

      setStats(stats);
      setSubscription(subscription);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
    }
  };

  fetchDashboardData();
}, []);
```

**Stats Response:**
```json
{
  "success": true,
  "data": {
    "total_applications": 45,
    "status_breakdown": {
      "sent": 20,
      "viewed": 15,
      "interview": 8,
      "rejected": 2
    },
    "platform_breakdown": {
      "LinkedIn": 25,
      "Indeed": 20
    },
    "recent_applications": [
      {
        "id": "uuid",
        "company_name": "Tech Corp",
        "job_title": "Software Engineer",
        "status": "sent",
        "applied_at": "2025-11-15T10:00:00Z"
      }
    ]
  }
}
```

---

### **2. Resumes Page (`/resumes`)**

**On Page Load - Fetch All Resumes:**
```javascript
useEffect(() => {
  const fetchResumes = async () => {
    try {
      const response = await apiClient.get('/api/resumes');
      const resumes = response.data.data.resumes;
      setResumes(resumes);
    } catch (error) {
      console.error('Failed to load resumes:', error);
    }
  };

  fetchResumes();
}, []);
```

**Upload Resume:**
```javascript
const handleUpload = async (file) => {
  try {
    // Convert to base64
    const base64 = await fileToBase64(file);

    // Upload
    const response = await apiClient.post('/api/resumes', {
      filename: file.name,
      file_base64: base64,  // NOT "content"!
      is_default: false
    });

    const newResume = response.data.data.resume;
    setResumes([...resumes, newResume]);
    toast.success('Resume uploaded successfully');
  } catch (error) {
    toast.error(error.response?.data?.error?.message || 'Upload failed');
  }
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

**Display Resume:**
```javascript
{resumes.map(resume => (
  <div key={resume.id} className="resume-card">
    <h3>{resume.filename}</h3>  {/* ✅ This field exists! */}
    <p>Type: {resume.file_type}</p>
    <p>Size: {(resume.file_size / 1024).toFixed(2)} KB</p>
    <p>Uploaded: {new Date(resume.uploaded_at).toLocaleDateString()}</p>
    {resume.is_default && <Badge>Default</Badge>}

    <button onClick={() => handleSetDefault(resume.id)}>
      Set as Default
    </button>
    <button onClick={() => handleDelete(resume.id)}>
      Delete
    </button>
  </div>
))}
```

**Set as Default:**
```javascript
const handleSetDefault = async (resumeId) => {
  try {
    await apiClient.put(`/api/resumes/${resumeId}/default`);

    // Update local state
    setResumes(resumes.map(r => ({
      ...r,
      is_default: r.id === resumeId
    })));

    toast.success('Default resume updated');
  } catch (error) {
    toast.error('Failed to set default');
  }
};
```

**Delete Resume:**
```javascript
const handleDelete = async (resumeId) => {
  if (!confirm('Are you sure you want to delete this resume?')) return;

  try {
    await apiClient.delete(`/api/resumes/${resumeId}`);
    setResumes(resumes.filter(r => r.id !== resumeId));
    toast.success('Resume deleted');
  } catch (error) {
    toast.error('Failed to delete resume');
  }
};
```

---

### **3. AI Config Page (`/ai-config`)**

**Create/Update Configuration:**
```javascript
const handleSubmit = async (formData) => {
  try {
    const payload = {
      platforms: formData.platforms,  // Array: ["LinkedIn", "Indeed"]
      primary_job_title: formData.primaryJobTitle,
      primary_location: formData.primaryLocation,
      primary_min_salary: formData.primaryMinSalary,
      primary_experience_level: formData.primaryExperienceLevel,
      primary_keywords: formData.primaryKeywords,  // Array
      primary_resume_id: formData.primaryResumeId,

      // Secondary (optional)
      secondary_job_title: formData.secondaryJobTitle,
      secondary_location: formData.secondaryLocation,
      secondary_min_salary: formData.secondaryMinSalary,
      secondary_experience_level: formData.secondaryExperienceLevel,
      secondary_keywords: formData.secondaryKeywords,  // Array
      secondary_resume_id: formData.secondaryResumeId,

      is_active: true
    };

    const response = await apiClient.post('/api/search-config', payload);
    const config = response.data.data.config;

    toast.success('Configuration saved successfully');
    navigate('/saved-applicationdata');
  } catch (error) {
    toast.error(error.response?.data?.error?.message || 'Failed to save');
  }
};
```

**⚠️ Important - Array Fields:**
```javascript
// ✅ Correct
{
  "platforms": ["LinkedIn", "Indeed"],
  "primary_keywords": ["Python", "Backend", "API"]
}

// ❌ Wrong
{
  "platforms": "LinkedIn,Indeed",  // String - won't work!
  "primary_keywords": '["Python", "Backend"]'  // JSON string - won't work!
}
```

---

### **4. Saved Application Data (`/saved-applicationdata`)**

**⚠️ IMPORTANT: This endpoint was fixed! Restart backend to get the fix.**

**On Page Load - Fetch Config:**
```javascript
useEffect(() => {
  const fetchConfig = async () => {
    try {
      const response = await apiClient.get('/api/search-config');
      const { config, has_config } = response.data.data;

      if (has_config) {
        setConfig(config);
        setShowEmptyState(false);
      } else {
        // No config yet - show empty state
        setShowEmptyState(true);
      }
    } catch (error) {
      console.error('Failed to load config:', error);
      toast.error('Failed to load configuration');
    }
  };

  fetchConfig();
}, []);
```

**Response (After Restart with Latest Code):**
```json
// When config exists
{
  "success": true,
  "data": {
    "config": {
      "id": "uuid",
      "platforms": ["LinkedIn", "Indeed"],
      "primary_job_title": "Software Engineer",
      // ... all config fields
    },
    "has_config": true
  }
}

// When no config (NOT 404 anymore!)
{
  "success": true,
  "data": {
    "config": null,
    "has_config": false,
    "message": "No configuration found. Create one to get started."
  }
}
```

**Edit Config:**
```javascript
const handleEdit = async (configId, updates) => {
  try {
    const response = await apiClient.put(`/api/search-config/${configId}`, updates);
    const updatedConfig = response.data.data.config;

    setConfig(updatedConfig);
    toast.success('Configuration updated');
  } catch (error) {
    toast.error('Failed to update configuration');
  }
};
```

**Delete Config:**
```javascript
const handleDelete = async (configId) => {
  if (!confirm('Delete this configuration?')) return;

  try {
    await apiClient.delete(`/api/search-config/${configId}`);
    setConfig(null);
    setShowEmptyState(true);
    toast.success('Configuration deleted');
  } catch (error) {
    toast.error('Failed to delete configuration');
  }
};
```

---

### **5. Applications Page (`/applications`)**

**Fetch Applications with Filters:**
```javascript
const [applications, setApplications] = useState([]);
const [filters, setFilters] = useState({
  status: '',
  platform: '',
  search: '',
  page: 1,
  limit: 20
});

useEffect(() => {
  const fetchApplications = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.status) params.append('status', filters.status);
      if (filters.platform) params.append('platform', filters.platform);
      if (filters.search) params.append('search', filters.search);
      params.append('page', filters.page);
      params.append('limit', filters.limit);

      const response = await apiClient.get(`/api/applications?${params}`);
      const { applications, pagination } = response.data.data;

      setApplications(applications);
      setPagination(pagination);
    } catch (error) {
      console.error('Failed to load applications:', error);
    }
  };

  fetchApplications();
}, [filters]);
```

**Create Application Manually:**
```javascript
const handleCreateApplication = async (formData) => {
  try {
    const response = await apiClient.post('/api/applications', {
      company_name: formData.companyName,
      job_title: formData.jobTitle,
      platform: formData.platform,
      job_url: formData.jobUrl,
      location: formData.location,
      salary_range: formData.salaryRange,
      status: 'sent',
      notes: formData.notes
    });

    const newApp = response.data.data.application;
    setApplications([newApp, ...applications]);
    toast.success('Application added');
  } catch (error) {
    toast.error(error.response?.data?.error?.message || 'Failed to create');
  }
};
```

**Update Application Status:**
```javascript
const handleUpdateStatus = async (applicationId, newStatus) => {
  try {
    const response = await apiClient.put(`/api/applications/${applicationId}`, {
      status: newStatus
    });

    const updated = response.data.data.application;

    // Update local state
    setApplications(applications.map(app =>
      app.id === applicationId ? updated : app
    ));

    toast.success('Status updated');
  } catch (error) {
    toast.error('Failed to update status');
  }
};
```

**Update Notes:**
```javascript
const handleUpdateNotes = async (applicationId, notes) => {
  try {
    await apiClient.put(`/api/applications/${applicationId}`, { notes });

    setApplications(applications.map(app =>
      app.id === applicationId ? { ...app, notes } : app
    ));

    toast.success('Notes updated');
  } catch (error) {
    toast.error('Failed to update notes');
  }
};
```

**Delete Application:**
```javascript
const handleDelete = async (applicationId) => {
  if (!confirm('Delete this application?')) return;

  try {
    await apiClient.delete(`/api/applications/${applicationId}`);
    setApplications(applications.filter(app => app.id !== applicationId));
    toast.success('Application deleted');
  } catch (error) {
    toast.error('Failed to delete application');
  }
};
```

---

### **6. Profile Page (`/settings/profile`)**

**⚠️ IMPORTANT: Profile endpoint was enhanced! Restart backend to get the fix.**

**On Page Load - Fetch Profile:**
```javascript
useEffect(() => {
  const fetchProfile = async () => {
    try {
      const response = await apiClient.get('/api/auth/me');
      const { user, subscription } = response.data.data;

      // Populate form
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

      setSubscription(subscription);
      setAvatarUrl(user.avatar_base64);
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  fetchProfile();
}, []);
```

**Save Profile:**
```javascript
const handleSave = async () => {
  try {
    const response = await apiClient.put('/api/auth/me', formData);
    const updatedUser = response.data.data.user;

    // Update form with saved data
    setFormData(updatedUser);
    toast.success('Profile updated successfully');
  } catch (error) {
    toast.error(error.response?.data?.error?.message || 'Failed to save');
  }
};
```

**Upload Avatar:**
```javascript
const handleAvatarUpload = async (file) => {
  try {
    const base64 = await fileToBase64(file);

    const response = await apiClient.post('/api/auth/upload-avatar', {
      avatar_base64: base64
    });

    const updatedUser = response.data.data.user;
    setAvatarUrl(updatedUser.avatar_base64);
    toast.success('Avatar updated');
  } catch (error) {
    toast.error('Avatar upload failed');
  }
};
```

---

### **7. Account Settings (`/settings/account`)**

**⚠️ IMPORTANT: Change password endpoint exists and works!**

**Change Password:**
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
    await apiClient.post('/api/auth/change-password', {
      current_password: currentPassword,  // ⚠️ Exact field name (underscore)
      new_password: newPassword            // ⚠️ Exact field name (underscore)
    });

    toast.success('Password changed successfully');

    // Clear form
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  } catch (error) {
    const errorMessage = error.response?.data?.error?.message;
    if (errorMessage === 'Current password is incorrect') {
      toast.error('Current password is incorrect');
    } else if (errorMessage.includes('Password must')) {
      toast.error(errorMessage);
    } else {
      toast.error('Failed to change password');
    }
  }
};
```

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

---

### **8. Subscription Settings (`/settings/subscription`)**

**Fetch Subscription:**
```javascript
useEffect(() => {
  const fetchSubscription = async () => {
    try {
      // Option 1: Get from profile endpoint
      const response = await apiClient.get('/api/auth/me');
      const { subscription } = response.data.data;

      // Option 2: Get from subscription endpoint
      // const response = await apiClient.get('/api/subscription');
      // const subscription = response.data.data.subscription;

      setSubscription(subscription);
    } catch (error) {
      console.error('Failed to load subscription:', error);
    }
  };

  fetchSubscription();
}, []);
```

**Display Subscription:**
```javascript
<div className="subscription-info">
  <h3>Current Plan: {subscription.plan_type.toUpperCase()}</h3>
  <p>Status: {subscription.status}</p>
  <p>Applications Used: {subscription.applications_used} / {subscription.applications_limit}</p>

  {subscription.plan_type === 'free' && (
    <div className="upgrade-section">
      <h4>Upgrade Your Plan</h4>
      <button onClick={() => handleUpgrade('pro')}>
        Pro Plan - $29/month
      </button>
      <button onClick={() => handleUpgrade('max')}>
        Max Plan - $99/month
      </button>
    </div>
  )}
</div>
```

**Get Available Plans:**
```javascript
const response = await apiClient.get('/api/subscription/plans');
const plans = response.data.data.plans;
```

---

## 🧪 **Testing All Endpoints**

### **Step 1: Register & Login**
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'

# Login (copy access_token from response)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!@#"
  }'
```

### **Step 2: Set Token**
```bash
TOKEN="paste-your-access-token-here"
```

### **Step 3: Test Each Endpoint**

**Profile:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/auth/me
```

**Resumes:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/resumes
```

**Search Config (Should NOT return 404 after restart!):**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/search-config
```

**Applications:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/applications
```

**Change Password:**
```bash
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Test123!@#",
    "new_password": "NewPass123!@#"
  }'
```

---

## ⚠️ **Common Mistakes to Avoid**

### **1. Wrong Data Access**
```javascript
// ❌ Wrong
const user = response.user;
const resumes = response.resumes;

// ✅ Correct
const user = response.data.data.user;
const resumes = response.data.data.resumes;
```

### **2. Wrong Field Names**
```javascript
// ❌ Wrong (camelCase)
{
  "currentPassword": "...",
  "newPassword": "...",
  "fileName": "..."
}

// ✅ Correct (snake_case)
{
  "current_password": "...",
  "new_password": "...",
  "file_base64": "..."
}
```

### **3. Array Fields as Strings**
```javascript
// ❌ Wrong
{
  "platforms": "LinkedIn,Indeed",
  "skills": "Python,JavaScript"
}

// ✅ Correct
{
  "platforms": ["LinkedIn", "Indeed"],
  "skills": ["Python", "JavaScript"]
}
```

### **4. Missing Authorization Header**
```javascript
// ❌ Wrong - no token
fetch('/api/resumes')

// ✅ Correct
fetch('/api/resumes', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

---

## 🚀 **Deployment Checklist**

Before testing, ensure:

- ✅ **Backend server restarted** with latest code
- ✅ **Database migrations run** (if any)
- ✅ **Environment variables set** (CORS_ORIGINS, DATABASE_URL, etc.)
- ✅ **CORS configured** with frontend URL
- ✅ **Test user created** for testing

---

## 📝 **Quick Reference**

All endpoints return:
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional message"
}
```

Errors return:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

**Need more help?** See:
- `API_ENDPOINTS_REFERENCE.md` - Detailed endpoint documentation
- `FRONTEND_ISSUES_ANALYSIS.md` - Issue analysis and solutions
- `FRONTEND_TROUBLESHOOTING.md` - Debugging guide
