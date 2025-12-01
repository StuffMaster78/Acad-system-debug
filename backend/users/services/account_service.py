"""
Comprehensive Account Management Service

Handles all account-related operations including:
- Password management (reset, change)
- 2FA/MFA setup and management
- Profile update requests
- Account security settings
- Email verification
"""
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import pyotp
import qrcode
import io
import base64
import secrets
import hashlib

from authentication.models.mfa_settings import MFASettings
from authentication.models.backup_code import BackupCode
from authentication.models.password_reset import PasswordResetRequest
from users.models import ProfileUpdateRequest

# AccountDeletionRequest is in authentication.models.deletion_requests
from authentication.models.deletion_requests import AccountDeletionRequest
from authentication.services.password_reset_service import PasswordResetService
from authentication.services.mfa import MFAService

User = get_user_model()


class AccountService:
    """
    Unified service for account management operations.
    """
    
    def __init__(self, user):
        """
        Args:
            user: User instance
        """
        self.user = user
        self.mfa_service = MFAService(user)
    
    # ==================== Password Management ====================
    
    @transaction.atomic
    def change_password(self, current_password: str, new_password: str) -> dict:
        """
        Change user's password after verifying current password.
        
        Args:
            current_password: Current password
            new_password: New password
            
        Returns:
            dict: Success message
            
        Raises:
            ValidationError: If current password is incorrect
        """
        if not self.user.check_password(current_password):
            raise ValidationError("Current password is incorrect.")
        
        self.user.set_password(new_password)
        self.user.save()
        
        return {"message": "Password changed successfully."}
    
    @transaction.atomic
    def request_password_reset(self, website=None) -> dict:
        """
        Request password reset (sends email with token and OTP).
        
        Args:
            website: Website instance (for multitenancy)
            
        Returns:
            dict: Success message (always returns success for security)
        """
        if not website:
            from websites.models import Website
            website = getattr(self.user, 'website', None) or Website.objects.first()
        
        if not website:
            raise ValidationError("Website is required for password reset.")
        
        service = PasswordResetService(self.user, website)
        reset_request = service.generate_reset_token()
        
        # Send email (handled by email service)
        from authentication.services.password_reset_email_service import PasswordResetEmailService
        email_service = PasswordResetEmailService(self.user, website, reset_request)
        email_service.send_reset_email()
        
        return {
            "message": "If that email exists, a password reset link was sent.",
            "token": reset_request.token,  # Only for development/testing
            "otp_code": reset_request.otp_code  # Only for development/testing
        }
    
    @transaction.atomic
    def complete_password_reset(self, token: str, otp_code: str, new_password: str) -> dict:
        """
        Complete password reset using token and OTP.
        
        Args:
            token: Reset token
            otp_code: OTP code
            new_password: New password
            
        Returns:
            dict: Success message
            
        Raises:
            ValidationError: If token/OTP is invalid
        """
        try:
            reset_request = PasswordResetRequest.objects.get(token=token)
        except PasswordResetRequest.DoesNotExist:
            raise ValidationError("Invalid reset token.")
        
        if reset_request.is_used:
            raise ValidationError("This reset link has already been used.")
        
        if reset_request.is_expired():
            raise ValidationError("Reset token has expired.")
        
        # Verify OTP
        if reset_request.otp_code != otp_code:
            raise ValidationError("Invalid OTP code.")
        
        # Set new password
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        
        # Mark token as used
        reset_request.is_used = True
        reset_request.save()
        
        return {"message": "Password reset successfully."}
    
    # ==================== 2FA/MFA Management ====================
    
    @transaction.atomic
    def setup_2fa_totp(self) -> dict:
        """
        Setup TOTP-based 2FA (generates secret and QR code).
        
        Returns:
            dict: Contains secret, QR code data URL, and backup codes
        """
        # Generate TOTP secret
        secret = self.mfa_service.generate_totp_secret()
        
        # Generate QR code
        qr_code_data = self._generate_totp_qr_code(secret)
        
        # Generate backup codes
        backup_codes = self.mfa_service.generate_backup_codes(count=10)
        
        return {
            "secret": secret,
            "qr_code": qr_code_data,
            "backup_codes": backup_codes,
            "message": "2FA setup initiated. Scan QR code and verify with a code."
        }
    
    def _generate_totp_qr_code(self, secret: str) -> str:
        """
        Generate QR code data URL for TOTP setup.
        
        Args:
            secret: TOTP secret key
            
        Returns:
            str: Base64-encoded QR code image data URL
        """
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=self.user.email,
            issuer_name="Writing System"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 data URL
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @transaction.atomic
    def verify_and_enable_2fa(self, totp_code: str) -> dict:
        """
        Verify TOTP code and enable 2FA.
        
        Args:
            totp_code: 6-digit TOTP code from authenticator app
            
        Returns:
            dict: Success message
            
        Raises:
            ValidationError: If code is invalid
        """
        # Verify the code
        self.mfa_service.validate_totp_code(totp_code)
        
        # Enable MFA
        self.mfa_service.enable_mfa('qr_code')
        
        return {"message": "2FA enabled successfully."}
    
    @transaction.atomic
    def disable_2fa(self, password: str, backup_code: str = None) -> dict:
        """
        Disable 2FA (requires password or backup code).
        
        Args:
            password: User's password
            backup_code: Optional backup code (if password forgotten)
            
        Returns:
            dict: Success message
            
        Raises:
            ValidationError: If password/code is invalid
        """
        # Verify password or backup code
        if backup_code:
            try:
                self.mfa_service.validate_backup_code(backup_code)
            except ValidationError:
                raise ValidationError("Invalid backup code.")
        else:
            if not self.user.check_password(password):
                raise ValidationError("Password is incorrect.")
        
        # Disable MFA
        self.mfa_service.disable_mfa()
        
        return {"message": "2FA disabled successfully."}
    
    def get_2fa_status(self) -> dict:
        """
        Get current 2FA status.
        
        Returns:
            dict: 2FA status information
        """
        mfa_settings, _ = MFASettings.get_or_create_for_user(self.user)
        
        return {
            "enabled": mfa_settings.is_mfa_enabled,
            "method": mfa_settings.mfa_method,
            "backup_codes_count": BackupCode.objects.filter(
                user=self.user,
                used=False
            ).count()
        }
    
    def regenerate_backup_codes(self, password: str) -> dict:
        """
        Regenerate backup codes (invalidates old ones).
        
        Args:
            password: User's password for verification
            
        Returns:
            dict: New backup codes
            
        Raises:
            ValidationError: If password is incorrect
        """
        if not self.user.check_password(password):
            raise ValidationError("Password is incorrect.")
        
        # Delete old backup codes
        BackupCode.objects.filter(user=self.user).delete()
        
        # Generate new ones
        backup_codes = self.mfa_service.generate_backup_codes(count=10)
        
        return {
            "backup_codes": backup_codes,
            "message": "Backup codes regenerated. Save them securely."
        }
    
    # ==================== Profile Update Requests ====================
    
    @transaction.atomic
    def request_profile_update(self, requested_data: dict, website=None) -> dict:
        """
        Request profile update (for fields requiring admin approval).
        
        Args:
            requested_data: Dictionary of fields to update
            website: Website instance
            
        Returns:
            dict: Success message
        """
        if not website:
            website = getattr(self.user, 'website', None)
            if not website:
                from websites.models import Website
                website = Website.objects.first()
        
        if not website:
            raise ValidationError("Website is required.")
        
        # Fields that require admin approval
        admin_approval_fields = ["email", "role", "website"]
        
        # Separate auto-approve from admin-approval fields
        auto_approve = {}
        admin_approval = {}
        
        for field, value in requested_data.items():
            if field in admin_approval_fields:
                admin_approval[field] = value
            else:
                auto_approve[field] = value
        
        # Apply auto-approve updates immediately
        if auto_approve:
            for field, value in auto_approve.items():
                if hasattr(self.user, field):
                    setattr(self.user, field, value)
            self.user.save()
        
        # Create update request for admin-approval fields
        if admin_approval:
            ProfileUpdateRequest.objects.create(
                user=self.user,
                website=website,
                requested_data=admin_approval
            )
            return {
                "message": "Profile updated. Some changes require admin approval.",
                "auto_approved": auto_approve,
                "pending_approval": admin_approval
            }
        
        return {
            "message": "Profile updated successfully.",
            "auto_approved": auto_approve
        }
    
    def get_profile_update_requests(self) -> list:
        """
        Get all profile update requests for the user.
        
        Returns:
            list: List of update requests
        """
        requests = ProfileUpdateRequest.objects.filter(user=self.user).order_by('-created_at')
        return [
            {
                "id": req.id,
                "requested_data": req.requested_data,
                "status": req.status,
                "admin_response": req.admin_response,
                "created_at": req.created_at,
                "updated_at": req.updated_at
            }
            for req in requests
        ]
    
    # ==================== Account Deletion ====================
    
    @transaction.atomic
    def request_account_deletion(self, reason: str = None, website=None) -> dict:
        """
        Request account deletion.
        
        Args:
            reason: Optional reason for deletion
            website: Website instance (for multitenancy)
            
        Returns:
            dict: Success message
        """
        if not website:
            website = getattr(self.user, 'website', None)
            if not website:
                from websites.models import Website
                website = Website.objects.first()
        
        if not website:
            raise ValidationError("Website is required for account deletion.")
        
        # Check if request already exists
        existing = AccountDeletionRequest.objects.filter(
            user=self.user,
            website=website,
            status='pending'
        ).first()
        
        if existing:
            raise ValidationError("Account deletion request already pending.")
        
        # Create deletion request
        AccountDeletionRequest.objects.create(
            user=self.user,
            website=website,
            reason=reason
        )
        
        # Notify admins
        self._notify_admins_deletion_request()
        
        return {
            "message": "Account deletion request submitted. Your account will be deleted after the grace period."
        }
    
    def _notify_admins_deletion_request(self):
        """Notify admins about deletion request."""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            admin_emails = User.objects.filter(
                role__in=['admin', 'superadmin']
            ).values_list('email', flat=True)
            
            if admin_emails:
                send_mail(
                    subject="New Account Deletion Request",
                    message=f"User {self.user.email} has requested account deletion.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=list(admin_emails),
                    fail_silently=True
                )
        except Exception:
            pass  # Don't fail if email fails
    
    def get_deletion_status(self) -> dict:
        """
        Get account deletion request status.
        
        Returns:
            dict: Deletion status information
        """
        request = AccountDeletionRequest.objects.filter(
            user=self.user
        ).order_by('-request_time').first()
        
        if not request:
            return {"requested": False}
        
        return {
            "requested": True,
            "status": request.status,
            "reason": request.reason,
            "created_at": request.request_time,
            "scheduled_deletion_date": request.scheduled_deletion_time
        }
    
    # ==================== Security Settings ====================
    
    def get_security_settings(self) -> dict:
        """
        Get user's security settings summary.
        
        Returns:
            dict: Security settings information
        """
        mfa_status = self.get_2fa_status()
        deletion_status = self.get_deletion_status()
        
        return {
            "email_verified": getattr(self.user, 'email_verified', False),
            "two_factor_enabled": mfa_status["enabled"],
            "two_factor_method": mfa_status["method"],
            "backup_codes_remaining": mfa_status["backup_codes_count"],
            "account_deletion_requested": deletion_status["requested"],
            "last_password_change": getattr(self.user, 'last_password_change', None),
            "account_created": self.user.date_joined
        }

