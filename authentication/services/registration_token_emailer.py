from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from authentication.models.register import RegistrationToken


class RegistrationTokenEmailer:
    """
    Sends email with a registration token to the user's email.
    """

    def __init__(self, token: RegistrationToken, website: str = None):
        """
        Args:
            token (RegistrationToken): The token to email.
            website (str): Optional base URL for frontend.
        """
        self.token = token
        self.website = website or "https://example.com"

    def send(self):
        """
        Sends the registration email.
        """
        user_email = self.token.user.email
        registration_url = f"{self.website}/register/verify/{self.token.token}"

        subject = "Complete Your Registration"
        message = (
            f"Hi {self.token.user.username},\n\n"
            "Thanks for signing up!\n"
            "Click the link below to complete your registration:\n\n"
            f"{registration_url}\n\n"
            "If you didn’t request this, ignore the message.\n"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )