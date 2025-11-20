from django.core.mail import send_mail
from django.conf import settings
from authentication.services.token_services import SecureTokenService

class UnlockEmailService:
    """Service to handle sending unlock account emails."""

    @staticmethod
    def send_unlock_notice(user):
        """Sends an email to the user with a link to unlock their account."""
        unlock_url = f"{settings.FRONTEND_URL}/unlock-account?email={user.email}"
        send_mail(
            "Unlock Your Account",
            f"Click the link to unlock your account: {unlock_url}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )

    @staticmethod
    def send_unlock_email(user):
        token = SecureTokenService.create_token(
            user=user,
            purpose="unlock_account",
            expiry_minutes=30
        )

        url = f"{settings.FRONTEND_URL}/unlock-account/confirm/?token={token.token}"
        send_mail(
            subject="Unlock Your Account",
            message=f"Click to unlock your account:\n\n{url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email]
        )