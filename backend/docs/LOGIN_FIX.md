# Login Error Fix - Website ID Constraint

## Problem
When logging in (especially via admin panel), the system was trying to create audit logs and activity logs, but these models required a `website_id` which wasn't available during login.

## Solution Applied

### 1. Made Website Fields Nullable
- **UserAuditLog.website**: Changed from `CASCADE` (required) to `SET_NULL` (nullable)
- **ActivityLog.website**: Changed from `CASCADE` (required) to `SET_NULL` (nullable)

### 2. Enhanced Website Detection
- Updated `log_user_login` signal to try getting website from:
  1. User's website attribute
  2. Request host header
  3. First active website in database
  4. Allow None if none found

### 3. Updated Middleware
- `ActivityAuditMiddleware` now tries to get website from user if not in request
- `safe_log_activity` helper automatically tries to get website from user

### 4. Removed Constraint
- Removed unique constraint on `ActivityLog` that included website (since it can be null now)

## Files Modified
- `users/models.py` - Made UserAuditLog.website nullable
- `activity/models.py` - Made ActivityLog.website nullable, removed unique constraint
- `users/signals.py` - Enhanced website detection in login signal
- `activity/middleware.py` - Enhanced website detection in middleware
- `activity/utils/logger_safe.py` - Auto-detect website from user

## Migration Status
✅ Migrations created
✅ Migrations applied
✅ System restarted

## Testing
You should now be able to:
1. Login via admin panel: `http://localhost:8000/admin/`
2. Login via API: `POST /api/v1/auth/login/`
3. System will log activities even if website is not available

The system will gracefully handle cases where website context is missing during login or system events.

