"""
Session Limit Service
Manages concurrent session limits and enforcement.
"""
import logging
from typing import Optional, List
from django.utils import timezone
from django.core.exceptions import ValidationError
from authentication.models.login import LoginSession
from authentication.models.session_limits import SessionLimitPolicy
from websites.utils import get_current_website

logger = logging.getLogger(__name__)


class SessionLimitService:
    """
    Service for managing concurrent session limits.
    """
    
    DEFAULT_MAX_SESSIONS = 3
    
    def __init__(self, user, website=None):
        self.user = user
        self.website = website or get_current_website()
        if not self.website:
            from websites.models import Website
            self.website = Website.objects.filter(is_active=True).first()
    
    def get_or_create_policy(self) -> SessionLimitPolicy:
        """Get or create session limit policy for user."""
        if not self.website:
            raise ValueError("Website context required for session limit policy")
        
        policy, created = SessionLimitPolicy.objects.get_or_create(
            user=self.user,
            website=self.website,
            defaults={
                'max_concurrent_sessions': self.DEFAULT_MAX_SESSIONS,
                'allow_unlimited_trusted': False,
                'revoke_oldest_on_limit': True,
            }
        )
        return policy
    
    def get_active_sessions(self) -> List[LoginSession]:
        """Get all active sessions for user."""
        if not self.website:
            return []
        
        return list(LoginSession.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('last_activity'))
    
    def get_active_session_count(self) -> int:
        """Get count of active sessions."""
        return len(self.get_active_sessions())
    
    def enforce_session_limit(self, new_session: LoginSession = None) -> Optional[LoginSession]:
        """
        Enforce session limit by revoking oldest sessions if needed.
        
        Args:
            new_session: New session being created (optional)
        
        Returns:
            Revoked session if one was revoked, None otherwise
        """
        policy = self.get_or_create_policy()
        
        # Check if unlimited for trusted devices
        if policy.allow_unlimited_trusted and new_session:
            from authentication.models.devices import TrustedDevice
            device_token = getattr(new_session, 'device_token', None)
            if device_token:
                is_trusted = TrustedDevice.objects.filter(
                    user=self.user,
                    website=self.website,
                    device_token=device_token,
                    expires_at__gt=timezone.now()
                ).exists()
                if is_trusted:
                    return None  # No limit for trusted devices
        
        active_sessions = self.get_active_sessions()
        max_sessions = policy.max_concurrent_sessions
        
        if len(active_sessions) >= max_sessions:
            if policy.revoke_oldest_on_limit:
                # Revoke oldest session
                oldest_session = active_sessions[0]
                oldest_session.revoke()
                
                # Log security event
                from authentication.models.security_events import SecurityEvent
                try:
                    SecurityEvent.log_event(
                        user=self.user,
                        website=self.website,
                        event_type='session_revoked_limit',
                        severity='low',
                        is_suspicious=False,
                        metadata={
                            'reason': 'session_limit_reached',
                            'max_sessions': max_sessions,
                            'revoked_session_id': str(oldest_session.id),
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to log security event: {e}")
                
                return oldest_session
            else:
                # Don't revoke, just prevent new session
                raise ValidationError(
                    f"Maximum number of concurrent sessions ({max_sessions}) reached. "
                    "Please logout from another device or contact support."
                )
        
        return None
    
    def update_policy(
        self,
        max_concurrent_sessions: int = None,
        allow_unlimited_trusted: bool = None,
        revoke_oldest_on_limit: bool = None
    ):
        """
        Update session limit policy.
        
        Args:
            max_concurrent_sessions: Maximum concurrent sessions allowed
            allow_unlimited_trusted: Allow unlimited sessions from trusted devices
            revoke_oldest_on_limit: Revoke oldest session when limit reached
        """
        policy = self.get_or_create_policy()
        
        if max_concurrent_sessions is not None:
            policy.max_concurrent_sessions = max_concurrent_sessions
        if allow_unlimited_trusted is not None:
            policy.allow_unlimited_trusted = allow_unlimited_trusted
        if revoke_oldest_on_limit is not None:
            policy.revoke_oldest_on_limit = revoke_oldest_on_limit
        
        policy.save()
    
    def get_session_limit_info(self) -> dict:
        """Get session limit information for user."""
        policy = self.get_or_create_policy()
        active_count = self.get_active_session_count()
        
        return {
            'max_concurrent_sessions': policy.max_concurrent_sessions,
            'active_sessions': active_count,
            'remaining_sessions': max(0, policy.max_concurrent_sessions - active_count),
            'allow_unlimited_trusted': policy.allow_unlimited_trusted,
            'revoke_oldest_on_limit': policy.revoke_oldest_on_limit,
        }

