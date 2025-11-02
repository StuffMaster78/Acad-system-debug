# HTTPS Error Fix

## Problem
The Django development server is receiving HTTPS requests, but it only supports HTTP. This causes errors like:
```
code 400, message Bad request version
You're accessing the development server over HTTPS, but it only supports HTTP.
```

## Solution Applied

### 1. Security Settings Updated
Added explicit security settings to ensure HTTPS is disabled in development:
- `SECURE_SSL_REDIRECT = False` - No automatic redirect to HTTPS
- `SECURE_PROXY_SSL_HEADER = None` - Don't trust proxy headers
- `SESSION_COOKIE_SECURE = False` - Allow cookies over HTTP
- `CSRF_COOKIE_SECURE = False` - Allow CSRF cookies over HTTP

### 2. How to Access the Server

**Correct URLs (HTTP only):**
```
http://localhost:8000/
http://localhost:8000/api/v1/
http://localhost:8000/api/v1/docs/swagger/
http://127.0.0.1:8000/
```

**❌ Wrong URLs (HTTPS):**
```
https://localhost:8000/  # DON'T USE HTTPS!
```

## Additional Troubleshooting

### If you still see HTTPS errors:

1. **Clear browser HSTS cache:**
   - Chrome: `chrome://net-internals/#hsts`
   - Firefox: Clear site data
   - Safari: Clear browsing data

2. **Check for proxy/load balancer:**
   - Make sure no reverse proxy is forwarding HTTPS requests
   - Check if any monitoring/healthcheck services are using HTTPS

3. **Verify Docker port mapping:**
   ```bash
   docker-compose ps
   # Should show: 0.0.0.0:8000->8000/tcp
   ```

4. **Test directly:**
   ```bash
   curl http://localhost:8000/api/v1/
   # Should work, not return SSL errors
   ```

5. **Check browser URL:**
   - Make sure you're typing `http://` not `https://`
   - Remove any browser auto-complete that adds HTTPS

## For Production

When deploying to production:
1. Use a reverse proxy (Nginx/Apache) with SSL termination
2. Set `SECURE_SSL_REDIRECT = True`
3. Set `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
4. Set `SESSION_COOKIE_SECURE = True`
5. Set `CSRF_COOKIE_SECURE = True`

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for complete production setup.

