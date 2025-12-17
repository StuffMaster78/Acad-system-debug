# Impersonation System Implementation

## Overview

The impersonation system allows administrators and superadmins to temporarily access user accounts for support, debugging, and customer service purposes. This document explains the implementation details, design choices, and patterns used.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Design Patterns](#design-patterns)
3. [Security Model](#security-model)
4. [Token-Based Approach](#token-based-approach)
5. [Database Schema](#database-schema)
6. [API Endpoints](#api-endpoints)
7. [Frontend Integration](#frontend-integration)
8. [Rate Limiting](#rate-limiting)
9. [Error Handling](#error-handling)
10. [Design Choices & Rationale](#design-choices--rationale)

---

## Architecture Overview

### High-Level Flow

```
Admin → Generate Token → Start Impersonation → Access as Target User → End Impersonation → Return to Admin
```

### Components

1. **Backend Service Layer** (`ImpersonationService`)
   - Centralized business logic
   - Permission validation
   - Token generation and validation

2. **Model Layer** (`ImpersonationToken`, `ImpersonationLog`)
   - Token storage and expiration
   - Audit logging

3. **API Layer** (`ImpersonationTokenViewSet`)
   - RESTful endpoints
   - Rate limiting
   - Request validation

4. **Frontend Integration**
   - Token generation
   - New tab impersonation
   - Role-based dashboard redirection

---

## Design Patterns

### 1. Service Pattern

**Location**: `backend/authentication/services/impersonation_service.py`

The `ImpersonationService` class encapsulates all impersonation business logic:

```python
class ImpersonationService:
    @staticmethod
    def can_impersonate(admin_user, target_user):
        """Check if admin can impersonate target user"""
        
    @staticmethod
    def generate_token(admin_user, target_user, website, expires_hours=1):
        """Generate impersonation token"""
        
    @staticmethod
    def start_impersonation(token, admin_token):
        """Start impersonation session"""
        
    @staticmethod
    def end_impersonation(impersonation_token):
        """End impersonation and restore admin session"""
```

**Benefits**:
- Separation of concerns
- Reusable business logic
- Easier testing
- Centralized permission checks

### 2. Token-Based Authentication Pattern

Instead of directly switching user sessions, we use temporary tokens:

**Why Token-Based?**
- **Security**: Tokens expire automatically
- **Auditability**: Each impersonation has a unique token
- **Flexibility**: Can be used across tabs/sessions
- **Revocability**: Tokens can be invalidated

**Token Structure**:
```python
ImpersonationToken:
    - token: Unique identifier (UUID)
    - admin_user: Who initiated impersonation
    - target_user: Who is being impersonated
    - website: Tenant context
    - expires_at: Automatic expiration
```

### 3. Repository Pattern (via Django ORM)

Django's ORM acts as a repository layer:

```python
# Model methods encapsulate data access
@classmethod
def generate_token(cls, admin_user, target_user, website, expires_hours=1):
    return cls.objects.create(...)
```

### 4. Strategy Pattern for Permission Checks

Different permission rules for different scenarios:

```python
def can_impersonate(admin_user, target_user):
    # Strategy 1: Role-based checks
    if target_user.role in ['superadmin']:
        return False, "Cannot impersonate superadmins"
    
    # Strategy 2: Self-impersonation prevention
    if admin_user.id == target_user.id:
        return False, "Cannot impersonate yourself"
    
    # Strategy 3: Website/tenant isolation
    # ... tenant checks
    
    return True, None
```

### 5. Factory Pattern for Token Generation

```python
@classmethod
def generate_token(cls, admin_user, target_user, website, expires_hours=1):
    """Factory method for creating tokens"""
    token = cls(
        token=str(uuid.uuid4()),
        admin_user=admin_user,
        target_user=target_user,
        website=website,
        expires_at=timezone.now() + timedelta(hours=expires_hours)
    )
    token.save()
    return token
```

---

## Security Model

### Multi-Layer Security

1. **Authentication Layer**
   - JWT tokens required
   - Admin/superadmin role verification

2. **Authorization Layer**
   - Permission checks before token generation
   - Role-based access control (RBAC)

3. **Token Security**
   - Unique UUID tokens
   - Time-based expiration (default: 1 hour)
   - Single-use tokens (optional)

4. **Audit Trail**
   - All impersonation actions logged
   - Admin and target user tracked
   - Timestamps for start/end

5. **Rate Limiting**
   - Prevents abuse
   - Configurable limits (200/hour for admins)

### Permission Matrix

| Admin Role | Can Impersonate | Cannot Impersonate |
|------------|----------------|-------------------|
| Admin | Clients, Writers, Editors, Support | Superadmins, Other Admins |
| Superadmin | All roles | None (except self) |

### Security Features

1. **Self-Impersonation Prevention**
   ```python
   if admin_user.id == target_user.id:
       return False, "Cannot impersonate yourself"
   ```

2. **Superadmin Protection**
   ```python
   if target_user.role == 'superadmin':
       return False, "Cannot impersonate superadmins"
   ```

3. **Website/Tenant Isolation**
   - Impersonation respects tenant boundaries
   - Cross-tenant impersonation blocked

4. **Token Expiration**
   - Automatic cleanup of expired tokens
   - Prevents indefinite access

---

## Token-Based Approach

### Why Tokens Instead of Direct Session Switching?

#### Traditional Approach (Session Switching)
```python
# Direct session switch - NOT USED
request.session['user_id'] = target_user.id
```

**Problems**:
- No audit trail
- Hard to track who's impersonating
- Difficult to revoke
- No expiration mechanism
- Security risk if session hijacked

#### Our Approach (Token-Based)
```python
# Generate token
token = ImpersonationService.generate_token(admin, target_user, website)

# Start impersonation with token
response = ImpersonationService.start_impersonation(token, admin_token)
# Returns new JWT tokens for target user
```

**Benefits**:
- ✅ Full audit trail
- ✅ Automatic expiration
- ✅ Revocable
- ✅ Trackable
- ✅ Secure (JWT-based)

### Token Lifecycle

```
1. Generation
   Admin → POST /auth/impersonate/create_token/
   → Returns: { token: "uuid", expires_at: "..." }

2. Activation
   Admin → POST /auth/impersonate/start/ { token: "uuid" }
   → Returns: { access_token: "...", user: {...}, impersonation: {...} }

3. Usage
   Frontend uses new access_token for all API calls
   → All requests include impersonation context in JWT

4. Termination
   Admin → POST /auth/impersonate/end/
   → Returns: { access_token: "...", user: {...} } (admin's tokens)
```

---

## Database Schema

### ImpersonationToken Model

```python
class ImpersonationToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    admin_user = models.ForeignKey(User, related_name='user_impersonation_tokens')
    target_user = models.ForeignKey(User, related_name='impersonated_by_tokens')
    website = models.ForeignKey(Website, related_name='impersonation_web_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
```

**Design Choices**:
- **UUID tokens**: Cryptographically secure, globally unique
- **Foreign keys**: Maintain referential integrity
- **Expiration**: Time-based cleanup
- **Website field**: Multi-tenant support

### ImpersonationLog Model

```python
class ImpersonationLog(models.Model):
    admin_user = models.ForeignKey(User, related_name='impersonation_logs_for_admin')
    target_user = models.ForeignKey(User, related_name='impersonation_logs_for_target_user')
    website = models.ForeignKey(Website, related_name='impersonation_logs')
    token = models.ForeignKey(ImpersonationToken, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Purpose**: Audit trail for compliance and security

**Design Choices**:
- **Separate from token**: Logs persist even after token expiration
- **Nullable token**: Supports logging even if token generation fails
- **Timestamps**: Track when impersonation occurred

---

## API Endpoints

### RESTful Design

All endpoints follow REST conventions:

```
POST   /api/v1/auth/impersonate/create_token/  # Create token
POST   /api/v1/auth/impersonate/start/         # Start impersonation
POST   /api/v1/auth/impersonate/end/           # End impersonation
GET    /api/v1/auth/impersonate/status/        # Check status
GET    /api/v1/auth/impersonate/expired/       # List expired tokens
```

### Endpoint Details

#### 1. Create Token
```http
POST /api/v1/auth/impersonate/create_token/
Authorization: Bearer <admin_token>
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

**Design Choice**: Separate token creation from activation allows:
- Token sharing (if needed)
- Pre-validation
- Better error handling

#### 2. Start Impersonation
```http
POST /api/v1/auth/impersonate/start/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "token": "abc123..."
}
```

**Response**:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": { /* target user data */ },
  "impersonation": {
    "impersonated_by": { /* admin data */ },
    "started_at": "..."
  }
}
```

**Design Choice**: Returns new JWT tokens instead of modifying session:
- Works across tabs/devices
- Stateless (RESTful)
- Can be revoked server-side

#### 3. End Impersonation
```http
POST /api/v1/auth/impersonate/end/
Authorization: Bearer <impersonation_token>
```

**Response**:
```json
{
  "access_token": "...",  // Admin's token
  "refresh_token": "...",
  "user": { /* admin user data */ },
  "message": "Impersonation ended"
}
```

**Design Choice**: Requires impersonation token (not admin token):
- Prevents unauthorized termination
- Ensures proper session cleanup

---

## Frontend Integration

### Architecture

```
UserManagement.vue (Admin Panel)
    ↓
generateImpersonationToken(userId)
    ↓
POST /auth/impersonate/create_token/
    ↓
Open new tab: /impersonate?token=...
    ↓
Impersonate.vue
    ↓
startImpersonation(token)
    ↓
POST /auth/impersonate/start/
    ↓
Update auth store
    ↓
Redirect to role-specific dashboard
```

### Design Choices

#### 1. New Tab Approach

**Why?**
- Admin can continue working in original tab
- Clear separation between admin and impersonated sessions
- Better UX for support scenarios

**Implementation**:
```javascript
const impersonateUser = async (user) => {
  const token = await usersAPI.generateImpersonationToken(user.id)
  const impersonateUrl = `${baseUrl}/impersonate?token=${token}`
  window.open(impersonateUrl, '_blank', 'noopener,noreferrer')
}
```

#### 2. Role-Based Dashboard Redirection

**Why?**
- Different roles have different dashboards
- Better UX - user lands where they expect
- Consistent with normal login flow

**Implementation**:
```javascript
const userRole = user?.role
let dashboardRoute = '/dashboard' // Default

if (userRole === 'client') {
  dashboardRoute = '/client'
} else if (userRole === 'admin') {
  dashboardRoute = '/admin/dashboard'
} else if (userRole === 'superadmin') {
  dashboardRoute = '/superadmin/dashboard'
}

window.location.href = dashboardRoute
```

#### 3. Auth Store Integration

**Why?**
- Centralized authentication state
- Consistent with rest of app
- Easy to check impersonation status

**Implementation**:
```javascript
// Auth store state
state: () => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isImpersonating: false,
  impersonator: null
})

// After impersonation starts
authStore.isImpersonating = true
authStore.impersonator = impersonation?.impersonated_by
```

---

## Rate Limiting

### Implementation

```python
class ImpersonationTokenThrottle(UserRateThrottle):
    rate = "200/hour"  # Increased from 5/hour for development
    scope = "impersonation_token"
```

### Design Choices

#### 1. User-Based Throttling

**Why not IP-based?**
- Admins may work from different IPs
- More accurate per-user limits
- Prevents shared IP issues

#### 2. Configurable Rate

**Current**: 200/hour
- High enough for development/testing
- Low enough to prevent abuse
- Can be adjusted per environment

#### 3. Scope-Based Cache Keys

**Format**: `throttle_impersonation_token_{user_id}`

**Benefits**:
- Easy to identify in Redis
- Per-user tracking
- Can be cleared individually

### Clearing Rate Limits

**Management Command**:
```bash
python manage.py clear_rate_limit --type impersonation --user-id 123
```

**Why needed?**
- Development/testing scenarios
- Legitimate admin operations
- Emergency access

---

## Error Handling

### Error Types

1. **Permission Errors** (403)
   - Cannot impersonate superadmin
   - Cannot impersonate yourself
   - Insufficient permissions

2. **Validation Errors** (400)
   - Invalid token
   - Missing required fields
   - Invalid user ID

3. **Not Found Errors** (404)
   - Token doesn't exist
   - User doesn't exist
   - Expired token

4. **Rate Limit Errors** (429)
   - Too many requests
   - Wait time provided

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "detail": "Technical details (optional)",
  "code": "ERROR_CODE (optional)"
}
```

### Frontend Error Handling

```javascript
try {
  const response = await usersAPI.generateImpersonationToken(userId)
  // Success handling
} catch (error) {
  if (error.response?.status === 429) {
    // Rate limit - show wait time
    message.value = `Too many requests. Please wait ${waitTime} seconds.`
  } else if (error.response?.status === 403) {
    // Permission denied
    message.value = error.response.data.error || 'Access denied'
  } else {
    // Generic error
    message.value = 'Failed to impersonate user'
  }
}
```

---

## Design Choices & Rationale

### 1. Why Token-Based Instead of Session-Based?

**Session-Based** (Rejected):
- ❌ No audit trail
- ❌ Hard to revoke
- ❌ No expiration
- ❌ Security risk

**Token-Based** (Chosen):
- ✅ Full audit trail
- ✅ Automatic expiration
- ✅ Revocable
- ✅ Secure (JWT)

### 2. Why Separate Token Creation and Activation?

**Single-Step** (Rejected):
- ❌ Less flexible
- ❌ Harder to validate upfront
- ❌ Can't share tokens

**Two-Step** (Chosen):
- ✅ Pre-validation possible
- ✅ Better error handling
- ✅ Token can be shared (if needed)
- ✅ Clear separation of concerns

### 3. Why New Tab Instead of Same Tab?

**Same Tab** (Rejected):
- ❌ Admin loses their session
- ❌ Confusing UX
- ❌ Hard to switch back

**New Tab** (Chosen):
- ✅ Admin keeps working
- ✅ Clear separation
- ✅ Better for support scenarios
- ✅ Easy to close and return

### 4. Why JWT Tokens Instead of Session Tokens?

**Session Tokens** (Rejected):
- ❌ Server-side state required
- ❌ Harder to scale
- ❌ Cross-domain issues

**JWT Tokens** (Chosen):
- ✅ Stateless
- ✅ Scalable
- ✅ Works across domains
- ✅ Can include impersonation claims

### 5. Why Rate Limiting?

**No Rate Limiting** (Rejected):
- ❌ Vulnerable to abuse
- ❌ No protection against attacks
- ❌ Can overwhelm system

**Rate Limiting** (Chosen):
- ✅ Prevents abuse
- ✅ Protects system resources
- ✅ Configurable per environment
- ✅ Clear error messages

### 6. Why Separate ImpersonationLog?

**Logging in Token Model** (Rejected):
- ❌ Tokens expire and get deleted
- ❌ Lose audit trail
- ❌ Hard to query historical data

**Separate Log Model** (Chosen):
- ✅ Persistent audit trail
- ✅ Survives token expiration
- ✅ Easy to query and report
- ✅ Compliance-friendly

### 7. Why Website/Tenant Field?

**No Tenant Isolation** (Rejected):
- ❌ Security risk
- ❌ Data leakage possible
- ❌ Multi-tenant issues

**Tenant Isolation** (Chosen):
- ✅ Respects tenant boundaries
- ✅ Prevents cross-tenant access
- ✅ Better security
- ✅ Multi-tenant support

---

## Security Considerations

### 1. Token Security

- **UUID Generation**: Cryptographically secure
- **Expiration**: Automatic cleanup
- **Single Use**: Tokens can be marked as used
- **Revocation**: Tokens can be invalidated

### 2. Permission Checks

- **Multi-layer**: Service layer + API layer
- **Role-based**: Different rules for different roles
- **Tenant-aware**: Respects multi-tenant boundaries

### 3. Audit Trail

- **Comprehensive logging**: All actions logged
- **User tracking**: Admin and target tracked
- **Timestamped**: Full timeline available

### 4. Rate Limiting

- **Prevents abuse**: Configurable limits
- **User-based**: More accurate than IP-based
- **Clear errors**: Helpful error messages

---

## Future Enhancements

### Potential Improvements

1. **Token Revocation**
   - Admin can revoke active tokens
   - Emergency termination
   - Security incident response

2. **Time-Based Restrictions**
   - Only allow impersonation during business hours
   - Configurable time windows

3. **Notification System**
   - Notify target user when impersonated
   - Email/SMS alerts
   - Optional opt-out

4. **Impersonation Reasons**
   - Require reason for impersonation
   - Track why impersonation occurred
   - Better audit trail

5. **Session Recording**
   - Record impersonation sessions
   - Playback for training
   - Compliance support

6. **Approval Workflow**
   - Require approval for sensitive impersonations
   - Multi-admin approval
   - Escalation paths

---

## Testing Considerations

### Unit Tests

- Service layer logic
- Permission checks
- Token generation/validation
- Error handling

### Integration Tests

- API endpoints
- Database operations
- Token lifecycle
- Rate limiting

### Security Tests

- Permission bypass attempts
- Token manipulation
- Rate limit bypass
- Cross-tenant access

---

## Conclusion

The impersonation system uses modern design patterns and security best practices to provide a secure, auditable, and user-friendly way for administrators to access user accounts. The token-based approach, combined with comprehensive logging and rate limiting, ensures both functionality and security.

Key strengths:
- ✅ Secure token-based authentication
- ✅ Comprehensive audit trail
- ✅ Multi-tenant support
- ✅ Rate limiting protection
- ✅ User-friendly frontend integration
- ✅ Role-based access control

This implementation provides a solid foundation for admin support operations while maintaining security and compliance requirements.

