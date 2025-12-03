# Authentication Documentation

## Overview

The Writing System platform implements a comprehensive, production-grade authentication system with multiple authentication methods, robust security features, and support for multi-tenancy. This document provides complete documentation for all authentication flows, API endpoints, and security features.

**Base URL**: `/api/v1/auth/`

---

## Table of Contents

1. [Authentication Methods](#authentication-methods)
2. [Registration](#registration)
3. [Login Flows](#login-flows)
4. [Password Management](#password-management)
5. [Token Management](#token-management)
6. [Session Management](#session-management)
7. [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
8. [Magic Link Authentication](#magic-link-authentication)
9. [Security Features](#security-features)
10. [Account Management](#account-management)
11. [API Endpoints Reference](#api-endpoints-reference)
12. [Frontend Integration](#frontend-integration)
13. [Error Handling](#error-handling)
14. [Security Best Practices](#security-best-practices)
15. [Troubleshooting](#troubleshooting)

---

## Authentication Methods

The platform supports multiple authentication methods:

1. **Email/Password** - Traditional authentication with JWT tokens
2. **Magic Link** - Passwordless authentication via email
3. **Two-Factor Authentication (2FA)** - Additional security layer with TOTP
4. **Session-based** - For web applications with session cookies

---

## Registration

### User Registration

**Endpoint**: `POST /api/v1/auth/register/`

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "referral_code": "REF123" // Optional
}
```

**Response** (201 Created):
```json
{
  "message": "Registration successful. Please check your email for activation.",
  "user_id": 1,
  "email": "user@example.com"
}
```

**Error Responses**:
- `400 Bad Request`: 
  - Email already exists
  - Username already exists
  - Password validation failed
  - Missing required fields
- `429 Too Many Requests`: Rate limit exceeded

**Registration Flow**:
1. User submits registration form
2. System validates input (email, username, password strength)
3. User account created with default role: `client`
4. Account is set to `is_active=True` (immediate activation)
5. Activation email sent (if email verification enabled)
6. Referral code processed (if provided)

**Password Requirements**:
- Minimum 8 characters
- Cannot be too similar to username/email
- Cannot be a common password
- Recommended: Mix of uppercase, lowercase, numbers, and special characters

---

## Login Flows

### 1. Email/Password Login

**Endpoint**: `POST /api/v1/auth/login/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false // Optional, extends session duration
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "uuid-string",
  "expires_in": 3600
}
```

**2FA Required Response** (202 Accepted):
```json
{
  "requires_2fa": true,
  "session_id": "uuid-string",
  "message": "2FA verification required."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid credentials
- `403 Forbidden`: Account disabled or locked
- `429 Too Many Requests`: Account locked due to failed attempts

**Login Process**:
1. User submits credentials
2. System authenticates user
3. Checks account status (active, locked, suspended)
4. Checks for 2FA requirement
5. If 2FA enabled, returns session_id for 2FA verification
6. If no 2FA, generates JWT tokens
7. Creates login session
8. Logs security event
9. Returns tokens and user info

### 2. Login with 2FA

If user has 2FA enabled, login requires additional step:

**Step 1: Initial Login** (same as above, returns `requires_2fa: true`)

**Step 2: Verify 2FA Code**

**Endpoint**: `POST /api/v1/auth/2fa/totp/login/`

**Request Body**:
```json
{
  "session_id": "uuid-string-from-login",
  "totp_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...},
  "session_id": "uuid-string"
}
```

---

## Password Management

### Change Password (Authenticated)

**Endpoint**: `POST /api/v1/auth/change-password/`

**Authentication**: Required

**Request Body**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully."
}
```

**Security Features**:
- Current password verification required
- Password strength validation
- Session maintained after change
- Security event logged
- Notification sent to user

### Request Password Reset

**Endpoint**: `POST /api/v1/auth/password-reset/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "detail": "If that email exists, a reset link was sent."
}
```

**Notes**:
- Always returns success (security best practice)
- Reset token expires in 1 hour
- Only one active reset token per user
- Rate limited: 3 requests per hour per email

### Confirm Password Reset

**Endpoint**: `POST /api/v1/auth/password-reset/confirm/`

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "reset-token-from-email",
  "password": "newpassword123"
}
```

**Response** (200 OK):
```json
{
  "detail": "Password reset successful."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token, weak password

---

## Token Management

### JWT Token Structure

The platform uses JWT (JSON Web Tokens) for authentication:

**Access Token**:
- Expires in: 1 hour (configurable)
- Contains: User ID, email, role, permissions
- Used for: API authentication

**Refresh Token**:
- Expires in: 7 days (configurable)
- Used for: Obtaining new access tokens
- Stored securely: Encrypted in database

**Token Payload Example**:
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "role": "client",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Refresh Access Token

**Endpoint**: `POST /api/v1/auth/refresh-token/`

**Authentication**: Not required (but requires valid refresh token)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 3600
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired refresh token
- `401 Unauthorized`: Token revoked or blacklisted

### Token Blacklisting

Tokens can be blacklisted (revoked) for security:
- On logout
- On password change (optional)
- On suspicious activity
- Manually by admin

Blacklisted tokens are stored in Redis cache for fast lookup.

---

## Session Management

### Active Sessions

**Endpoint**: `GET /api/v1/auth/user-sessions/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": "uuid",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "device_type": "desktop",
      "location": "New York, US",
      "last_activity": "2025-12-03T10:30:00Z",
      "is_current": true,
      "created_at": "2025-12-03T09:00:00Z"
    }
  ]
}
```

### Logout

**Endpoint**: `POST /api/v1/auth/logout/`

**Authentication**: Required

**Query Parameters**:
- `logout_all` (optional): If `true`, logout from all devices

**Request Body** (optional):
```json
{
  "logout_all": false
}
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully."
}
```

**Behavior**:
- Default: Only current session invalidated
- `logout_all=true`: All sessions invalidated
- All tokens revoked and blacklisted
- Security event logged

### Session Timeout

Sessions automatically expire based on:
- **Default**: 24 hours
- **Remember Me**: 30 days
- **Inactive**: Configurable timeout (default: 2 hours)

Session timeout warnings are shown to users before expiration.

---

## Two-Factor Authentication (2FA)

### Setup 2FA

**Endpoint**: `POST /api/v1/auth/2fa/totp/setup/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": [
    "1234-5678",
    "2345-6789",
    ...
  ],
  "message": "Scan QR code with authenticator app"
}
```

**Process**:
1. User requests 2FA setup
2. System generates TOTP secret
3. QR code generated for easy setup
4. Backup codes generated (10 codes)
5. User scans QR code with authenticator app
6. User verifies setup with TOTP code

### Verify 2FA Setup

**Endpoint**: `POST /api/v1/auth/2fa/totp/verify/`

**Authentication**: Required

**Request Body**:
```json
{
  "totp_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "2FA enabled successfully.",
  "backup_codes": ["1234-5678", ...]
}
```

### Disable 2FA

**Endpoint**: `DELETE /api/v1/auth/mfa-settings/{id}/`

**Authentication**: Required

**Request Body**:
```json
{
  "password": "userpassword",
  "backup_code": "1234-5678" // Optional, can use password or backup code
}
```

**Response** (200 OK):
```json
{
  "message": "2FA disabled successfully."
}
```

### MFA Settings

**Endpoint**: `GET /api/v1/auth/mfa-settings/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "is_mfa_enabled": true,
  "backup_codes_remaining": 8,
  "last_used": "2025-12-01T10:00:00Z"
}
```

---

## Magic Link Authentication

### Request Magic Link

**Endpoint**: `POST /api/v1/auth/magic-link/request/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "detail": "Magic link sent to your email."
}
```

**Notes**:
- Magic link expires in 15 minutes
- Only one active magic link per user
- Previous links revoked when new one requested
- Rate limited: 3 requests per hour per email

### Verify Magic Link

**Endpoint**: `POST /api/v1/auth/magic-link/verify/`

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "uuid-token-from-email"
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...},
  "session_id": "uuid-string",
  "message": "Welcome back!"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token
- `403 Forbidden`: Account disabled
- `404 Not Found`: Token not found

---

## Security Features

### Rate Limiting

All authentication endpoints are rate-limited:

| Endpoint | Limit | Window |
|----------|-------|--------|
| Login | 5 attempts | 1 minute |
| Magic Link Request | 3 requests | 1 hour |
| Password Reset | 3 requests | 1 hour |
| Account Unlock | 3 requests | 1 hour |
| Registration | 5 requests | 1 hour |

**Rate Limit Headers**:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1638360000
```

### Account Lockout

**Smart Lockout System**:
- Progressive lockout duration
- IP-based and user-based tracking
- Trusted device exemption
- Automatic unlock after duration

**Lockout Thresholds**:
- 3 failed attempts: 5-minute lockout
- 5 failed attempts: 30-minute lockout
- 10 failed attempts: 2-hour lockout
- 15 failed attempts: 24-hour lockout

**Lockout Response**:
```json
{
  "error": "Account temporarily locked",
  "message": "Too many failed login attempts",
  "lockout_until": "2025-12-03T11:00:00Z",
  "lockout_duration_minutes": 30,
  "unlock_options": ["email", "wait"]
}
```

### Failed Login Tracking

Failed login attempts are tracked:
- Per user
- Per IP address
- Per website (multi-tenant)
- With timestamps and user agents

### Security Events

All authentication events are logged:

**Event Types**:
- `login` - Successful login
- `login_failed` - Failed login attempt
- `logout` - User logout
- `password_change` - Password changed
- `password_reset` - Password reset requested/completed
- `2fa_enabled` - 2FA enabled
- `2fa_disabled` - 2FA disabled
- `account_locked` - Account locked
- `account_unlocked` - Account unlocked
- `suspicious_activity` - Suspicious activity detected

**Security Event Model**:
```json
{
  "event_type": "login",
  "severity": "low",
  "is_suspicious": false,
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "device": "Desktop",
  "location": "New York, US",
  "timestamp": "2025-12-03T10:00:00Z"
}
```

### IP Blocking

Suspicious IP addresses can be blocked:
- Automatic blocking after repeated failed attempts
- Manual blocking by admin
- Temporary or permanent blocks
- IP whitelist for trusted networks

### Device Tracking

Trusted devices are tracked:
- Device fingerprinting
- Device name and type
- Last used timestamp
- Trusted device exemption from lockout

---

## Account Management

### Account Unlock Request

**Endpoint**: `POST /api/v1/auth/account-unlock/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response** (200 OK):
```json
{
  "detail": "If that email exists, an unlock link was sent."
}
```

### Confirm Account Unlock

**Endpoint**: `POST /api/v1/auth/account-unlock/confirm/`

**Authentication**: Not required

**Request Body**:
```json
{
  "token": "unlock-token-from-email"
}
```

**Response** (200 OK):
```json
{
  "detail": "Account unlocked successfully."
}
```

### Account Status

**Endpoint**: `GET /api/v1/auth/user/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "client",
  "is_active": true,
  "is_locked": false,
  "last_login": "2025-12-03T10:00:00Z",
  "created_at": "2025-11-01T10:00:00Z"
}
```

---

## API Endpoints Reference

### Authentication Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/login/` | No | Email/password login |
| POST | `/api/v1/auth/register/` | No | Register new account |
| POST | `/api/v1/auth/logout/` | Yes | Logout user |
| POST | `/api/v1/auth/refresh-token/` | No | Refresh access token |

### Password Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/change-password/` | Yes | Change password |
| POST | `/api/v1/auth/password-reset/` | No | Request password reset |
| POST | `/api/v1/auth/password-reset/confirm/` | No | Confirm password reset |

### 2FA Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/2fa/totp/setup/` | Yes | Setup 2FA |
| POST | `/api/v1/auth/2fa/totp/verify/` | Yes | Verify 2FA setup |
| POST | `/api/v1/auth/2fa/totp/login/` | No | Login with 2FA code |
| GET | `/api/v1/auth/mfa-settings/` | Yes | Get 2FA settings |
| DELETE | `/api/v1/auth/mfa-settings/{id}/` | Yes | Disable 2FA |

### Magic Link Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/magic-link/request/` | No | Request magic link |
| POST | `/api/v1/auth/magic-link/verify/` | No | Verify magic link |

### Session Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/auth/user-sessions/` | Yes | List active sessions |
| POST | `/api/v1/auth/session-management/revoke/{id}/` | Yes | Revoke specific session |
| POST | `/api/v1/auth/session-management/revoke-all/` | Yes | Revoke all sessions |

### Account Management

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/account-unlock/` | No | Request account unlock |
| POST | `/api/v1/auth/account-unlock/confirm/` | No | Confirm account unlock |
| GET | `/api/v1/auth/user/` | Yes | Get current user info |

---

## Frontend Integration

### Token Storage

**Recommended Approach**: Store tokens securely

```javascript
// Option 1: httpOnly Cookies (Most Secure)
// Tokens automatically sent with requests
// Not accessible via JavaScript

// Option 2: Secure Storage (LocalStorage/SessionStorage)
localStorage.setItem('access_token', accessToken);
localStorage.setItem('refresh_token', refreshToken);

// Option 3: Memory (Most Secure, but lost on refresh)
let accessToken = null; // Store in memory only
```

### Token Refresh

Implement automatic token refresh:

```javascript
// Intercept 401 responses
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      
      try {
        const { data } = await axios.post('/api/v1/auth/refresh-token/', {
          refresh: refreshToken
        });
        
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        
        // Retry original request
        error.config.headers.Authorization = `Bearer ${data.access}`;
        return axios.request(error.config);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);
```

### Request Headers

Include token in API requests:

```javascript
axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
```

### Login Flow Example

```javascript
async function login(email, password, rememberMe) {
  try {
    const response = await axios.post('/api/v1/auth/login/', {
      email,
      password,
      remember_me: rememberMe
    });
    
    if (response.data.requires_2fa) {
      // Redirect to 2FA verification
      return { requires2FA: true, sessionId: response.data.session_id };
    }
    
    // Store tokens
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    
    // Store user info
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return { success: true, user: response.data.user };
  } catch (error) {
    return { error: error.response?.data?.detail || 'Login failed' };
  }
}
```

### Magic Link Flow

```javascript
// Request magic link
async function requestMagicLink(email) {
  await axios.post('/api/v1/auth/magic-link/request/', { email });
}

// Verify magic link (from email redirect)
async function verifyMagicLink(token) {
  const response = await axios.post('/api/v1/auth/magic-link/verify/', {
    token
  });
  
  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);
  
  return response.data;
}
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": "Error message",
  "detail": "Additional details",
  "code": "error_code"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `authentication_failed` | Invalid credentials | 401 |
| `account_locked` | Account locked | 429 |
| `account_disabled` | Account disabled | 403 |
| `token_expired` | Token expired | 401 |
| `token_invalid` | Invalid token | 401 |
| `rate_limit_exceeded` | Too many requests | 429 |
| `validation_error` | Input validation failed | 400 |
| `permission_denied` | Insufficient permissions | 403 |
| `2fa_required` | 2FA verification required | 202 |
| `2fa_invalid` | Invalid 2FA code | 400 |

### Error Handling Example

```javascript
try {
  const response = await axios.post('/api/v1/auth/login/', credentials);
  // Handle success
} catch (error) {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // Invalid credentials
        showError('Invalid email or password');
        break;
      case 403:
        // Account disabled
        showError('Account is disabled. Please contact support.');
        break;
      case 429:
        // Rate limited
        const retryAfter = error.response.headers['retry-after'];
        showError(`Too many attempts. Try again in ${retryAfter} seconds.`);
        break;
      default:
        showError('An error occurred. Please try again.');
    }
  }
}
```

---

## Security Best Practices

### For Developers

1. **Token Security**
   - Never expose tokens in URLs
   - Use HTTPS for all requests
   - Implement token refresh before expiry
   - Clear tokens on logout

2. **Password Security**
   - Enforce strong password requirements
   - Hash passwords (already handled by backend)
   - Never log passwords
   - Implement password strength meter

3. **Session Security**
   - Implement session timeout warnings
   - Allow users to view active sessions
   - Enable logout from all devices
   - Track suspicious sessions

4. **2FA Implementation**
   - Encourage 2FA for all users
   - Provide backup codes
   - Support multiple authenticator apps
   - Allow 2FA recovery

5. **Rate Limiting**
   - Implement client-side rate limiting
   - Show user-friendly error messages
   - Display retry countdown
   - Prevent form spam

### For Users

1. **Password Security**
   - Use strong, unique passwords
   - Don't reuse passwords
   - Change password regularly
   - Use password manager

2. **2FA**
   - Enable 2FA for account
   - Store backup codes securely
   - Use authenticator app
   - Keep backup codes safe

3. **Session Management**
   - Logout from shared devices
   - Review active sessions regularly
   - Report suspicious activity
   - Use "Remember Me" only on trusted devices

4. **Account Security**
   - Monitor login activity
   - Review security events
   - Report suspicious activity
   - Keep email address updated

---

## Troubleshooting

### Common Issues

#### 1. "Invalid credentials" error

**Possible Causes**:
- Incorrect email or password
- Account locked
- Account disabled

**Solutions**:
- Verify credentials
- Check account status
- Request account unlock if locked
- Contact support if disabled

#### 2. Token expired

**Solution**:
- Implement automatic token refresh
- Redirect to login if refresh fails
- Store refresh token securely

#### 3. Account locked

**Solution**:
- Wait for lockout period to expire
- Request account unlock via email
- Contact support for immediate unlock

#### 4. 2FA code not working

**Possible Causes**:
- Clock sync issue
- Wrong authenticator app
- Code expired

**Solutions**:
- Check device time sync
- Verify correct authenticator app
- Use backup code if available
- Re-setup 2FA if needed

#### 5. Magic link not received

**Possible Causes**:
- Email in spam folder
- Incorrect email address
- Rate limited

**Solutions**:
- Check spam folder
- Verify email address
- Wait before requesting again
- Contact support if issue persists

---

## Multi-Tenancy

The authentication system supports multi-tenant architecture:

- **Website Context**: Users belong to specific websites
- **Isolated Sessions**: Sessions are website-specific
- **Scoped Data**: All authentication data is website-scoped
- **Cross-Tenant Prevention**: Users cannot access other websites' data

**Website Detection**:
1. `X-Website-ID` header
2. User's assigned website
3. Default active website

---

## Configuration

### JWT Settings

```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

### Rate Limiting

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/minute',
        'user': '1000/day',
    }
}
```

### Session Settings

```python
# settings.py
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True
```

---

## API Testing

### Using cURL

**Login**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

**Authenticated Request**:
```bash
curl -X GET http://localhost:8000/api/v1/auth/user/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Using Postman

1. Create new request
2. Set method and URL
3. Add headers:
   - `Content-Type: application/json`
   - `Authorization: Bearer YOUR_ACCESS_TOKEN`
4. Add body (for POST requests)
5. Send request

---

## Support

For authentication issues:

1. **Check Documentation**: Review this documentation
2. **Review Error Messages**: Check API error responses
3. **Check Account Status**: Verify account is active and not locked
4. **Contact Support**: If issues persist, contact support team

**Support Channels**:
- Email: support@example.com
- Support Tickets: `/support/tickets/`
- Documentation: `/api/v1/docs/`

---

## Version History

- **v1.0.0** (December 2025) - Initial authentication documentation
- Includes all authentication methods, security features, and API endpoints

---

## Additional Resources

- [User Journey Documentation](./USER_JOURNEY_DOCUMENTATION.md)
- [API Documentation](./COMPLETE_API_DOCUMENTATION.md)
- [Security Best Practices](./SECURITY_BEST_PRACTICES.md)

---

*Last Updated: December 3, 2025*

