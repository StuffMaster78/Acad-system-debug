from authentication.models.login import LoginSession
from django.utils.timezone import now


class LoginSessionService:
    """
    Manages creation, lookup, and revocation of login sessions.
    """

    def __init__(self, user, website):
        """
        Args:
            user (User): The user logging in.
            website (Website): The multitenant website context.
        """
        self.user = user
        self.website = website

    def create_session(self, data):
        """
        Creates a new login session.

        Args:
            data (dict): Session info including ip_address, user_agent, 
                         device_name, and token.

        Returns:
            LoginSession: The created session instance.
        """
        return LoginSession.objects.create(
            user=self.user,
            website=self.website,
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            device_name=data.get("device_name"),
            token=data.get("token"),
            logged_in_at=now(),
            is_active=True
        )

    def revoke_session(self, token):
        """
        Deactivates a session by token.

        Args:
            token (str): The session token.

        Returns:
            bool: True if session revoked, False otherwise.
        """
        try:
            session = LoginSession.objects.get(
                user=self.user,
                website=self.website,
                token=token,
                is_active=True
            )
            session.is_active = False
            session.save()
            return True
        except LoginSession.DoesNotExist:
            return False