# Streamlined Authentication System Guide
## User-Friendly & Secure Authentication for Clients

This guide provides a comprehensive overview of the authentication system, focusing on making it easy for clients to manage their accounts securely.

**Base URL**: `/api/v1/auth/`

---

## Quick Reference: Client Authentication Endpoints

### 🔐 Login Methods

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| **Email/Password** | `POST /api/v1/auth/login/` | No | Traditional login with email and password |
| **Magic Link** | `POST /api/v1/auth/magic-link/request/` | No | Passwordless login via email link |
| **Magic Link Verify** | `POST /api/v1/auth/magic-link/verify/` | No | Verify magic link token and get JWT tokens |

### 🔑 Password Management

| Action | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| **Change Password** | `POST /api/v1/auth/change-password/` | ✅ Yes | Change password for logged-in users |
| **Request Password Reset** | `POST /api/v1/auth/password-reset/` | No | Request password reset link via email |
| **Confirm Password Reset** | `POST /api/v1/auth/password-reset/confirm/` | No | Reset password using token from email |

### 🔄 Token Management

| Action | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| **Refresh Token** | `POST /api/v1/auth/refresh-token/` | No | Get new access token using refresh token |
| **Logout** | `POST /api/v1/auth/logout/` | ✅ Yes | Logout and invalidate tokens |

### 🔒 Security Features

| Feature | Endpoint | Auth Required | Description |
|---------|----------|---------------|-------------|
| **2FA Setup** | `POST /api/v1/auth/2fa/totp/setup/` | ✅ Yes | Set up two-factor authentication |
| **2FA Verify** | `POST /api/v1/auth/2fa/totp/verify/` | ✅ Yes | Verify 2FA code |
| **Account Unlock** | `POST /api/v1/auth/account-unlock/` | No | Request account unlock if locked |
| **Session Management** | `GET /api/v1/auth/user-sessions/` | ✅ Yes | View active sessions |

---

## Detailed Endpoint Documentation

### 1. Email/Password Login

**Endpoint**: `POST /api/v1/auth/login/`

**Request**:
```json
{
  "email": "client@example.com",
  "password": "yourpassword123",
  "remember_me": false
}
```

**Success Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "client@example.com",
    "username": "client_user",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "uuid-string",
  "expires_in": 3600
}
```

**2FA Required** (202 Accepted):
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
- `429 Too Many Requests`: Too many login attempts

---

### 2. Magic Link Login (Passwordless)

#### Step 1: Request Magic Link

**Endpoint**: `POST /api/v1/auth/magic-link/request/`

**Request**:
```json
{
  "email": "client@example.com"
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
- Only one active magic link per user
- Previous links are revoked when a new one is requested
- Rate limited to prevent abuse

#### Step 2: Verify Magic Link

**Endpoint**: `POST /api/v1/auth/magic-link/verify/`

**Request**:
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
    "email": "client@example.com",
    "username": "client_user",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "uuid-string",
  "expires_in": 3600,
  "message": "Welcome back, client@example.com!"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token
- `403 Forbidden`: Account disabled

---

### 3. Change Password (Authenticated)

**Endpoint**: `POST /api/v1/auth/change-password/`

**Authentication**: Required (JWT Bearer Token)

**Request**:
```json
{
  "current_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Success Response** (200 OK):
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
- ✅ Current password verification required
- ✅ Password strength validation
- ✅ Session maintained after password change (no logout)
- ✅ Audit log entry created
- ✅ Security notification sent

---

### 4. Password Reset (Forgot Password)

#### Step 1: Request Password Reset

**Endpoint**: `POST /api/v1/auth/password-reset/`

**Request**:
```json
{
  "email": "client@example.com"
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

#### Step 2: Confirm Password Reset

**Endpoint**: `POST /api/v1/auth/password-reset/confirm/`

**Request**:
```json
{
  "token": "reset-token-from-email",
  "password": "newpassword123"
}
```

**Success Response** (200 OK):
```json
{
  "detail": "Password reset successful."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid or expired token, weak password

---

### 5. Refresh Access Token

**Endpoint**: `POST /api/v1/auth/refresh-token/`

**Request**:
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

### 6. Logout

**Endpoint**: `POST /api/v1/auth/logout/`

**Authentication**: Required (JWT Bearer Token)

**Query Parameters**:
- `logout_all` (optional): If `true`, logout from all devices

**Request**:
```http
POST /api/v1/auth/logout/?logout_all=false
Authorization: Bearer <access_token>
```

**Response** (200 OK):
```json
{
  "detail": "Logged out successfully."
}
```

---

## User Flows

### Flow 1: First-Time Login

1. User registers (if registration is enabled)
2. User receives verification email
3. User clicks verification link
4. User logs in with email/password or magic link
5. If 2FA is enabled, user enters 2FA code
6. User receives JWT tokens and is logged in

### Flow 2: Regular Login

1. User goes to login page
2. User enters email and password OR requests magic link
3. If magic link: User clicks link in email
4. If 2FA is enabled, user enters 2FA code
5. User receives JWT tokens and is logged in

### Flow 3: Password Change

1. User is logged in
2. User goes to account settings
3. User enters current password, new password, and confirmation
4. System validates password strength
5. Password is changed
6. User receives security notification
7. Session remains active (no logout)

### Flow 4: Forgot Password

1. User clicks "Forgot Password" link
2. User enters email address
3. User receives password reset email
4. User clicks reset link in email
5. User enters new password
6. Password is reset
7. User can now login with new password

### Flow 5: Magic Link Login

1. User clicks "Login with Magic Link"
2. User enters email address
3. User receives magic link email
4. User clicks magic link
5. User is automatically logged in
6. User receives JWT tokens

---

## Security Best Practices

### For Users

1. **Use Strong Passwords**: Minimum 8 characters with mix of letters, numbers, and special characters
2. **Enable 2FA**: Add an extra layer of security
3. **Don't Share Credentials**: Never share your password or magic links
4. **Logout from Shared Devices**: Always logout when using shared computers
5. **Monitor Active Sessions**: Regularly check active sessions and logout suspicious ones
6. **Change Password Regularly**: Update your password periodically
7. **Use Magic Links on Trusted Devices**: Magic links are convenient but ensure device security

### For Developers

1. **Always Use HTTPS**: Never send credentials over HTTP
2. **Store Tokens Securely**: Use secure storage (httpOnly cookies or secure local storage)
3. **Handle Token Expiration**: Implement token refresh logic
4. **Validate Input**: Always validate user input on both client and server
5. **Rate Limiting**: Respect rate limits to prevent abuse
6. **Error Handling**: Don't expose sensitive information in error messages
7. **Session Management**: Implement proper session management and cleanup

---

## Frontend Integration Examples

### React/Next.js Example

```typescript
// Login with email/password
const login = async (email: string, password: string) => {
  const response = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, remember_me: false })
  });
  
  if (response.ok) {
    const data = await response.json();
    // Store tokens securely
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  }
  throw new Error('Login failed');
};

