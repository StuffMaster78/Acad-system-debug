# Account Management Refinement

## Overview

A comprehensive account management system has been created to streamline password reset, 2FA setup, profile updates, and account security. This provides a unified, user-friendly interface for all account-related operations.

## What Was Created

### 1. Account Service (`backend/users/services/account_service.py`)

A unified service class that handles all account management operations:

#### Password Management
- **`change_password()`**: Change password with current password verification
- **`request_password_reset()`**: Request password reset (sends email with token + OTP)
- **`complete_password_reset()`**: Complete password reset using token and OTP

#### 2FA/MFA Management
- **`setup_2fa_totp()`**: Setup TOTP-based 2FA (generates secret, QR code, backup codes)
- **`verify_and_enable_2fa()`**: Verify TOTP code and enable 2FA
- **`disable_2fa()`**: Disable 2FA (requires password or backup code)
- **`get_2fa_status()`**: Get current 2FA status
- **`regenerate_backup_codes()`**: Regenerate backup codes (invalidates old ones)

#### Profile Update Requests
- **`request_profile_update()`**: Request profile update (auto-approves basic fields, requires admin approval for sensitive fields)
- **`get_profile_update_requests()`**: Get all profile update requests for the user

#### Account Deletion
- **`request_account_deletion()`**: Request account deletion
- **`get_deletion_status()`**: Get account deletion request status

#### Security Settings
- **`get_security_settings()`**: Get comprehensive security settings summary

### 2. API Endpoints (`backend/users/views/account_management.py`)

Unified REST API endpoints under `/api/v1/users/account/`:

#### Password Management
- `POST /api/v1/users/account/change-password/` - Change password
- `POST /api/v1/users/account/request-password-reset/` - Request password reset (public)
- `POST /api/v1/users/account/complete-password-reset/` - Complete password reset (public)

#### 2FA/MFA Management
- `GET /api/v1/users/account/2fa/status/` - Get 2FA status
- `POST /api/v1/users/account/2fa/setup/` - Setup 2FA (returns QR code and backup codes)
- `POST /api/v1/users/account/2fa/verify-and-enable/` - Verify and enable 2FA
- `POST /api/v1/users/account/2fa/disable/` - Disable 2FA
- `POST /api/v1/users/account/2fa/regenerate-backup-codes/` - Regenerate backup codes

#### Profile Updates
- `POST /api/v1/users/account/request-profile-update/` - Request profile update
- `GET /api/v1/users/account/profile-update-requests/` - Get profile update requests

#### Account Deletion
- `POST /api/v1/users/account/request-deletion/` - Request account deletion
- `GET /api/v1/users/account/deletion-status/` - Get deletion status

#### Security Settings
- `GET /api/v1/users/account/security-settings/` - Get security settings summary

### 3. Serializers (`backend/users/serializers/account_serializers.py`)

- `ChangePasswordSerializer`: For password changes
- `CompletePasswordResetSerializer`: For password reset completion (token + OTP + new password)
- `ProfileUpdateRequestSerializer`: For profile update requests
- `AccountDeletionRequestSerializer`: For account deletion requests

## Key Features

### Streamlined Password Reset

**Before**: Multiple endpoints, inconsistent flow
**After**: 
- Single unified endpoint
- Token + OTP dual verification for security
- Clear error messages
- Email notifications

**Flow**:
1. User requests reset → receives email with token and OTP
2. User enters token + OTP + new password
3. Password is reset securely

### Complete 2FA Setup

**Features**:
- QR code generation for authenticator apps
- Backup codes generation (10 codes)
- Enable/disable with password verification
- Backup code regeneration
- Status checking

**Flow**:
1. User initiates setup → receives QR code and backup codes
2. User scans QR code in authenticator app
3. User verifies with 6-digit code
4. 2FA is enabled

### Profile Update Workflow

**Auto-Approved Fields** (immediate update):
- `username`, `first_name`, `last_name`
- `phone_number`, `bio`, `country`, `state`

**Admin Approval Required** (creates update request):
- `email`, `role`, `website`

**Flow**:
1. User submits update request
2. Basic fields updated immediately
3. Sensitive fields create approval request
4. Admin reviews and approves/rejects
5. User notified of result

### Account Deletion

- Request-based deletion (not immediate)
- Grace period before final deletion
- Admin notification
- Status tracking

## Usage Examples

### Change Password

```python
POST /api/v1/users/account/change-password/
{
    "current_password": "oldpass123",
    "new_password": "newpass123"
}
```

### Setup 2FA

```python
# Step 1: Get QR code and backup codes
POST /api/v1/users/account/2fa/setup/
Response: {
    "secret": "...",
    "qr_code": "data:image/png;base64,...",
    "backup_codes": ["code1", "code2", ...],
    "message": "2FA setup initiated..."
}

# Step 2: Verify and enable
POST /api/v1/users/account/2fa/verify-and-enable/
{
    "totp_code": "123456"
}
```

### Request Profile Update

```python
POST /api/v1/users/account/request-profile-update/
{
    "phone_number": "+1234567890",
    "bio": "Updated bio",
    "email": "newemail@example.com"  # Requires admin approval
}
Response: {
    "message": "Profile updated. Some changes require admin approval.",
    "auto_approved": {"phone_number": "...", "bio": "..."},
    "pending_approval": {"email": "..."}
}
```

## Security Features

1. **Password Reset**: Dual verification (token + OTP)
2. **2FA**: TOTP with backup codes
3. **Profile Updates**: Admin approval for sensitive fields
4. **Account Deletion**: Request-based with grace period
5. **Password Verification**: Required for sensitive operations (disable 2FA, regenerate backup codes)

## Next Steps

### Frontend Integration

The following frontend components should be created/updated:

1. **Password Reset Flow**
   - Forgot password page
   - Reset password page (with token + OTP input)
   - Change password form in settings

2. **2FA Management**
   - 2FA setup wizard (QR code display, verification)
   - 2FA status display
   - Backup codes display/download
   - Disable 2FA confirmation

3. **Profile Updates**
   - Profile update form
   - Update request status display
   - Admin approval interface

4. **Account Settings**
   - Unified account settings page
   - Security settings summary
   - Account deletion request form

### API Client Updates

Update frontend API client (`frontend/src/api/`) to include:
- `accountAPI.changePassword()`
- `accountAPI.requestPasswordReset()`
- `accountAPI.completePasswordReset()`
- `accountAPI.setup2FA()`
- `accountAPI.enable2FA()`
- `accountAPI.disable2FA()`
- `accountAPI.get2FAStatus()`
- `accountAPI.requestProfileUpdate()`
- `accountAPI.getProfileUpdateRequests()`
- `accountAPI.requestAccountDeletion()`
- `accountAPI.getSecuritySettings()`

## Benefits

1. **Unified Interface**: All account operations in one place
2. **Better Security**: Enhanced password reset, complete 2FA support
3. **User-Friendly**: Clear workflows, helpful error messages
4. **Admin Control**: Approval workflow for sensitive changes
5. **Maintainable**: Centralized service layer, consistent API

## Testing

Run Django system check:
```bash
docker-compose run --rm web python manage.py check
```

All endpoints are ready for integration testing and frontend development.

