"""
Unified Account Management ViewSet

Provides comprehensive account management endpoints:
- Password management (change, reset)
- 2FA/MFA setup and management
- Profile update requests
- Account security settings
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.core.exceptions import ValidationError

from users.services.account_service import AccountService
from users.services.phone_reminder_service import PhoneReminderService
from users.serializers.account_serializers import (
    ChangePasswordSerializer,
    CompletePasswordResetSerializer,
    ProfileUpdateRequestSerializer,
    AccountDeletionRequestSerializer,
)


class AccountManagementViewSet(viewsets.ViewSet):
    """
    Unified account management endpoints.
    """
    permission_classes = [IsAuthenticated]
    
    def get_service(self):
        """Get account service instance for current user."""
        return AccountService(self.request.user)
    
    @action(detail=False, methods=['get'], url_path='phone-reminder')
    def get_phone_reminder(self, request):
        """
        Get phone number reminder information for the current user.
        
        Response:
        {
            "needs_reminder": true,
            "has_phone_number": false,
            "phone_number": null,
            "message": "Please update your phone number...",
            "reasons": ["Order fulfillment coordination", ...]
        }
        """
        service = PhoneReminderService(request.user)
        reminder_info = service.get_reminder_info()
        return Response(reminder_info, status=status.HTTP_200_OK)
    
    # ==================== Password Management ====================
    
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """
        Change user's password.
        
        Request body:
        {
            "current_password": "oldpass123",
            "new_password": "newpass123"
        }
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            service = self.get_service()
            result = service.change_password(
                current_password=serializer.validated_data['current_password'],
                new_password=serializer.validated_data['new_password']
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'], url_path='request-password-reset', permission_classes=[])
    def request_password_reset(self, request):
        """
        Request password reset (public endpoint).
        
        Request body:
        {
            "email": "user@example.com"
        }
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        email = request.data.get('email')
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Security: don't reveal if email exists
            return Response(
                {"message": "If that email exists, a password reset link was sent."},
                status=status.HTTP_200_OK
            )
        
        try:
            service = AccountService(user)
            result = service.request_password_reset()
            # Remove sensitive data from response
            result.pop('token', None)
            result.pop('otp_code', None)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='complete-password-reset', permission_classes=[])
    def complete_password_reset(self, request):
        """
        Complete password reset using token and OTP.
        
        Request body:
        {
            "token": "reset_token",
            "otp_code": "123456",
            "new_password": "newpass123"
        }
        """
        serializer = CompletePasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Get user from token
            from authentication.models.password_reset import PasswordResetRequest
            reset_request = PasswordResetRequest.objects.get(
                token=serializer.validated_data['token']
            )
            user = reset_request.user
            
            service = AccountService(user)
            result = service.complete_password_reset(
                token=serializer.validated_data['token'],
                otp_code=serializer.validated_data['otp_code'],
                new_password=serializer.validated_data['new_password']
            )
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
        except Exception as e:
            return Response(
                {"error": "Invalid reset token or OTP code."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # ==================== 2FA/MFA Management ====================
    
    @action(detail=False, methods=['get'], url_path='2fa/status')
    def get_2fa_status(self, request):
        """Get current 2FA status."""
        service = self.get_service()
        result = service.get_2fa_status()
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'], url_path='2fa/setup')
    def setup_2fa(self, request):
        """
        Setup TOTP-based 2FA (generates secret and QR code).
        
        Returns QR code and backup codes.
        """
        service = self.get_service()
        try:
            result = service.setup_2fa_totp()
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'], url_path='2fa/verify-and-enable')
    def verify_and_enable_2fa(self, request):
        """
        Verify TOTP code and enable 2FA.
        
        Request body:
        {
            "totp_code": "123456"
        }
        """
        totp_code = request.data.get('totp_code')
        if not totp_code:
            return Response(
                {"error": "TOTP code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        try:
            result = service.verify_and_enable_2fa(totp_code)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'], url_path='2fa/disable')
    def disable_2fa(self, request):
        """
        Disable 2FA (requires password or backup code).
        
        Request body:
        {
            "password": "userpassword",
            "backup_code": "optional_backup_code"
        }
        """
        password = request.data.get('password')
        backup_code = request.data.get('backup_code')
        
        if not password and not backup_code:
            return Response(
                {"error": "Password or backup code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        try:
            result = service.disable_2fa(password=password, backup_code=backup_code)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['post'], url_path='2fa/regenerate-backup-codes')
    def regenerate_backup_codes(self, request):
        """
        Regenerate backup codes.
        
        Request body:
        {
            "password": "userpassword"
        }
        """
        password = request.data.get('password')
        if not password:
            return Response(
                {"error": "Password is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = self.get_service()
        try:
            result = service.regenerate_backup_codes(password)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    # ==================== Profile Update Requests ====================
    
    @action(detail=False, methods=['post'], url_path='request-profile-update')
    def request_profile_update(self, request):
        """
        Request profile update (for fields requiring admin approval).
        
        Request body:
        {
            "email": "newemail@example.com",
            "phone_number": "+1234567890",
            ...
        }
        """
        requested_data = request.data
        
        service = self.get_service()
        try:
            result = service.request_profile_update(requested_data)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['get'], url_path='profile-update-requests')
    def get_profile_update_requests(self, request):
        """Get all profile update requests for the user."""
        service = self.get_service()
        requests = service.get_profile_update_requests()
        return Response(requests, status=status.HTTP_200_OK)
    
    # ==================== Account Deletion ====================
    
    @action(detail=False, methods=['post'], url_path='request-deletion')
    def request_account_deletion(self, request):
        """
        Request account deletion.
        
        Request body:
        {
            "reason": "Optional reason for deletion"
        }
        """
        reason = request.data.get('reason')
        website = getattr(request.user, 'website', None)
        
        service = self.get_service()
        try:
            result = service.request_account_deletion(reason=reason, website=website)
            return Response(result, status=status.HTTP_200_OK)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['get'], url_path='deletion-status')
    def get_deletion_status(self, request):
        """Get account deletion request status."""
        service = self.get_service()
        result = service.get_deletion_status()
        return Response(result, status=status.HTTP_200_OK)
    
    # ==================== Security Settings ====================
    
    @action(detail=False, methods=['get'], url_path='security-settings')
    def get_security_settings(self, request):
        """Get comprehensive security settings summary."""
        service = self.get_service()
        result = service.get_security_settings()
        return Response(result, status=status.HTTP_200_OK)

