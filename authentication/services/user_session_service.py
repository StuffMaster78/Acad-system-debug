from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.sessions.models import Session
from authentication.models import UserSession


class UserSessionService:
    """
    Handles creation, termination, validation, and refreshing
    of user sessions in a multitenant environment.
    """

    SESSION_TIMEOUT_HOURS = 24

    def __init__(self, user, website):
        self.user = user
        self.website = website

    def create_session(self, session_key, ip_address=None, device_type=None,
                       user_agent=None, country=None, expires_at=None):
        """
        Creates or updates a user session for this website.
        """
        if not expires_at:
            expires_at = timezone.now() + timedelta(hours=self.SESSION_TIMEOUT_HOURS)

        session, _ = UserSession.objects.update_or_create(
            session_key=session_key,
            website=self.website,
            defaults={
                "user": self.user,
                "ip_address": ip_address,
                "device_type": device_type,
                "user_agent": user_agent,
                "country": country,
                "expires_at": expires_at,
                "is_active": True
            }
        )
        return session

    def get_active_sessions(self):
        """
        Returns all active sessions for the user under this website.
        """
        return UserSession.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        )

    def terminate_session(self, session_key):
        """
        Terminates a session by session key.
        """
        try:
            session = UserSession.objects.get(
                session_key=session_key,
                user=self.user,
                website=self.website
            )
        except UserSession.DoesNotExist:
            raise ValidationError("Session not found.")
        session.terminate()
        return session

    def terminate_all_sessions(self, exclude_session_key=None):
        """
        Terminates all sessions for the user under this website,
        optionally excluding one.
        """
        qs = UserSession.objects.filter(
            user=self.user,
            website=self.website,
            is_active=True
        )
        if exclude_session_key:
            qs = qs.exclude(session_key=exclude_session_key)

        count = 0
        for session in qs:
            session.terminate()
            count += 1
        return count

    def refresh_session_activity(self, session_key):
        """
        Refreshes last activity timestamp if session is still active.
        """
        try:
            session = UserSession.objects.get(
                session_key=session_key,
                user=self.user,
                website=self.website,
                is_active=True
            )
        except UserSession.DoesNotExist:
            raise ValidationError("Active session not found.")

        if session.is_expired():
            raise ValidationError("Session expired.")

        session.last_activity = timezone.now()
        session.save(update_fields=["last_activity"])
        return session