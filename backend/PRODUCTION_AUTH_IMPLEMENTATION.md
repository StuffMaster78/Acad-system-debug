# Production-Grade Authentication Implementation

## Overview

This document describes the production-grade authentication, logout, and impersonation system that is robust, resilient, secure, and scalable.

## Architecture

### Unified Authentication Service

**File**: `authentication/services/auth_service.py`

A centralized `AuthenticationService` that handles:
- User login with validation
- 2FA verification
- Token refresh
- Logout with session cleanup
- Account lockout checks
- Multi-tenant support

**Key Features**:
- ✅ Account lockout protection
- ✅ Failed login attempt tracking
- ✅ 2FA support
- ✅ Remember me functionality
- ✅ Device tracking
- ✅ Session management
- ✅ JWT token generation

### Token-Based Impersonation

**File**: `authentication/services/impersonation_service.py`

Production-grade impersonation system with:
- ✅ Permission checks (superadmin vs admin)
- ✅ Token-based security
- ✅ JWT token support for stateless auth
- ✅ Comprehensive audit logging
- ✅ Session and token management
- ✅ Security validations

**Permission Rules**:
- **Superadmins**: Can impersonate anyone (except themselves)
- **Admins**: Can only impersonate clients and writers (not other admins/superadmins)

## API Endpoints

### Authentication Endpoints

**Base URL**: `/api/v1/auth/auth/`

#### Login
```http
POST /api/v1/auth/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

**Response** (200 OK):
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "full_name": "John Doe",
    "role": "client"
  },
  "session_id": "...",
  "expires_in": 3600
}
```

**Response** (202 Accepted - 2FA Required):
```json
{
  "requires_2fa": true,
  "session_id": "...",
  "message": "2FA verification required."
}
```

#### Verify 2FA
```http
POST /api/v1/auth/auth/verify-2fa/
Content-Type: application/json

{
  "user_id": 1,
  "session_id": "...",
  "totp_code": "123456"
}
```

#### Logout
```http
POST /api/v1/auth/auth/logout/
Authorization: Bearer <access_token>

# Optional query param: ?logout_all=true
```

#### Refresh Token
```http
POST /api/v1/auth/auth/refresh-token/
Content-Type: application/json

{
  "refresh_token": "..."
}
```

### Impersonation Endpoints

**Base URL**: `/api/v1/auth/impersonate/`

#### Create Token
```http
POST /api/v1/auth/impersonate/create_token/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "target_user": 123
}
```

**Response**:
```json
{
  "token": "abc123...",
  "expires_at": "2024-01-01T12:00:00Z"
}
```

#### Start Impersonation
```http
POST /api/v1/auth/impersonate/start/
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "token": "abc123..."
}
```

**Response**:
```json
{
  "access_token": "...",  // New token for target user
  "refresh_token": "...",
  "user": {
    "id": 123,
    "email": "client@example.com",
    ...
  },
  "impersonation": {
    "impersonated_by": {
      "id": 1,
      "email": "admin@example.com",
      "full_name": "Admin User"
    },
    "started_at": "2024-01-01T10:00:00Z"
  }
}
```

#### End Impersonation
```http
POST /api/v1/auth/impersonate/end/
Authorization: Bearer <impersonation_access_token>
```

**Response**:
```json
{
  "access_token": "...",  // New token for admin
  "refresh_token": "...",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    ...
  },
  "message": "Impersonation ended. You are now logged in as yourself."
}
```

#### Check Impersonation Status
```http
GET /api/v1/auth/impersonate/status/
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "is_impersonating": true,
  "impersonator": {
    "id": 1,
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "admin"
  }
}
```

## Security Features

### 1. Rate Limiting

- **Login**: 5 attempts per minute (per IP)
- **Impersonation**: 5 token creations per hour (per admin)
- **Token Refresh**: Configurable via DRF throttling

### 2. Account Lockout

- Automatic lockout after failed attempts
- Lockout duration based on attempt count
- Clear error messages with lockout expiration

### 3. Token Security

- JWT tokens with expiration
- Refresh token rotation
- Token blacklisting support
- Impersonation claims in JWT

### 4. Audit Logging

