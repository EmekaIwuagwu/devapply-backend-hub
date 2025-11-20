# Job Search Config API - Field Mapping Fix

## Problem Solved

The `/api/search-config` endpoint was not storing most fields because:
1. **Missing database columns**: `config_name`, `primary_max_salary`, `primary_job_type`, `primary_remote_preference`
2. **Field name mismatch**: Frontend sends simplified names (`job_title`), backend expected `primary_job_title`

## What Was Fixed

### 1. Added Missing Database Columns
- `config_name` - Name for the configuration
- `primary_job_type` - Job type (full-time, part-time, contract, etc.)
- `primary_max_salary` - Maximum salary
- `primary_remote_preference` - Remote preference (remote, hybrid, onsite)
- Same for secondary config

### 2. Updated Endpoint to Accept Both Field Name Formats
The endpoint now accepts **both simplified and full field names**:

| Frontend Sends | Backend Stores As |
|----------------|-------------------|
| `config_name` | `config_name` |
| `job_title` | `primary_job_title` |
| `location` | `primary_location` |
| `job_type` | `primary_job_type` |
| `salary_min` | `primary_min_salary` |
| `salary_max` | `primary_max_salary` |
| `experience_level` | `primary_experience_level` |
| `remote_preference` | `primary_remote_preference` |
| `keywords` | `primary_keywords` |
| `platforms` | `platforms` |

---

## API Usage

### **POST /api/search-config** - Create/Update Configuration

**You can now send EITHER format:**

#### **Option 1: Simplified Field Names (Recommended)**
```json
{
  "config_name": "My Search Config",
  "job_title": "Blockchain Engineer",
  "platforms": ["LinkedIn", "Indeed"],
  "keywords": ["Solidity", "Web3", "Smart Contracts"],
  "location": "Remote",
  "job_type": "full-time",
  "experience_level": "senior",
  "salary_min": 100000,
  "salary_max": 150000,
  "remote_preference": "remote"
}
```

#### **Option 2: Full Field Names**
```json
{
  "config_name": "My Search Config",
  "platforms": ["LinkedIn", "Indeed"],
  "primary_job_title": "Blockchain Engineer",
  "primary_location": "Remote",
  "primary_job_type": "full-time",
  "primary_min_salary": 100000,
  "primary_max_salary": 150000,
  "primary_experience_level": "senior",
  "primary_remote_preference": "remote",
  "primary_keywords": ["Solidity", "Web3"]
}
```

#### **Option 3: Mixed (also works!)**
```json
{
  "config_name": "My Search Config",
  "job_title": "Blockchain Engineer",
  "primary_keywords": ["Solidity", "Web3"],
  "location": "Remote",
  "salary_min": 100000
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "config": {
      "id": "config-uuid",
      "user_id": "user-uuid",
      "config_name": "My Search Config",
      "platforms": ["LinkedIn", "Indeed"],
      "primary_job_title": "Blockchain Engineer",
      "primary_location": "Remote",
      "primary_job_type": "full-time",
      "primary_min_salary": 100000,
      "primary_max_salary": 150000,
      "primary_experience_level": "senior",
      "primary_remote_preference": "remote",
      "primary_keywords": ["Solidity", "Web3"],
      "primary_resume_id": null,
      "secondary_job_title": null,
      "secondary_location": null,
      "secondary_job_type": null,
      "secondary_min_salary": null,
      "secondary_max_salary": null,
      "secondary_experience_level": null,
      "secondary_remote_preference": null,
      "secondary_keywords": [],
      "secondary_resume_id": null,
      "is_active": true,
      "created_at": "2025-11-15T12:00:00.000000",
      "updated_at": "2025-11-15T12:00:00.000000"
    }
  },
  "message": "Configuration created successfully"
}
```

---

### **GET /api/search-config** - Retrieve Configuration

**Request:**
```bash
GET /api/search-config
Authorization: Bearer <access_token>
```

**Response (After Fix):**
```json
{
  "success": true,
  "data": {
    "config": {
      "config_name": "My Search Config",
      "platforms": ["LinkedIn", "Indeed"],
      "primary_job_title": "Blockchain Engineer",
      "primary_location": "Remote",
      "primary_job_type": "full-time",
      "primary_min_salary": 100000,
      "primary_max_salary": 150000,
      "primary_experience_level": "senior",
      "primary_remote_preference": "remote",
      "primary_keywords": ["Solidity", "Web3"]
      // ... all other fields
    },
    "has_config": true
  }
}
```

**Response (No Config Yet):**
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

---

## Field Definitions

### **Required Fields**
- None (all fields are optional)

### **Field Types**

| Field | Type | Description | Example Values |
|-------|------|-------------|----------------|
| `config_name` | String | Name for this configuration | "My Primary Search" |
| `platforms` | Array | Job platforms to search | ["LinkedIn", "Indeed"] |
| `job_title` | String | Job title/role | "Software Engineer" |
| `location` | String | Job location | "Remote", "New York, NY" |
| `job_type` | String | Employment type | "full-time", "part-time", "contract" |
| `salary_min` | Integer | Minimum salary | 100000 |
| `salary_max` | Integer | Maximum salary | 150000 |
| `experience_level` | String | Experience level | "entry", "mid", "senior" |
| `remote_preference` | String | Remote work preference | "remote", "hybrid", "onsite" |
| `keywords` | Array | Search keywords | ["Python", "Django", "API"] |
| `resume_id` | String (UUID) | Resume to use for this search | "resume-uuid" |

