# Fix: HTTPS Errors in Django Development Server

## Problem
You're seeing errors like:
```
code 400, message Bad request version
You're accessing the development server over HTTPS, but it only supports HTTP.
```

## Solution

### 1. Always Use HTTP (not HTTPS)

**✅ Correct URLs:**
- `http://localhost:8000/` (not https://)
- `http://localhost:8000/api/v1/`
- `http://localhost:8000/admin/`

**❌ Wrong URLs:**
- `https://localhost:8000/` ← DON'T USE THIS!

### 2. Clear Browser HSTS Cache

Your browser may have cached HSTS (HTTP Strict Transport Security) for localhost, forcing HTTPS.

**Chrome/Edge:**
1. Go to: `chrome://net-internals/#hsts`
2. In "Delete domain security policies", enter: `localhost`
3. Click "Delete"
4. Also delete: `127.0.0.1`

**Firefox:**
1. Clear site data for localhost
2. Or: `about:preferences#privacy` → Clear Data

**Safari:**
1. Safari → Preferences → Privacy
2. Remove All Website Data
3. Or just clear localhost

### 3. Check Frontend Configuration

Make sure your frontend `.env` file uses HTTP:

```env
VITE_API_FULL_URL=http://localhost:8000/api/v1
# NOT https://localhost:8000/api/v1
```

### 4. Restart Everything

After clearing browser cache:
```bash
docker-compose restart web
```

### 5. Test with curl

Test that HTTP works:
```bash
curl http://localhost:8000/api/v1/
# Should return JSON, not SSL errors
```

### 6. Check for Monitoring Tools

If you have healthcheck or monitoring tools, make sure they're using HTTP:
```bash
# Check what's connecting
docker-compose logs web | grep -i https
```

## Django Settings (Already Configured)

The settings already have HTTPS disabled:
```python
SECURE_SSL_REDIRECT = False  # No HTTPS redirect
SECURE_PROXY_SSL_HEADER = None  # Don't trust proxy
SESSION_COOKIE_SECURE = False  # Allow HTTP cookies
CSRF_COOKIE_SECURE = False  # Allow HTTP CSRF
```

## Quick Fix

1. **Clear browser HSTS cache** (see step 2 above)
2. **Verify you're using `http://` not `https://`** in browser
3. **Check frontend `.env` file** uses HTTP
4. **Restart server**: `docker-compose restart web`

These errors are harmless but annoying - they're just failed HTTPS handshake attempts. The server will continue working on HTTP.

