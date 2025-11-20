# Frontend Integration Troubleshooting Guide

This guide helps diagnose and fix common issues when integrating the DevApply frontend with the backend API.

## Recent Fixes Applied

### ✅ Enhanced CORS Configuration
The CORS configuration has been updated to support comprehensive frontend integration:
- **Credentials Support**: Enabled for cookie-based auth
- **Allowed Headers**: Content-Type, Authorization, X-Requested-With
- **Exposed Headers**: Content-Type, rate limit headers
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS, PATCH

## Common Integration Issues & Solutions

### 1. CORS Errors ❌

**Symptoms:**
- Browser console shows: `Access to fetch at '...' has been blocked by CORS policy`
- Network tab shows failed OPTIONS (preflight) requests
- Error: `No 'Access-Control-Allow-Origin' header present`

**Solutions:**

#### A. Configure CORS_ORIGINS Environment Variable
Edit your `.env` file:

```bash
# For local development
CORS_ORIGINS=http://localhost:3000

# For Vite/SvelteKit (port 5173)
CORS_ORIGINS=http://localhost:5173

# For multiple origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend.com

# For all origins (development only - NOT recommended for production)
CORS_ORIGINS=*
```

#### B. Verify Frontend Request Configuration
Make sure your frontend is configured correctly:

**Axios Configuration:**
```javascript
// src/api/axios.js
const apiClient = axios.create({
  baseURL: 'http://localhost:5000',  // or your backend URL
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true  // Important for cookies/credentials
});
```

**Fetch Configuration:**
```javascript
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // Important for cookies/credentials
  body: JSON.stringify({ email, password })
});
```

### 2. Response Data Access Issues 🔍

**Symptoms:**
- Getting `undefined` when accessing response data
- Error: `Cannot read property 'user' of undefined`
- Data doesn't show up in frontend

**The Backend Response Structure:**
```json
{
  "success": true,
  "data": {
    "user": {...},
    "access_token": "...",
    "refresh_token": "..."
  },
  "message": "User registered successfully",
  "meta": {
    "timestamp": "2025-11-15T10:31:59.643186"
  }
}
```

**❌ Wrong Way:**
```javascript
const response = await axios.post('/api/auth/login', credentials);
const user = response.user;  // ❌ Wrong!
const token = response.access_token;  // ❌ Wrong!
```

**✅ Correct Way:**
```javascript
const response = await axios.post('/api/auth/login', credentials);
const user = response.data.data.user;  // ✅ Correct!
const token = response.data.data.access_token;  // ✅ Correct!
const message = response.data.message;  // ✅ Correct!
```

**Better: Use Destructuring**
```javascript
const { data } = await axios.post('/api/auth/login', credentials);
const { user, access_token, refresh_token } = data.data;
const message = data.message;
```

### 3. Authentication Token Issues 🔐

**Symptoms:**
- 401 Unauthorized errors
- "Token has expired" errors
- Login works but protected routes fail

**Solutions:**

#### A. Proper Token Storage
```javascript
// After successful login/register
const { data } = await axios.post('/api/auth/login', credentials);
const { access_token, refresh_token, user } = data.data;

// Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);
localStorage.setItem('user', JSON.stringify(user));
```

#### B. Add Token to All Requests
```javascript
// Axios interceptor (recommended)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### C. Implement Token Refresh
```javascript
// Axios response interceptor for auto-refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(
          '/api/auth/refresh',
          null,
          { headers: { Authorization: `Bearer ${refreshToken}` }}
        );

        const { access_token } = response.data.data;
        localStorage.setItem('access_token', access_token);

        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed - logout user
        localStorage.clear();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);
```

### 4. Array Field Issues (Skills, Platforms, Keywords) 📋

**Symptoms:**
- Skills/platforms not saving correctly
- Getting SQL errors when updating profile
- Array fields showing as strings

**Background:**
Recent update changed these fields from JSON to PostgreSQL ARRAY type:
- User `skills`
- JobSearchConfig `platforms`, `primary_keywords`, `secondary_keywords`

**✅ Correct Format:**
```javascript
// Update user profile with skills
await axios.put('/api/auth/me', {
  skills: ['Python', 'JavaScript', 'React']  // ✅ Array
});

