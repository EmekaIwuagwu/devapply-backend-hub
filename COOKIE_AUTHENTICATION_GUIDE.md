# Cookie-Based Authentication Guide

## Why Use Cookies?

LinkedIn and other job platforms have aggressive bot detection that blocks automated logins. Cookie-based authentication bypasses this by using your existing logged-in session.

**Benefits:**
- ✅ Bypasses bot detection completely
- ✅ No CAPTCHA challenges
- ✅ More reliable and faster
- ✅ Cookies last 2-4 weeks
- ✅ Simple 2-minute setup

---

## How to Get Your LinkedIn Cookies

### Step 1: Log into LinkedIn Normally

1. Open your regular browser (Chrome, Firefox, Edge, etc.)
2. Go to https://www.linkedin.com
3. Log in with your email and password
4. Complete any 2FA/security challenges if prompted
5. Make sure you're on your LinkedIn feed

### Step 2: Open Browser DevTools

**Chrome/Edge:**
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Or `Cmd+Option+I` (Mac)

**Firefox:**
- Press `F12` or `Ctrl+Shift+I` (Windows/Linux)
- Or `Cmd+Option+I` (Mac)

### Step 3: Navigate to Cookies

1. Click the **"Application"** tab (Chrome/Edge) or **"Storage"** tab (Firefox)
2. In the left sidebar, expand **"Cookies"**
3. Click on `https://www.linkedin.com`

You'll see a list of all LinkedIn cookies.

### Step 4: Find Important Cookies

LinkedIn requires these main cookies for authentication:

**Required:**
- `li_at` - Your session token (MOST IMPORTANT)
- `JSESSIONID` - Session ID

**Recommended (optional but helpful):**
- `liap` - Authentication persistence
- `bcookie` - Browser cookie
- `bscookie` - Browser secure cookie

### Step 5: Copy Cookie Values

For each cookie:
1. Click on the cookie name in the list
2. Look for the "Value" field
3. Copy the entire value (it's usually a long string)
4. Save it somewhere temporarily (notepad, etc.)

Example format:
```
li_at: AQEDARvHGq4CwUo2AAABk5F...  (very long string)
JSESSIONID: ajax:1234567890123456789
```

### Step 6: Send Cookies to DevApply API

**Using cURL:**
```bash
curl -X POST http://YOUR_SERVER_IP/api/credentials/linkedin/cookies \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cookies": {
      "li_at": "YOUR_LI_AT_VALUE_HERE",
      "JSESSIONID": "YOUR_JSESSIONID_VALUE_HERE",
      "liap": "YOUR_LIAP_VALUE_HERE",
      "bcookie": "YOUR_BCOOKIE_VALUE_HERE"
    }
  }'
```

**Using Postman/Thunder Client:**
1. Method: `POST`
2. URL: `http://YOUR_SERVER_IP/api/credentials/linkedin/cookies`
3. Headers:
   - `Authorization: Bearer YOUR_JWT_TOKEN`
   - `Content-Type: application/json`
4. Body (JSON):
```json
{
  "cookies": {
    "li_at": "YOUR_LI_AT_VALUE_HERE",
    "JSESSIONID": "YOUR_JSESSIONID_VALUE_HERE"
  }
}
```

**Using Python:**
```python
import requests

url = "http://YOUR_SERVER_IP/api/credentials/linkedin/cookies"
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN",
    "Content-Type": "application/json"
}
data = {
    "cookies": {
        "li_at": "YOUR_LI_AT_VALUE_HERE",
        "JSESSIONID": "YOUR_JSESSIONID_VALUE_HERE"
    }
}

response = requests.post(url, headers=headers, json=data)
print(response.json())
```

---

## Testing Your Setup

After saving cookies, trigger a job application to test:

```bash
cd ~/devapply-backend-hub
python test_immediate_apply.py
```

Watch the logs:
```bash
tail -f logs/celery-worker.log
```

**Success looks like:**
```
[LinkedIn Bot] 🍪 Using saved session cookies...
[LinkedIn Bot] Loading LinkedIn homepage...
[LinkedIn Bot] Adding 4 cookies to browser...
[LinkedIn Bot] Verifying cookie-based login...
[LinkedIn Bot] ✅ Cookie-based login successful!
[LinkedIn Bot] Searching for jobs...
```

---

## How Often to Update Cookies?

- **LinkedIn cookies typically last 2-4 weeks**
- You'll get notified when cookies expire
- Simply repeat the process to get fresh cookies
- Takes only 2 minutes

---

## Security Notes

**Is it safe?**
- ✅ Cookies are encrypted in the database (same as passwords)
- ✅ Cookies expire automatically
- ✅ You can revoke access anytime by logging out of LinkedIn
- ✅ Only works for your DevApply account

**Best practices:**
- Don't share your cookies with anyone
- Use a strong DevApply password
- Regularly update cookies (every 2-3 weeks)
- Log out of LinkedIn on shared computers

---

## Troubleshooting

### "Cookies expired or invalid"
- Your cookies have expired
- Simply get fresh cookies and update

### "Cookie-based login failed"
- Make sure you're logged into LinkedIn when copying cookies
- Check that you copied the full `li_at` value (it's long!)
- Try copying cookies again

### Still having issues?
1. Clear browser cache and cookies
2. Log out of LinkedIn completely
3. Log back in
4. Get fresh cookies
5. Update in DevApply

---

## For Indeed (Same Process)

The process is identical for Indeed:

1. Log into https://www.indeed.com
2. Open DevTools → Application/Storage → Cookies
3. Copy the important cookies (mainly session cookies)
4. Send to: `POST /api/credentials/indeed/cookies`

---

## Alternative: Browser Extension (Coming Soon)

We're working on a simple browser extension to make this even easier:
- One-click cookie capture
- Automatic updates when cookies refresh
- No manual copying needed

Stay tuned!
