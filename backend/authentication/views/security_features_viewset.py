"""
Security Features ViewSet
Handles all new security features: password history, expiration, breach detection,
account suspension, IP whitelisting, email change, phone verification, session limits.
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from authentication.services.password_history_service import PasswordHistoryService
from authentication.services.password_expiration_service import PasswordExpirationService
from authentication.services.password_breach_service import PasswordBreachService
from authentication.services.account_suspension_service import AccountSuspensionService
from authentication.services.ip_whitelist_service import IPWhitelistService
from authentication.services.email_change_service import EmailChangeService
from authentication.services.session_limit_service import SessionLimitService
from authentication.serializers import (
    PasswordHistorySerializer, PasswordExpirationPolicySerializer,
    PasswordBreachCheckSerializer, AccountSuspensionSerializer,
    IPWhitelistSerializer, UserIPWhitelistSettingsSerializer,
    EmailChangeRequestSerializer, PhoneVerificationSerializer,
    SessionLimitPolicySerializer, SecurityQuestionSerializer,
    UserSecurityQuestionSerializer
)
from authentication.decorators import require_email_verified, require_additional_verification
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PasswordSecurityViewSet(viewsets.ViewSet):
    """
    ViewSet for password security features: history, expiration, breach detection.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='history')
    def get_history(self, request):
        """Get password history count."""
        service = PasswordHistoryService(request.user)
        return Response({
            'history_count': service.get_history_count(),
            'max_history': PasswordHistoryService.DEFAULT_HISTORY_DEPTH
        })
    
    @action(detail=False, methods=['get'], url_path='expiration-status')
    def get_expiration_status(self, request):
        """Get password expiration status."""
        service = PasswordExpirationService(request.user)
        status_info = service.check_expiration_status()
        return Response(status_info)
    
    @action(detail=False, methods=['post'], url_path='check-breach')
    def check_password_breach(self, request):
        """Check if a password has been breached."""
        password = request.data.get('password')
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PasswordBreachService(request.user)
        result = service.check_password_breach(password)
        return Response(result)
    
    @action(detail=False, methods=['get'], url_path='breach-history')
    def get_breach_history(self, request):
        """Get recent breach check history."""
        service = PasswordBreachService(request.user)
        limit = int(request.query_params.get('limit', 10))
        history = service.get_breach_history(limit)
        serializer = PasswordBreachCheckSerializer(history, many=True)
        return Response(serializer.data)


