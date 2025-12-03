"""
Email Change Service
Manages email change requests with verification.
"""
import logging
import secrets
from typing import Optional, Dict, Any
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from authentication.models.account_security import EmailChangeRequest
from websites.utils import get_current_website

logger = logging.getLogger(__name__)
User = get_user_model()


class EmailChangeService:
    """
    Service for managing email change requests with verification.
    """
    
    TOKEN_EXPIRY_HOURS = 24
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def request_email_change(self, new_email: str, require_old_email_confirmation: bool = True) -> EmailChangeRequest:
        """
        Request email change.
        
        Args:
            new_email: New email address
            require_old_email_confirmation: Whether to require old email confirmation
        
        Returns:
            Created EmailChangeRequest instance
        
        Raises:
            ValidationError: If email is invalid or already in use
        """
        if not self.website:
            raise ValueError("Website context required")
        
        # Validate new email
        if new_email.lower() == self.user.email.lower():
            raise ValidationError("New email must be different from current email")
        
        # Check if email is already in use
        if User.objects.filter(email__iexact=new_email).exclude(id=self.user.id).exists():
            raise ValidationError("This email address is already in use")
        
        # Only clients can request email changes (not admins setting it for them)
        if self.user.role not in ['client', 'customer']:
            raise ValidationError("Only clients can request email changes. Please contact support.")
        
        # Cancel any existing pending requests
        EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=['pending', 'admin_approved', 'email_verified']
        ).update(status='cancelled')
        
        # Generate tokens
        verification_token = secrets.token_urlsafe(32)
        old_email_token = secrets.token_urlsafe(32) if require_old_email_confirmation else None
        
        # Create request (status: pending, requires admin approval)
        expires_at = timezone.now() + timezone.timedelta(hours=self.TOKEN_EXPIRY_HOURS)
        request = EmailChangeRequest.objects.create(
            user=self.user,
            website=self.website,
            old_email=self.user.email,
            new_email=new_email,
            verification_token=verification_token,
            old_email_verification_token=old_email_token,
            status='pending',  # Requires admin approval
            expires_at=expires_at,
        )
        
        # Send notification to admins (not verification email yet - wait for approval)
        self._notify_admins_of_request(request)
        
        # Log security event
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='email_change_requested',
                severity='high',
                is_suspicious=False,
                metadata={
                    'old_email': self.user.email,
                    'new_email': new_email,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
        
        return request
    
    def approve_email_change(self, admin_user, rejection_reason: str = None) -> bool:
        """
        Admin approves or rejects email change request.
        
        Args:
            admin_user: Admin user approving/rejecting
            rejection_reason: Reason for rejection (if rejecting)
        
        Returns:
            True if approved, False if rejected
        """
        if not self.website:
            raise ValueError("Website context required")
        
        # Check admin permissions
        if admin_user.role not in ['admin', 'superadmin']:
            raise ValidationError("Only admins can approve email changes")
        
        pending_request = EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            status='pending'
        ).order_by('-created_at').first()
        
        if not pending_request:
            raise ValidationError("No pending email change request found")
        
        if pending_request.is_expired:
            pending_request.status = 'cancelled'
            pending_request.save()
            raise ValidationError("Email change request has expired")
        
        if rejection_reason:
            # Reject request
            pending_request.status = 'rejected'
            pending_request.rejection_reason = rejection_reason
            pending_request.save()
            
            # Notify user of rejection
            self._send_rejection_email(pending_request, rejection_reason)
            return False
        else:
            # Approve request
            pending_request.status = 'admin_approved'
            pending_request.admin_approved = True
            pending_request.approved_by = admin_user
            pending_request.approved_at = timezone.now()
            pending_request.save()
            
            # Now send verification email to new email
            self._send_verification_emails(pending_request)
            
            # Log security event
            from authentication.models.security_events import SecurityEvent
            try:
                SecurityEvent.log_event(
                    user=self.user,
                    website=self.website,
                    event_type='email_change_approved',
                    severity='high',
                    is_suspicious=False,
                    metadata={
                        'old_email': pending_request.old_email,
                        'new_email': pending_request.new_email,
                        'approved_by': admin_user.email,
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to log security event: {e}")
            
            return True
    
    def verify_new_email(self, token: str) -> bool:
        """
        Verify new email address.
        
        Args:
            token: Verification token from email
        
        Returns:
            True if verified successfully
        
        Raises:
            ValidationError: If token is invalid or expired
        """
        if not self.website:
            raise ValueError("Website context required")
        
        try:
            request = EmailChangeRequest.objects.get(
                user=self.user,
                website=self.website,
                verification_token=token,
                status='admin_approved'  # Must be approved first
            )
        except EmailChangeRequest.DoesNotExist:
            raise ValidationError("Invalid or expired verification token. Please ensure your request has been approved by an admin.")
        
        if request.is_expired:
            raise ValidationError("Verification token has expired")
        
        if not request.admin_approved:
            raise ValidationError("Email change request must be approved by an admin before verification")
        
        # Mark as verified and update status
        request.verified = True
        request.status = 'email_verified'
        request.save(update_fields=['verified', 'status'])
        
        # If old email confirmation not required, complete change immediately
        # Otherwise, wait for old email confirmation
        if not request.old_email_verification_token:
            self._complete_email_change(request)
        
        return True
    
    def confirm_old_email(self, token: str) -> bool:
        """
        Confirm old email address (if required).
        
        Args:
            token: Old email confirmation token
        
        Returns:
            True if confirmed successfully
        
        Raises:
            ValidationError: If token is invalid
        """
        if not self.website:
            raise ValueError("Website context required")
        
        try:
            request = EmailChangeRequest.objects.get(
                user=self.user,
                website=self.website,
                old_email_verification_token=token,
                status='email_verified',  # New email must be verified first
                old_email_confirmed=False
            )
        except EmailChangeRequest.DoesNotExist:
            raise ValidationError("Invalid confirmation token")
        
        if request.is_expired:
            raise ValidationError("Confirmation token has expired")
        
        # Mark old email as confirmed
        request.old_email_confirmed = True
        request.save(update_fields=['old_email_confirmed'])
        
        # Complete email change
        self._complete_email_change(request)
        
        return True
    
    def _complete_email_change(self, request: EmailChangeRequest):
        """Complete email change process."""
        # Update user email
        old_email = self.user.email
        self.user.email = request.new_email
        self.user.email_verified = False  # Require re-verification of new email
        self.user.save(update_fields=['email', 'email_verified'])
        
        # Mark request as completed
        request.status = 'completed'
        request.completed_at = timezone.now()
        request.save(update_fields=['status', 'completed_at'])
        
        # Send confirmation email to new email
        self._send_change_confirmation_email(request.new_email, old_email)
        
        # Log security event
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='email_changed',
                severity='high',
                is_suspicious=False,
                metadata={
                    'old_email': old_email,
                    'new_email': request.new_email,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
    
    def _notify_admins_of_request(self, request: EmailChangeRequest):
        """Notify admins of email change request."""
        from users.models import User
        admins = User.objects.filter(
            role__in=['admin', 'superadmin'],
            is_active=True
        )
        
        admin_emails = [admin.email for admin in admins if admin.email]
        
        if admin_emails:
            admin_url = f"{settings.FRONTEND_URL}/admin/email-changes/{request.id}/"
            send_mail(
                subject=f"Email Change Request - {request.user.email}",
                message=f"""
                A client has requested to change their email address.
                
                User: {request.user.email} (ID: {request.user.id})
                Old Email: {request.old_email}
                New Email: {request.new_email}
                
                Please review and approve/reject this request:
                {admin_url}
                
                Request expires at: {request.expires_at}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                fail_silently=False,
            )
    
    def _send_rejection_email(self, request: EmailChangeRequest, reason: str):
        """Send rejection email to user."""
        send_mail(
            subject="Email Change Request Rejected",
            message=f"""
            Your email change request has been rejected.
            
            Reason: {reason}
            
            If you believe this is an error, please contact support.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=False,
        )
    
    def _send_verification_emails(self, request: EmailChangeRequest):
        """Send verification emails to old and new email addresses."""
        # Send to new email
        verification_url = f"{settings.FRONTEND_URL}/verify-email-change?token={request.verification_token}"
        
        send_mail(
            subject="Verify Your New Email Address",
            message=f"""
            You have requested to change your email address.
            
            Please click the link below to verify your new email address:
            {verification_url}
            
            This link will expire in {self.TOKEN_EXPIRY_HOURS} hours.
            
            If you did not request this change, please ignore this email or contact support.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.new_email],
            fail_silently=False,
        )
        
        # Send notification to old email
        if request.old_email_verification_token:
            confirmation_url = f"{settings.FRONTEND_URL}/confirm-email-change?token={request.old_email_verification_token}"
            
            send_mail(
                subject="Email Change Request - Action Required",
                message=f"""
                A request has been made to change your email address from {request.old_email} to {request.new_email}.
                
                If this was you, please confirm by clicking the link below:
                {confirmation_url}
                
                If you did not request this change, please contact support immediately.
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.old_email],
                fail_silently=False,
            )
    
    def _send_change_confirmation_email(self, new_email: str, old_email: str):
        """Send confirmation email after email change is completed."""
        send_mail(
            subject="Email Address Changed Successfully",
            message=f"""
            Your email address has been successfully changed from {old_email} to {new_email}.
            
            If you did not make this change, please contact support immediately.
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
            fail_silently=False,
        )
    
    def cancel_request(self):
        """Cancel pending email change request."""
        if not self.website:
            return
        
        EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            verified=False
        ).update(verified=True)  # Mark as cancelled
    
    def get_pending_request(self) -> Optional[EmailChangeRequest]:
        """Get pending email change request if any."""
        if not self.website:
            return None
        
        return EmailChangeRequest.objects.filter(
            user=self.user,
            website=self.website,
            status__in=['pending', 'admin_approved', 'email_verified'],
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()
    
    def get_all_requests(self, status_filter: str = None):
        """Get all email change requests (for admins)."""
        if not self.website:
            return EmailChangeRequest.objects.none()
        
        queryset = EmailChangeRequest.objects.filter(website=self.website)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')

