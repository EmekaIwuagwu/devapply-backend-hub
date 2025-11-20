# Backend Deployment & Testing Checklist

This checklist ensures the latest backend fixes are deployed and working correctly.

---

## 🔧 **Step 1: Deploy Latest Code**

### **Local Development**

```bash
# 1. Pull latest code
git pull origin claude/debug-error-011VmaLLjC1EKFd6wGtwB6pq

# 2. Verify you have the latest changes
git log --oneline -5
# Should see: "Fix frontend integration issues and enhance profile/config endpoints"

# 3. Stop existing server
pkill -f "flask run"
# or
pkill -f "python run.py"

# 4. Restart server
flask run
# or
python run.py
```

### **Production (Render.com)**

```bash
# Option 1: Manual Deploy in Render Dashboard
1. Go to Render dashboard
2. Select your backend service
3. Click "Manual Deploy" > "Deploy latest commit"
4. Wait for deployment to complete (check logs)

# Option 2: Push to trigger auto-deploy
git push origin claude/debug-error-011VmaLLjC1EKFd6wGtwB6pq
# (if auto-deploy is configured)
```

---

## ✅ **Step 2: Verify Backend is Running**

### **Test Health Endpoint**

```bash
# Local
curl http://localhost:5000/health

# Production
curl https://your-backend.onrender.com/health
```

**Expected Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "DevApply Backend"
  }
}
```

---

## 🧪 **Step 3: Test Fixed Endpoints**

### **Test 1: Search Config (Fixed - No More 404)**

```bash
# Get token first
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!@#"
  }'

# Copy access_token, then test
TOKEN="your-access-token"

# This should NOT return 404 anymore
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/search-config
```

**Expected Response (BEFORE fix - 404):**
```json
{
  "success": false,
  "error": {
    "code": "CONFIG_NOT_FOUND",
    "message": "Configuration not found"
  }
}
```

**Expected Response (AFTER fix - 200):**
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

✅ **If you see the AFTER response, the fix is working!**

### **Test 2: Profile with Subscription (Enhanced)**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/auth/me
```

**Expected Response (AFTER fix):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "test@test.com",
      "full_name": "Test User",
      // ... all user fields
    },
    "subscription": {
      "id": "uuid",
      "plan_type": "free",
      "status": "active",
      "applications_limit": 10,
      "applications_used": 0
    }
  }
}
```

✅ **If you see both `user` and `subscription`, the enhancement is working!**

### **Test 3: Change Password (Already Working)**

```bash
curl -X POST http://localhost:5000/api/auth/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "Test123!@#",
    "new_password": "NewPass123!@#"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Password changed successfully"
}
```

✅ **If password changes successfully, endpoint is working!**

### **Test 4: Applications CRUD (Already Working)**

```bash
# Create application
curl -X POST http://localhost:5000/api/applications \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Test Corp",
    "job_title": "Software Engineer",
    "platform": "LinkedIn",
    "status": "sent"
  }'

# Should return created application with ID

# List applications
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/applications

# Update application (use ID from create response)
APP_ID="paste-application-id"
curl -X PUT http://localhost:5000/api/applications/$APP_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "interview",
    "notes": "Phone screen scheduled"
  }'

# Delete application
curl -X DELETE http://localhost:5000/api/applications/$APP_ID \
  -H "Authorization: Bearer $TOKEN"
```

✅ **If all CRUD operations work, endpoints are functional!**

### **Test 5: Resume Operations (Already Working)**

```bash
# List resumes
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/resumes

# Upload resume (with valid base64 - test with small file)
curl -X POST http://localhost:5000/api/resumes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "test_resume.pdf",
    "file_base64": "data:application/pdf;base64,JVBERi0xLjQ...",
    "is_default": true
  }'
```

✅ **If resumes list and upload work, endpoints are functional!**

---

## 🎯 **Step 4: Frontend Integration Test**

### **Create Test User**

```bash
# Register test user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "frontend-test@test.com",
    "password": "Test123!@#",
    "full_name": "Frontend Test User"
  }'