// Create job search config
await axios.post('/api/search-config', {
  platforms: ['LinkedIn', 'Indeed'],  // ✅ Array
  primary_keywords: ['Backend', 'API', 'Python'],  // ✅ Array
  secondary_keywords: ['Remote', 'Full-time']  // ✅ Array
});
```

**❌ Wrong Format:**
```javascript
// Don't send as string or stringified JSON
await axios.put('/api/auth/me', {
  skills: "Python,JavaScript,React"  // ❌ Wrong!
  skills: JSON.stringify(['Python', 'JavaScript'])  // ❌ Wrong!
});
```

### 5. Date/Time Format Issues 📅

**Symptoms:**
- Dates not displaying correctly
- "Invalid Date" errors

**Backend sends ISO 8601 format:**
```json
{
  "created_at": "2025-11-15T10:31:59.502015",
  "updated_at": "2025-11-15T10:31:59.502018"
}
```

**Frontend Parsing:**
```javascript
// Parse and format dates
const createdAt = new Date(user.created_at);
const formatted = createdAt.toLocaleDateString('en-US', {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
});
// Output: "Nov 15, 2025"

// Use libraries for better formatting
import { format } from 'date-fns';
const formatted = format(new Date(user.created_at), 'PPP');
// Output: "November 15th, 2025"
```

### 6. File Upload Issues 📤

**Symptoms:**
- Resume/avatar uploads fail
- "File too large" errors
- Invalid base64 errors

**Correct File Upload:**
```javascript
// Convert file to base64
const fileToBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = (error) => reject(error);
  });
};

// Upload resume
const handleResumeUpload = async (file) => {
  // Validate file size (5MB for resumes)
  if (file.size > 5 * 1024 * 1024) {
    alert('File too large. Maximum size is 5MB');
    return;
  }

  // Validate file type
  const allowedTypes = ['application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  if (!allowedTypes.includes(file.type)) {
    alert('Invalid file type. Only PDF, DOC, DOCX allowed');
    return;
  }

  const base64 = await fileToBase64(file);

  const response = await apiClient.post('/api/resumes', {
    file_base64: base64,  // Already includes "data:application/pdf;base64,..."
    filename: file.name,
    job_type: 'Software Engineering',
    is_default: true
  });
};

// Upload avatar (2MB limit)
const handleAvatarUpload = async (file) => {
  if (file.size > 2 * 1024 * 1024) {
    alert('Avatar too large. Maximum size is 2MB');
    return;
  }

  const base64 = await fileToBase64(file);

  await apiClient.post('/api/auth/upload-avatar', {
    avatar_base64: base64
  });
};
```

### 7. Rate Limiting Issues ⏱️

**Symptoms:**
- 429 "Rate limit exceeded" errors
- "Too many requests" messages

**Backend Rate Limits:**
- Login/Register: 5 attempts per 15 minutes
- Forgot Password: 3 attempts per hour
- Other endpoints: 100 requests per hour

**Frontend Handling:**
```javascript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'] || 60;
      alert(`Too many requests. Please wait ${retryAfter} seconds and try again.`);
    }
    return Promise.reject(error);
  }
);
```

### 8. Error Response Handling ⚠️

**Backend Error Format:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password",
    "details": {}
  }
}
```

**Frontend Error Handling:**
```javascript
try {
  const response = await apiClient.post('/api/auth/login', credentials);
  // Handle success
} catch (error) {
  if (error.response) {
    // Backend returned an error response
    const { code, message } = error.response.data.error;

    switch (code) {
      case 'INVALID_CREDENTIALS':
        setError('Invalid email or password');
        break;
      case 'RATE_LIMIT_EXCEEDED':
        setError('Too many login attempts. Please try again later.');
        break;
      case 'USER_NOT_FOUND':
        setError('Account not found');
        break;
      default:
        setError(message || 'An error occurred');
    }
  } else if (error.request) {
    // Request made but no response (network error)
    setError('Network error. Please check your connection.');
  } else {
    // Something else happened
    setError('An unexpected error occurred');
  }
}
```

