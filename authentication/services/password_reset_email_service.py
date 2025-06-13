from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.utils.html import strip_tags


class PasswordResetEmailService:
    """
    Sends hybrid password reset emails (OTP + link) to users.

    Attributes:
        user (User): The user receiving the reset email.
        website (Website): Tenant context.
        token (str): Password reset token.
        otp_code (str): 6-digit OTP code.
    """

    def __init__(self, user, website, token, otp_code):
        self.user = user
        self.website = website
        self.token = token
        self.otp_code = otp_code

    def build_reset_link(self):
        """
        Constructs the frontend password reset link using the token.

        Returns:
            str: Full URL to reset page.
        """
        base_url = self.website.reset_url or settings.DEFAULT_RESET_URL
        return f"{base_url}?token={self.token}"

    def send_email(self):
        """
        Sends the hybrid reset email.
        """
        subject = "Reset your password securely"
        reset_link = self.build_reset_link()

        html_message = f"""
            <p>Hi {self.user.first_name or self.user.username},</p>
            <p>You requested to reset your password.</p>
            <p><strong>Your OTP code:</strong> {self.otp_code}</p>
            <p>
                Or you can click this secure link to reset:
                <a href="{reset_link}">{reset_link}</a>
            </p>
            <p>
                If you did not request this, please ignore this email.
            </p>
        """

        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [self.user.email],
            html_message=html_message
        )