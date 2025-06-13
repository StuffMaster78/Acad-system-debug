from authentication.models.login import LoginSession
from authentication.models.logout import LogoutEvent
from django.utils import timezone


class KickoutService:
    """
    Handles admin-initiated user session terminations.
    """

    def __init__(self, website):
        self.website = website

    def kick_user(self, user, performed_by, ip_address=None, reason=""):
        """
        Kicks a user from sessions. Can be global or IP-specific.
        """
        query = LoginSession.objects.filter(
            user=user,
            website=self.website,
            is_active=True
        )
        if ip_address:
            query = query.filter(ip_address=ip_address)

        sessions = query.all()
        count = sessions.count()

        for session in sessions:
            LogoutEvent.objects.create(
                user=user,
                ip_address=session.ip_address,
                user_agent=session.user_agent,
                session_key=session.token,
                reason=reason or "admin_kick"
            )
            session.is_active = False
            session.save()

        return count