class AccountSecurityViewSet(viewsets.ViewSet):
    """
    ViewSet for account security: suspension, IP whitelisting.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='suspend')
    @require_additional_verification(require_password=True)
    def suspend_account(self, request):
        """Suspend user's own account."""
        reason = request.data.get('reason', '')
        scheduled_reactivation = request.data.get('scheduled_reactivation')
        
        if scheduled_reactivation:
            try:
                scheduled_reactivation = timezone.datetime.fromisoformat(scheduled_reactivation.replace('Z', '+00:00'))
            except Exception:
                return Response(
                    {'error': 'Invalid scheduled_reactivation format'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        service = AccountSuspensionService(request.user)
        service.suspend(reason, scheduled_reactivation)
        
        return Response({
            'message': 'Account suspended successfully',
            'suspension_info': service.get_suspension_info()
        })
    
    @action(detail=False, methods=['post'], url_path='reactivate')
    @require_additional_verification(require_password=True)
    def reactivate_account(self, request):
        """Reactivate suspended account."""
        service = AccountSuspensionService(request.user)
        service.reactivate()
        
        return Response({
            'message': 'Account reactivated successfully'
        })
    
    @action(detail=False, methods=['get'], url_path='suspension-status')
    def get_suspension_status(self, request):
        """Get account suspension status."""
        service = AccountSuspensionService(request.user)
        return Response(service.get_suspension_info())
    
    # IP Whitelist endpoints
    @action(detail=False, methods=['get'], url_path='ip-whitelist')
    def get_ip_whitelist(self, request):
        """Get user's IP whitelist."""
        service = IPWhitelistService(request.user)
        whitelisted_ips = service.get_whitelisted_ips()
        serializer = IPWhitelistSerializer(whitelisted_ips, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='ip-whitelist/add')
    @require_additional_verification(require_password=True)
    def add_ip_to_whitelist(self, request):
        """Add IP to whitelist."""
        ip_address = request.data.get('ip_address')
        label = request.data.get('label', '')
        
        if not ip_address:
            return Response(
                {'error': 'IP address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = IPWhitelistService(request.user)
        entry = service.add_ip(ip_address, label)
        serializer = IPWhitelistSerializer(entry)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'], url_path='ip-whitelist/remove')
    @require_additional_verification(require_password=True)
    def remove_ip_from_whitelist(self, request):
        """Remove IP from whitelist."""
        ip_address = request.data.get('ip_address')
        
        if not ip_address:
            return Response(
                {'error': 'IP address is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = IPWhitelistService(request.user)
        service.remove_ip(ip_address)
        return Response({'message': 'IP removed from whitelist'})
    
    @action(detail=False, methods=['post'], url_path='ip-whitelist/enable')
    @require_additional_verification(require_password=True)
    def enable_ip_whitelist(self, request):
        """Enable IP whitelist."""
        service = IPWhitelistService(request.user)
        service.enable_whitelist()
        return Response({'message': 'IP whitelist enabled'})
    
    @action(detail=False, methods=['post'], url_path='ip-whitelist/disable')
    @require_additional_verification(require_password=True)
    def disable_ip_whitelist(self, request):
        """Disable IP whitelist."""
        service = IPWhitelistService(request.user)
        service.disable_whitelist()
        return Response({'message': 'IP whitelist disabled'})
    
    @action(detail=False, methods=['get'], url_path='ip-whitelist/settings')
    def get_ip_whitelist_settings(self, request):
        """Get IP whitelist settings."""
        service = IPWhitelistService(request.user)
        settings = service.get_or_create_settings()
        serializer = UserIPWhitelistSettingsSerializer(settings)
        return Response(serializer.data)


class EmailChangeViewSet(viewsets.ViewSet):
    """
    ViewSet for email change with verification and admin approval.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='request')
    @require_additional_verification(require_password=True)
    def request_email_change(self, request):
        """
        Request email change (clients only).
        Requires admin approval before email verification.
        """
        # Only clients can request email changes
        if request.user.role not in ['client', 'customer']:
            return Response(
                {'error': 'Only clients can request email changes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_email = request.data.get('new_email')
        require_old_email_confirmation = request.data.get('require_old_email_confirmation', True)
        
        if not new_email:
            return Response(
                {'error': 'New email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = EmailChangeService(request.user)
        try:
            change_request = service.request_email_change(new_email, require_old_email_confirmation)
            serializer = EmailChangeRequestSerializer(change_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_email_change(self, request, pk=None):
        """
        Admin approves email change request.
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can approve email changes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rejection_reason = request.data.get('rejection_reason')
        
        from authentication.models.account_security import EmailChangeRequest
        try:
            change_request = EmailChangeRequest.objects.get(id=pk)
        except EmailChangeRequest.DoesNotExist:
            return Response(
                {'error': 'Email change request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = EmailChangeService(change_request.user)
        try:
            approved = service.approve_email_change(request.user, rejection_reason)
            if approved:
                return Response({'message': 'Email change approved. User will receive verification email.'})
            else:
                return Response({'message': 'Email change rejected.'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='admin/pending')
    def get_pending_requests(self, request):
        """
        Get all pending email change requests (admin only).
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can view pending requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from authentication.models.account_security import EmailChangeRequest
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        service = EmailChangeService(request.user, website)
        requests = service.get_all_requests(status_filter='pending')
        serializer = EmailChangeRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_new_email(self, request):
        """Verify new email address."""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Verification token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = EmailChangeService(request.user)
        try:
            service.verify_new_email(token)
            return Response({'message': 'Email verified successfully'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='confirm-old-email')
    def confirm_old_email(self, request):
        """Confirm old email address."""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Confirmation token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = EmailChangeService(request.user)
        try:
            service.confirm_old_email(token)
            return Response({'message': 'Email change completed successfully'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='pending')
    def get_pending_request(self, request):
        """Get pending email change request."""
        service = EmailChangeService(request.user)
        pending = service.get_pending_request()
        
        if pending:
            serializer = EmailChangeRequestSerializer(pending)
            return Response(serializer.data)
        return Response({'pending_request': None})
    
    @action(detail=False, methods=['post'], url_path='cancel')
    @require_additional_verification(require_password=True)
    def cancel_request(self, request):
        """Cancel pending email change request."""
        service = EmailChangeService(request.user)
        service.cancel_request()
        return Response({'message': 'Email change request cancelled'})


class PhoneVerificationViewSet(viewsets.ViewSet):
    """
    ViewSet for phone number verification.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='request')
    @require_additional_verification(require_password=True)
    def request_verification(self, request):
        """Request phone verification code."""
        phone_number = request.data.get('phone_number')
        
        if not phone_number:
            return Response(
                {'error': 'Phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from authentication.services.phone_verification_service import PhoneVerificationService
        service = PhoneVerificationService(request.user)
        
        try:
            verification = service.request_verification(phone_number)
            serializer = PhoneVerificationSerializer(verification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'], url_path='verify')
    def verify_code(self, request):
        """Verify phone verification code."""
        code = request.data.get('code')
        phone_number = request.data.get('phone_number')
        
        if not code or not phone_number:
            return Response(
                {'error': 'Code and phone number are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from authentication.services.phone_verification_service import PhoneVerificationService
        service = PhoneVerificationService(request.user)
        
        try:
            service.verify_code(phone_number, code)
            return Response({'message': 'Phone number verified successfully'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SessionLimitViewSet(viewsets.ViewSet):
    """
    ViewSet for session limit management.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='info')
    def get_session_limit_info(self, request):
        """Get session limit information."""
        service = SessionLimitService(request.user)
        info = service.get_session_limit_info()
        return Response(info)
    
    @action(detail=False, methods=['post'], url_path='update-policy')
    @require_additional_verification(require_password=True)
    def update_policy(self, request):
        """Update session limit policy."""
        service = SessionLimitService(request.user)
        
        service.update_policy(
            max_concurrent_sessions=request.data.get('max_concurrent_sessions'),
            allow_unlimited_trusted=request.data.get('allow_unlimited_trusted'),
            revoke_oldest_on_limit=request.data.get('revoke_oldest_on_limit')
        )
        
        return Response({'message': 'Session limit policy updated'})