## Testing Checklist ✅

### Backend Testing
```bash
# 1. Check if backend is running
curl http://localhost:5000/health

# 2. Test CORS preflight
curl -X OPTIONS http://localhost:5000/api/auth/login \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type, Authorization" \
  -v

# 3. Test registration
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User"
  }' \
  -v

# 4. Test login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost:3000" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#"
  }' \
  -v
```

### Frontend Testing

**1. Test API Connection:**
```javascript
// Simple connection test
fetch('http://localhost:5000/health')
  .then(res => res.json())
  .then(data => console.log('Backend connected:', data))
  .catch(err => console.error('Backend connection failed:', err));
```

**2. Test CORS:**
```javascript
// This should not show CORS errors in browser console
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'test@test.com', password: 'Test123!@#' })
})
  .then(res => res.json())
  .then(data => console.log('CORS working:', data))
  .catch(err => console.error('CORS error:', err));
```

**3. Test Authentication Flow:**
```javascript
// Complete auth flow test
async function testAuthFlow() {
  try {
    // 1. Register
    const registerRes = await apiClient.post('/api/auth/register', {
      email: 'newuser@test.com',
      password: 'Test123!@#',
      full_name: 'New User'
    });
    console.log('✅ Registration:', registerRes.data);

    // 2. Store tokens
    const { access_token, refresh_token } = registerRes.data.data;
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);

    // 3. Get profile (requires auth)
    const profileRes = await apiClient.get('/api/auth/me');
    console.log('✅ Profile fetch:', profileRes.data);

    // 4. Update profile
    const updateRes = await apiClient.put('/api/auth/me', {
      skills: ['JavaScript', 'React', 'Node.js'],
      location: 'New York, NY'
    });
    console.log('✅ Profile update:', updateRes.data);

    console.log('🎉 All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}
```

## Environment-Specific Configuration

### Development
```javascript
// config/development.js
export const API_BASE_URL = 'http://localhost:5000';
export const ENABLE_LOGGING = true;
```

### Production
```javascript
// config/production.js
export const API_BASE_URL = 'https://your-backend.onrender.com';
export const ENABLE_LOGGING = false;
```

### Using Environment Variables
```javascript
// .env.development
VITE_API_BASE_URL=http://localhost:5000

// .env.production
VITE_API_BASE_URL=https://your-backend.onrender.com

// src/api/axios.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
```

## Browser DevTools Debugging

### 1. Check Network Tab
- Look for failed requests (red)
- Check response status codes (401, 403, 404, 429, 500)
- Verify request headers include `Authorization: Bearer ...`
- Check response headers for CORS headers

### 2. Check Console
- Look for CORS errors
- Check for JavaScript errors
- Verify logged data structure matches expected format

### 3. Check Application Tab
- Verify tokens are stored in localStorage
- Check token format (should be JWT: `eyJ...`)
- Verify user data is properly stored

## Need More Help?

If you're still experiencing issues:

1. **Check backend logs** for detailed error messages
2. **Verify environment variables** are set correctly
3. **Test with cURL** to isolate frontend vs backend issues
4. **Check browser console** for detailed error messages
5. **Verify API endpoint URLs** match between frontend and backend

## Quick Reference: Common Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request payload format |
| 401 | Unauthorized | Add/refresh auth token |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Verify endpoint URL |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check backend logs |

## Summary of Fixes Applied

1. ✅ Enhanced CORS configuration with:
   - Credentials support
   - Explicit header allowances
   - All HTTP methods
   - Exposed rate-limit headers

2. ✅ Added CORS_ORIGINS documentation to `.env.example`

3. ✅ Created this comprehensive troubleshooting guide

These fixes should resolve most frontend integration issues. Make sure to restart your backend server after updating the CORS configuration!
