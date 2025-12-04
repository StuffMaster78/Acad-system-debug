"""
Account Suspension Service
Manages user-initiated account suspension.
"""
import logging
from typing import Optional
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from authentication.models.account_security import AccountSuspension
from authentication.models.login import LoginSession
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class AccountSuspensionService:
    """
    Service for managing user-initiated account suspension.
    """
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_or_create_suspension(self) -> AccountSuspension:
        """Get or create account suspension record."""
        if not self.website:
            raise ValueError("Website context required for account suspension")
        
        # Since AccountSuspension has OneToOneField on user, there can only be one per user
        # Try to get existing record first (by user only, since that's the unique constraint)
        try:
            suspension = AccountSuspension.objects.get(user=self.user)
            # Update website if it changed (though this shouldn't happen often)
            if suspension.website != self.website:
                suspension.website = self.website
                suspension.save(update_fields=['website'])
            return suspension
        except AccountSuspension.DoesNotExist:
            # Record doesn't exist, try to create it
            try:
                suspension = AccountSuspension.objects.create(
                    user=self.user,
                    website=self.website,
                    is_suspended=False,
                )
                return suspension
            except IntegrityError:
                # Race condition: another request created it between our get() and create()
                # The IntegrityError means the record exists (unique constraint violation)
                # Retry the get - we need to refresh from a new transaction
                logger.warning(f"Race condition detected for AccountSuspension (user={self.user.id}), retrying get")
                # Get the record in a new transaction (the failed transaction was rolled back)
                # Since IntegrityError occurred, the record must exist
                suspension = AccountSuspension.objects.get(user=self.user)
                # Update website if needed
                if suspension.website != self.website:
                    suspension.website = self.website
                    suspension.save(update_fields=['website'])
                return suspension
    
    def suspend(self, reason: str = "", scheduled_reactivation=None):
        """
        Suspend user account.
        
        Args:
            reason: Reason for suspension (user-provided)
            scheduled_reactivation: Optional datetime for automatic reactivation
        """
        suspension = self.get_or_create_suspension()
        suspension.suspend(reason, scheduled_reactivation)
        
        # Revoke all active sessions
        self._revoke_all_sessions()
        
        # Log security event
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='account_suspended',
                severity='medium',
                is_suspicious=False,
                metadata={
                    'reason': reason,
                    'scheduled_reactivation': scheduled_reactivation.isoformat() if scheduled_reactivation else None,
                    'user_initiated': True,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
    
    def reactivate(self):
        """Reactivate suspended account."""
        suspension = self.get_or_create_suspension()
        suspension.reactivate()
        
        # Log security event
        from authentication.models.security_events import SecurityEvent
        try:
            SecurityEvent.log_event(
                user=self.user,
                website=self.website,
                event_type='account_reactivated',
                severity='low',
                is_suspicious=False,
                metadata={
                    'user_initiated': True,
                }
            )
        except Exception as e:
            logger.warning(f"Failed to log security event: {e}")
    
    def is_suspended(self) -> bool:
        """Check if account is currently suspended."""
        suspension = self.get_or_create_suspension()
        
        # Check scheduled reactivation
        if suspension.is_suspended and suspension.scheduled_reactivation:
            suspension.check_scheduled_reactivation()
            suspension.refresh_from_db()
        
        return suspension.is_suspended
    
    def check_scheduled_reactivation(self):
        """Check and process scheduled reactivation."""
        suspension = self.get_or_create_suspension()
        if suspension.check_scheduled_reactivation():
            logger.info(f"Account {self.user.email} automatically reactivated")
    
    def _revoke_all_sessions(self):
        """Revoke all active sessions for user."""
        if not self.website:
            return
        
        active_sessions = LoginSession.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        )
        
        for session in active_sessions:
            session.revoke()
    
    def get_suspension_info(self) -> dict:
        """Get suspension information."""
        suspension = self.get_or_create_suspension()
        
        return {
            'is_suspended': suspension.is_suspended,
            'suspended_at': suspension.suspended_at.isoformat() if suspension.suspended_at else None,
            'suspension_reason': suspension.suspension_reason,
            'scheduled_reactivation': suspension.scheduled_reactivation.isoformat() if suspension.scheduled_reactivation else None,
            'reactivated_at': suspension.reactivated_at.isoformat() if suspension.reactivated_at else None,
        }

