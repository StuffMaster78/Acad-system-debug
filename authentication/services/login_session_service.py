import uuid
from authentication.models.login import LoginSession
from django.utils.timezone import now
from typing import Optional, Dict, Any


class LoginSessionService:
    """
    Production-grade service for managing login sessions.
    Provides static methods for session creation and revocation.
    """
    
    @staticmethod
    def start_session(
        user,
        website,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_info: Optional[Dict[str, Any]] = None
    ) -> LoginSession:
        """
        Create a new login session.
        
        Args:
            user: User instance
            website: Website instance
            ip: IP address (optional)
            user_agent: User agent string (optional)
            device_info: Device information dict (optional)
        
        Returns:
            LoginSession: Created session instance
        """
        token = str(uuid.uuid4())
        
        device_name = None
        if device_info:
            device_name = device_info.get('device_name')
        
        session = LoginSession.objects.create(
            user=user,
            website=website,
            ip_address=ip,
            user_agent=user_agent,
            device_name=device_name,
            token=token,
            logged_in_at=now(),
            is_active=True
        )
        
        return session
    
    @staticmethod
    def revoke_session(
        user,
        session_id: Optional[str] = None,
        website=None
    ) -> bool:
        """
        Revoke a specific session.
        
        Args:
            user: User instance
            session_id: Session ID to revoke (optional)
            website: Website instance (optional)
        
        Returns:
            bool: True if session was revoked
        """
        try:
            qs = LoginSession.objects.filter(
                user=user,
                is_active=True
            )
            
            if session_id:
                qs = qs.filter(id=session_id)
            
            if website:
                qs = qs.filter(website=website)
            
            count = qs.update(is_active=False, revoked_at=now())
            return count > 0
        except Exception:
            return False
    
    @staticmethod
    def revoke_all_sessions(
        user,
        website=None,
        exclude_session_id: Optional[str] = None
    ) -> int:
        """
        Revoke all active sessions for a user.
        
        Args:
            user: User instance
            website: Website instance (optional)
            exclude_session_id: Session ID to exclude from revocation (optional)
        
        Returns:
            int: Number of sessions revoked
        """
        try:
            qs = LoginSession.objects.filter(
                user=user,
                is_active=True
            )
            
            if website:
                qs = qs.filter(website=website)
            
            if exclude_session_id:
                qs = qs.exclude(id=exclude_session_id)
            
            count = qs.update(is_active=False, revoked_at=now())
            return count
        except Exception:
            return 0