```

**Expected:**
- ✅ Returns `access_token` and `refresh_token`
- ✅ Returns user object
- ✅ User has Free subscription (plan_type: "free", applications_limit: 10)

### **Test Frontend Pages**

1. **Login** (`/login`)
   - ✅ Can login with test credentials
   - ✅ Receives and stores tokens
   - ✅ Redirects to dashboard

2. **Dashboard** (`/dashboard`)
   - ✅ Shows stats (even if 0 applications)
   - ✅ Shows subscription info (Free plan)
   - ✅ No errors in console

3. **Profile** (`/settings/profile`)
   - ✅ Form loads with user data
   - ✅ Can update profile fields
   - ✅ Data persists after save and refresh

4. **Resumes** (`/resumes`)
   - ✅ Shows empty state initially
   - ✅ Can upload resume
   - ✅ Resume appears in list
   - ✅ Shows filename correctly

5. **AI Config** (`/ai-config`)
   - ✅ Can create configuration
   - ✅ Platforms and keywords save as arrays
   - ✅ Redirects to saved data page after save

6. **Saved Data** (`/saved-applicationdata`)
   - ✅ Shows empty state if no config
   - ✅ Shows config after creating one
   - ✅ Can edit config
   - ✅ Can delete config

7. **Applications** (`/applications`)
   - ✅ Shows empty state initially
   - ✅ Can create application manually
   - ✅ Can update status
   - ✅ Can add notes
   - ✅ Can delete application

8. **Account Settings** (`/settings/account`)
   - ✅ Can change password
   - ✅ Shows error for wrong current password
   - ✅ Validates new password strength

9. **Subscription** (`/settings/subscription`)
   - ✅ Shows Free plan
   - ✅ Shows 0/10 applications used
   - ✅ Shows upgrade options

---

## 🐛 **Common Issues & Solutions**

### **Issue: Still Getting 404 on `/api/search-config`**

**Cause:** Backend not restarted with latest code

**Solution:**
```bash
# Verify latest commit is deployed
git log --oneline -1
# Should show: "Fix frontend integration issues..."

# Restart server
pkill -f "flask run" && flask run
```

### **Issue: Profile Data Not Persisting**

**Cause:** Frontend not calling GET endpoint on page load

**Solution:** Ensure frontend calls `GET /api/auth/me` in `useEffect`:
```javascript
useEffect(() => {
  fetchProfile();
}, []);
```

### **Issue: Change Password Not Working**

**Cause:** Field names mismatch

**Solution:** Use `current_password` and `new_password` (not camelCase):
```javascript
{
  "current_password": "...",  // ✅ Correct
  "new_password": "..."       // ✅ Correct
}
```

### **Issue: CORS Errors**

**Cause:** Frontend URL not in CORS_ORIGINS

**Solution:**
```bash
# Add to .env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Restart server
```

### **Issue: Resume Upload "Unexpected token <"**

**Cause:** Using wrong endpoint or field names

**Solution:**
```javascript
// ✅ Correct
apiClient.post('/api/resumes', {  // NOT /api/resumes/upload
  filename: file.name,
  file_base64: base64,              // NOT "content"
  is_default: true
});
```

---

## 📊 **Verification Checklist**

Mark each item as complete:

### **Backend Deployment**
- [ ] Latest code pulled/deployed
- [ ] Backend server restarted
- [ ] Health endpoint returns 200
- [ ] No errors in server logs

### **Fixed Endpoints**
- [ ] GET `/api/search-config` returns 200 (not 404)
- [ ] GET `/api/auth/me` includes subscription
- [ ] POST `/api/auth/change-password` works
- [ ] POST `/api/applications` works
- [ ] PUT `/api/applications/{id}` works
- [ ] DELETE `/api/applications/{id}` works

### **Already Working Endpoints**
- [ ] POST `/api/resumes` (correct endpoint, not /upload)
- [ ] GET `/api/resumes` returns all resumes with filename
- [ ] All resume CRUD operations work
- [ ] Profile update and persistence work

### **Frontend Integration**
- [ ] Login works
- [ ] Dashboard loads
- [ ] Profile loads and persists
- [ ] Resumes show and persist
- [ ] AI config saves
- [ ] Saved data shows config
- [ ] Applications CRUD works
- [ ] Password change works
- [ ] Subscription shows Free plan

---

## 🎉 **Success Criteria**

All endpoints working when:

1. ✅ No 404 errors on any endpoint
2. ✅ Data persists after refresh
3. ✅ All CRUD operations functional
4. ✅ No CORS errors
5. ✅ Proper error messages shown
6. ✅ Subscription info displays correctly

---

## 📞 **Getting Help**

If issues persist after following this checklist:

1. **Check server logs** for detailed errors
2. **Check browser console** for frontend errors
3. **Test with cURL** to isolate frontend vs backend
4. **Verify environment variables** are set correctly
5. **Check database** for data persistence

**Documentation:**
- `COMPLETE_FRONTEND_INTEGRATION_GUIDE.md` - Full integration guide
- `API_ENDPOINTS_REFERENCE.md` - Endpoint documentation
- `FRONTEND_ISSUES_ANALYSIS.md` - Issue analysis
- `FRONTEND_TROUBLESHOOTING.md` - Debugging guide
