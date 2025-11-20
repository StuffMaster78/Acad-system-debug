from authentication.models.logout import LogoutEvent
import logging

logger = logging.getLogger(__name__)

class LogoutEventService:
    """
    Handles creation of logout event records.
    """

    @staticmethod
    def log_event(user, website, ip_address=None,
                  user_agent=None, session_key=None,
                  reason="user_initiated"):
        """
        Creates a logout event entry.

        Args:
            user (User): The user logging out.
            website (Website): The tenant context (required).
            ip_address (str): IP address of the request.
            user_agent (str): User agent string.
            session_key (str): Session key, if any.
            reason (str): Reason for logout.
        
        Returns:
            LogoutEvent instance or None if website is missing
        """
        if not website:
            logger.warning(
                f"Cannot create logout event for user {user.id}: website is required but not provided"
            )
            return None
        
        try:
            return LogoutEvent.objects.create(
                user=user,
                website=website,
                ip_address=ip_address,
                user_agent=user_agent,
                session_key=session_key,
                reason=reason
            )
        except Exception as e:
            logger.error(f"Failed to create logout event: {e}", exc_info=True)
            return None