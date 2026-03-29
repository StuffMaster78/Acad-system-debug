# Authentication System Documentation

## Overview

The Writing System Backend provides a comprehensive, secure, and user-friendly authentication system with multiple login methods, password management, and security features.

**Base URL**: `/api/v1/auth/`

---

## Authentication Methods

### 1. Email/Password Login

Traditional email and password authentication with JWT tokens.

**Endpoint**: `POST /api/v1/auth/login/`

**Authentication**: Not required

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
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
- `400 Bad Request`: Invalid credentials or missing fields
- `403 Forbidden`: Account disabled or locked
- `429 Too Many Requests`: Rate limit exceeded

---

### 2. Magic Link Login

Passwordless login via email magic link. Users request a link and click it to authenticate.

#### Request Magic Link

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
  "detail": "Magic link sent."
}
```

**Notes**:
- Magic link expires in 15 minutes
- Only one active magic link per user at a time
- Previous links are revoked when a new one is requested
- Rate limited to prevent abuse

#### Verify Magic Link

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
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "uuid-string",
  "expires_in": 3600,
  "message": "Welcome back, user@example.com!"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token
- `403 Forbidden`: Account disabled
- `404 Not Found`: Token not found

---

### 3. Two-Factor Authentication (2FA)

For users with 2FA enabled, login requires an additional TOTP code.

#### Setup 2FA

**Endpoint**: `POST /api/v1/auth/2fa/totp/setup/`

**Authentication**: Required

**Response** (200 OK):
```json
{
  "secret": "base32-secret",
  "qr_code": "data:image/png;base64,...",
  "backup_codes": ["code1", "code2", ...]
}
```

#### Verify 2FA Code

**Endpoint**: `POST /api/v1/auth/verify-2fa/`

**Authentication**: Not required (but requires valid session_id from login)

**Request Body**:
```json
{
  "user_id": 1,
  "session_id": "uuid-string",
  "totp_code": "123456"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {...},
  "session_id": "uuid-string",
  "expires_in": 3600
}
```

---

## Password Management

### 1. Change Password (Authenticated Users)

Change password for logged-in users.

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

**Error Responses**:
- `400 Bad Request`: 
  - Current password incorrect
  - New password doesn't match confirmation
  - New password same as current
  - Password validation failed (weak password)
- `401 Unauthorized`: Not authenticated

**Password Requirements**:
- Minimum 8 characters
- Cannot be too similar to user information
- Cannot be a common password
- Must contain a mix of letters, numbers, and special characters (configurable)

**Security Features**:
- Current password verification required
- Password strength validation
- Session maintained after password change (no logout)
- Audit log entry created
- Security notification sent

---

### 2. Password Reset (Forgot Password)

Request password reset link via email.

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
- Always returns success message (security best practice)
- Reset link expires in 1 hour
- Only one active reset token per user
- Rate limited to prevent abuse

#### Confirm Password Reset

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

### Refresh Access Token

Refresh expired access token using refresh token.

**Endpoint**: `POST /api/v1/auth/refresh-token/`

**Authentication**: Not required

**Request Body**:
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 3600
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired refresh token

---

### Logout

Logout user and invalidate tokens/session.

**Endpoint**: `POST /api/v1/auth/logout/`

**Authentication**: Required

**Query Parameters**:
- `logout_all` (optional): If `true`, logout from all devices

**Response** (200 OK):
```json
{
  "message": "Logged out successfully."
}
```

**Notes**:
- By default, only current session is invalidated
- `logout_all=true` invalidates all sessions for the user
- All tokens are revoked

---

## Registration

**Endpoint**: `POST /api/v1/auth/register/`

**Authentication**: Not required

**Request Body**:
```json
{
  "username": "johndoe",
  "email": "user@example.com",
  "password": "password123"
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

**Notes**:
- User account is created but may require email activation
- Activation link sent via email
- Password must meet strength requirements

---

## Account Security

### Account Unlock

Request account unlock if locked due to failed login attempts.

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

#### Confirm Account Unlock

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

---

## Security Features

### Rate Limiting

All authentication endpoints are rate-limited to prevent abuse:

- **Login**: 5 attempts per minute
- **Magic Link**: 3 requests per hour per email
- **Password Reset**: 3 requests per hour per email
- **Account Unlock**: 3 requests per hour per email

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

### Account Lockout

After multiple failed login attempts, accounts are temporarily locked:
- Lockout duration: 30 minutes (configurable)
- Lockout threshold: 5 failed attempts (configurable)
- Automatic unlock after duration expires
- Manual unlock via account unlock endpoint

### Session Management

- Sessions tracked with device information
- IP address and user agent logged
- Multiple sessions supported per user
- Session revocation on logout
- Session expiry based on `remember_me` flag

### Audit Logging

All authentication events are logged:
- Login attempts (successful and failed)
- Logout events
- Password changes
- Magic link usage
- 2FA verification
- Account unlock requests

---

## Best Practices

### For Frontend Developers

1. **Token Storage**: Store tokens securely (httpOnly cookies or secure storage)
2. **Token Refresh**: Implement automatic token refresh before expiry
3. **Error Handling**: Handle all error responses gracefully
4. **Loading States**: Show loading indicators during authentication
5. **Session Management**: Implement logout on token expiry
6. **Magic Link Flow**: Handle magic link redirects properly
7. **2FA Flow**: Guide users through 2FA setup and verification

### For Users

1. **Strong Passwords**: Use strong, unique passwords
2. **2FA**: Enable 2FA for additional security
3. **Magic Links**: Use magic links for quick, secure login
4. **Session Management**: Logout from shared devices
5. **Password Changes**: Change password regularly
6. **Account Security**: Monitor login activity

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": "Error message",
  "detail": "Additional details (optional)"
}
```

### Common Error Codes

- `authentication_failed`: Invalid credentials
- `account_locked`: Account locked due to failed attempts
- `account_disabled`: Account disabled by admin
- `token_expired`: Token has expired
- `token_invalid`: Invalid token
- `rate_limit_exceeded`: Too many requests
- `validation_error`: Input validation failed
- `permission_denied`: Insufficient permissions

---

## Multi-Tenancy

All authentication endpoints support multi-tenancy:
- Users are scoped to their website
- Magic links are website-specific
- Password resets are website-specific
- Sessions are website-specific

Website context is automatically determined from:
1. Request headers (X-Website-ID)
2. User's assigned website
3. Default active website

---

## API Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/v1/auth/login/` | No | Email/password login |
| POST | `/api/v1/auth/register/` | No | Register new account |
| POST | `/api/v1/auth/logout/` | Yes | Logout user |
| POST | `/api/v1/auth/refresh-token/` | No | Refresh access token |
| POST | `/api/v1/auth/verify-2fa/` | No | Verify 2FA code |
| POST | `/api/v1/auth/change-password/` | Yes | Change password |
| POST | `/api/v1/auth/password-reset/` | No | Request password reset |
| POST | `/api/v1/auth/password-reset/confirm/` | No | Confirm password reset |
| POST | `/api/v1/auth/magic-link/request/` | No | Request magic link |
| POST | `/api/v1/auth/magic-link/verify/` | No | Verify magic link |
| POST | `/api/v1/auth/account-unlock/` | No | Request account unlock |
| POST | `/api/v1/auth/account-unlock/confirm/` | No | Confirm account unlock |

---

## Interactive Documentation

For interactive API documentation:
- **Swagger UI**: `/api/v1/docs/swagger/`
- **ReDoc**: `/api/v1/docs/redoc/`

---

## Support

For authentication issues:
1. Check this documentation
2. Review error messages
3. Check account status (locked/disabled)
4. Contact support if issues persist

---

**Last Updated**: 2024-12-19  
**Version**: 1.0.0