---

## Deployment Steps

### **Step 1: Run Database Migration**

```bash
# Option 1: Using Flask-Migrate
flask db upgrade

# Option 2: Using custom migration script
python migrate.py

# Option 3: Manual SQL (if migrations don't work)
psql $DATABASE_URL < migrations/manual_add_search_config_fields.sql
```

### **Step 2: Restart Backend Server**

```bash
# Local development
pkill -f "flask run"
flask run

# Production (Render)
# Click "Manual Deploy" in Render dashboard
```

### **Step 3: Verify Fix**

```bash
# Get token
TOKEN="your-access-token"

# Test POST (create config)
curl -X POST https://devapply-backend.onrender.com/api/search-config \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "config_name": "Test Config",
    "job_title": "Engineer",
    "location": "Remote",
    "job_type": "full-time",
    "salary_min": 100000,
    "salary_max": 150000,
    "platforms": ["LinkedIn"]
  }'

# Test GET (retrieve config)
curl -H "Authorization: Bearer $TOKEN" \
  https://devapply-backend.onrender.com/api/search-config
```

**Expected Result:** All fields should be stored and returned!

---

## Manual SQL Migration (Backup Option)

If automated migrations don't work, run this SQL directly:

```sql
-- Add missing columns to job_search_configs table
ALTER TABLE job_search_configs
  ADD COLUMN IF NOT EXISTS config_name VARCHAR(255),
  ADD COLUMN IF NOT EXISTS primary_job_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS primary_max_salary INTEGER,
  ADD COLUMN IF NOT EXISTS primary_remote_preference VARCHAR(50),
  ADD COLUMN IF NOT EXISTS secondary_job_type VARCHAR(50),
  ADD COLUMN IF NOT EXISTS secondary_max_salary INTEGER,
  ADD COLUMN IF NOT EXISTS secondary_remote_preference VARCHAR(50);
```

---

## Testing Checklist

- [ ] Database migration ran successfully
- [ ] Backend server restarted
- [ ] POST with simplified field names works
- [ ] All fields are stored in database
- [ ] GET returns all stored fields
- [ ] Frontend can create and retrieve configs
- [ ] No errors in server logs

---

## Frontend Integration Example

```javascript
// Create/Update Config
const saveConfig = async (formData) => {
  try {
    const response = await apiClient.post('/api/search-config', {
      config_name: formData.configName,
      job_title: formData.jobTitle,
      location: formData.location,
      job_type: formData.jobType,
      salary_min: formData.salaryMin,
      salary_max: formData.salaryMax,
      experience_level: formData.experienceLevel,
      remote_preference: formData.remotePreference,
      keywords: formData.keywords,
      platforms: formData.platforms
    });

    const config = response.data.data.config;
    console.log('Config saved:', config);

    // All fields should now be populated!
    console.log('Job Title:', config.primary_job_title);
    console.log('Location:', config.primary_location);
    console.log('Job Type:', config.primary_job_type);
    console.log('Salary Range:', config.primary_min_salary, '-', config.primary_max_salary);

  } catch (error) {
    console.error('Failed to save config:', error);
  }
};

// Fetch Config
const fetchConfig = async () => {
  try {
    const response = await apiClient.get('/api/search-config');
    const { config, has_config } = response.data.data;

    if (has_config) {
      // Map backend fields to form fields
      setFormData({
        configName: config.config_name || '',
        jobTitle: config.primary_job_title || '',
        location: config.primary_location || '',
        jobType: config.primary_job_type || '',
        salaryMin: config.primary_min_salary || 0,
        salaryMax: config.primary_max_salary || 0,
        experienceLevel: config.primary_experience_level || '',
        remotePreference: config.primary_remote_preference || '',
        keywords: config.primary_keywords || [],
        platforms: config.platforms || []
      });
    } else {
      // No config yet - show empty form
      console.log('No config found');
    }
  } catch (error) {
    console.error('Failed to fetch config:', error);
  }
};
```

---

## Files Changed

1. **app/models/job_search_config.py** - Added missing database columns
2. **app/routes/search_config.py** - Updated endpoint to accept simplified field names
3. **migrations/versions/20251115_add_search_config_fields.py** - Database migration

---

## Summary

✅ **Problem**: Frontend sends `job_title`, backend expected `primary_job_title`
✅ **Solution**: Backend now accepts BOTH formats

✅ **Problem**: Missing database columns (max_salary, job_type, etc.)
✅ **Solution**: Added all missing columns via migration

✅ **Result**: All fields now stored and returned correctly!

---

## Need Help?

If you still see `null` values:
1. Verify database migration ran successfully
2. Check server logs for errors
3. Verify you're sending the correct field names
4. Test with cURL to isolate frontend vs backend issues