- All impersonation actions logged
- Login/logout events tracked
- Failed login attempts recorded
- Session management logged

### 5. Permission Validation

- Multi-level permission checks
- Role-based access control
- Tenant/website isolation
- Admin vs superadmin distinction

## Implementation Details

### JWT Token Claims

**Normal User Token**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "role": "client",
  "exp": 1234567890
}
```

**Impersonation Token**:
```json
{
  "user_id": 123,  // Target user ID
  "email": "client@example.com",
  "role": "client",
  "is_impersonation": true,
  "impersonated_by": 1,  // Admin user ID
  "exp": 1234567890
}
```

### Session Management

- Sessions stored in database (`LoginSession` model)
- Device tracking (IP, user agent, device name)
- Multi-device support
- Session revocation (single or all)
- Automatic cleanup of expired sessions

### Error Handling

All authentication endpoints return consistent error formats:

```json
{
  "error": "Error message here"
}
```

Common error codes:
- `400`: Bad request (validation errors)
- `401`: Unauthorized (invalid credentials)
- `403`: Forbidden (permission denied)
- `429`: Too many requests (rate limited)
- `500`: Internal server error

## Migration Guide

### From Old Login Endpoints

**Old**:
```http
POST /api/v1/auth/login/
```

**New**:
```http
POST /api/v1/auth/auth/login/
```

### From Old Impersonation

**Old** (deprecated):
```http
POST /api/v1/users/users/{id}/impersonate/
```

**New** (token-based):
```http
# Step 1: Create token
POST /api/v1/auth/impersonate/create_token/
# Step 2: Use token
POST /api/v1/auth/impersonate/start/
```

## Testing

### Test Login Flow
```bash
# 1. Login
curl -X POST http://localhost:8000/api/v1/auth/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'

# 2. Use access token
curl http://localhost:8000/api/v1/users/users/me/ \
  -H "Authorization: Bearer <access_token>"
```

### Test Impersonation Flow
```bash
# 1. Admin creates token
curl -X POST http://localhost:8000/api/v1/auth/impersonate/create_token/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"target_user": 123}'

# 2. Start impersonation (returns new tokens)
curl -X POST http://localhost:8000/api/v1/auth/impersonate/start/ \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "<token_from_step_1>"}'

# 3. Use impersonation token (now acting as target user)

# 4. End impersonation
curl -X POST http://localhost:8000/api/v1/auth/impersonate/end/ \
  -H "Authorization: Bearer <impersonation_token>"
```

## Production Considerations

### 1. Environment Variables

```bash
# JWT Settings
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=3600  # 1 hour
JWT_REFRESH_TOKEN_LIFETIME=604800  # 7 days

# Session Settings
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### 2. Rate Limiting

Adjust based on your needs:
- Increase for internal tools
- Decrease for public APIs
- Use Redis for distributed rate limiting

### 3. Monitoring

Track:
- Failed login attempts
- Impersonation usage
- Token refresh rates
- Session duration
- Lockout events

### 4. Cleanup Tasks

Schedule Celery tasks for:
- Expired token cleanup
- Inactive session cleanup
- Failed login attempt cleanup
- Impersonation log archival

## Security Best Practices

1. **Always use HTTPS** in production
2. **Implement token rotation** for long-lived sessions
3. **Monitor for suspicious activity** (multiple IPs, rapid impersonation)
4. **Regular security audits** of impersonation logs
5. **Limit impersonation duration** (tokens expire in 1 hour)
6. **Require 2FA** for admin accounts
7. **Log all security events** for forensics

## Troubleshooting

### Login Fails
1. Check account lockout status
2. Verify credentials
3. Check for 2FA requirement
4. Review failed login logs

### Impersonation Fails
1. Verify admin permissions
2. Check token expiration
3. Validate target user role
4. Review impersonation logs

### Token Issues
1. Check token expiration
2. Verify token signature
3. Check token blacklist
4. Validate refresh token

## Future Enhancements

- [ ] Device fingerprinting
- [ ] Biometric authentication
- [ ] OAuth/SSO integration
- [ ] Advanced session analytics
- [ ] Automated threat detection
- [ ] Passwordless authentication

