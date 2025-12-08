"""
Password Expiration Service
Manages password expiration policies and enforcement.
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from authentication.models.password_security import PasswordExpirationPolicy
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class PasswordExpirationService:
    """
    Service for managing password expiration policies.
    """
    
    DEFAULT_EXPIRATION_DAYS = 90
    DEFAULT_WARNING_DAYS = 7
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_or_create_policy(self) -> PasswordExpirationPolicy:
        """Get or create password expiration policy for user."""
        if not self.website:
            raise ValueError("Website context required for password expiration policy")
        
        # Handle race condition: if another request creates the policy between
        # get() and create(), catch IntegrityError and retry get()
        # Note: user is OneToOneField, so unique constraint is only on user_id
        try:
            policy, created = PasswordExpirationPolicy.objects.get_or_create(
                user=self.user,
                defaults={
                    'website': self.website,
                    'password_changed_at': timezone.now(),
                    'expires_in_days': self.DEFAULT_EXPIRATION_DAYS,
                    'warning_days_before': self.DEFAULT_WARNING_DAYS,
                }
            )
            # Update website if it changed (for existing policies)
            if not created and policy.website != self.website:
                policy.website = self.website
                policy.save(update_fields=['website'])
            return policy
        except Exception as e:
            # If we get an IntegrityError (unique constraint violation),
            # another request created the policy between our get() and create()
            from django.db import IntegrityError
            if isinstance(e, IntegrityError):
                try:
                    # Retry getting the existing policy
                    policy = PasswordExpirationPolicy.objects.get(user=self.user)
                    # Update website if it's different
                    if policy.website != self.website:
                        policy.website = self.website
                        policy.save(update_fields=['website'])
                    return policy
                except PasswordExpirationPolicy.DoesNotExist:
                    # This shouldn't happen, but log it if it does
                    logger.error(f"IntegrityError but policy not found for user {self.user.id}")
                    raise
            # Re-raise if it's not an IntegrityError
            raise
    
    def update_password_changed(self):
        """Update password changed timestamp when user changes password."""
        policy = self.get_or_create_policy()
        policy.update_password_changed()
    
    def check_expiration_status(self) -> Dict[str, Any]:
        """
        Check password expiration status.
        
        Returns:
            Dict with expiration status information
        """
        policy = self.get_or_create_policy()
        
        if policy.is_exempt:
            return {
                'is_exempt': True,
                'is_expired': False,
                'is_expiring_soon': False,
                'days_until_expiration': None,
            }
        
        return {
            'is_exempt': False,
            'is_expired': policy.is_expired,
            'is_expiring_soon': policy.is_expiring_soon,
            'days_until_expiration': policy.days_until_expiration,
            'expires_at': policy.expires_at.isoformat() if policy.expires_at else None,
            'password_changed_at': policy.password_changed_at.isoformat(),
        }
    
    def require_password_change(self) -> bool:
        """
        Check if password change is required.
        
        Returns:
            True if password change is required
        """
        status = self.check_expiration_status()
        return status.get('is_expired', False)
    
    def should_send_warning(self) -> bool:
        """
        Check if expiration warning should be sent.
        
        Returns:
            True if warning should be sent
        """
        policy = self.get_or_create_policy()
        
        if policy.is_exempt or policy.is_expired:
            return False
        
        if not policy.is_expiring_soon:
            return False
        
        # Check if warning was already sent recently (within last 24 hours)
        if policy.last_warning_sent:
            from datetime import timedelta
            if timezone.now() - policy.last_warning_sent < timedelta(hours=24):
                return False
        
        return True
    
    def mark_warning_sent(self):
        """Mark that expiration warning was sent."""
        policy = self.get_or_create_policy()
        policy.last_warning_sent = timezone.now()
        policy.save(update_fields=['last_warning_sent'])
    
    def set_exemption(self, is_exempt: bool, reason: str = ""):
        """
        Set password expiration exemption for user.
        
        Args:
            is_exempt: Whether to exempt user from expiration
            reason: Reason for exemption (for audit)
        """
        policy = self.get_or_create_policy()
        policy.is_exempt = is_exempt
        policy.save(update_fields=['is_exempt'])
        
        # Log exemption change
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='password_expiration_exemption_changed',
                severity='low',
                is_suspicious=False,
                metadata={
                    'is_exempt': is_exempt,
                    'reason': reason,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
    
    def update_policy(self, expires_in_days: int = None, warning_days_before: int = None):
        """
        Update password expiration policy.
        
        Args:
            expires_in_days: Days until password expires
            warning_days_before: Days before expiration to warn
        """
        policy = self.get_or_create_policy()
        
        if expires_in_days is not None:
            policy.expires_in_days = expires_in_days
        if warning_days_before is not None:
            policy.warning_days_before = warning_days_before
        
        policy.save()