// Request magic link
const requestMagicLink = async (email: string) => {
  const response = await fetch('/api/v1/auth/magic-link/request/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  
  return response.json();
};

// Change password
const changePassword = async (
  currentPassword: string,
  newPassword: string,
  confirmPassword: string
) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('/api/v1/auth/change-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
  });
  
  return response.json();
};

// Refresh token
const refreshToken = async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  const response = await fetch('/api/v1/auth/refresh-token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refreshToken })
  });
  
  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return data;
  }
  throw new Error('Token refresh failed');
};
```

---

## Error Handling

### Common Error Codes

| Code | Status | Description | Solution |
|------|--------|-------------|----------|
| `authentication_failed` | 400 | Invalid credentials | Check email/password |
| `account_locked` | 403 | Account is locked | Request account unlock |
| `account_disabled` | 403 | Account is disabled | Contact support |
| `token_expired` | 400 | Token expired | Refresh token or re-login |
| `token_invalid` | 400 | Invalid token | Request new token |
| `rate_limit_exceeded` | 429 | Too many requests | Wait before retrying |
| `password_validation_failed` | 400 | Weak password | Use stronger password |
| `2fa_required` | 202 | 2FA verification needed | Enter 2FA code |

### Error Response Format

```json
{
  "error": "Error message",
  "code": "error_code",
  "details": {
    "field": "Specific field error"
  }
}
```

---

## Rate Limiting

All authentication endpoints are rate-limited to prevent abuse:

- **Login**: 5 attempts per 15 minutes per IP
- **Magic Link Request**: 3 requests per hour per email
- **Password Reset**: 3 requests per hour per email
- **Password Change**: 5 attempts per hour per user

Rate limit information is included in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time when limit resets

---

## Multi-Tenancy

All authentication endpoints automatically handle multi-tenancy:
- Users are scoped to their website
- Magic links are website-specific
- Password resets are website-specific
- Sessions are website-specific

---

## Support & Troubleshooting

### Common Issues

1. **"Invalid credentials"**: Check email and password, ensure account is active
2. **"Account locked"**: Too many failed login attempts, request unlock
3. **"Magic link expired"**: Request a new magic link (expires in 15 minutes)
4. **"Token expired"**: Refresh token or login again
5. **"Rate limit exceeded"**: Wait before retrying

### Getting Help

- Check this documentation first
- Review error messages carefully
- Contact support if issues persist
- Check system status page for outages

---

## Summary

The authentication system provides:
- ✅ Multiple login methods (email/password, magic link)
- ✅ Secure password management (change, reset)
- ✅ Token-based authentication (JWT)
- ✅ Two-factor authentication support
- ✅ Session management
- ✅ Rate limiting and security features
- ✅ User-friendly error messages
- ✅ Comprehensive audit logging

All endpoints are production-ready, secure, and user-friendly!

