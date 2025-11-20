import secrets
import random
from django.utils import timezone
from django.core.exceptions import ValidationError
from authentication.models.password_reset import PasswordResetRequest


class PasswordResetService:
    """
    Handles hybrid password reset (link + OTP) with multitenancy support.
    """

    TOKEN_EXPIRATION_HOURS = 1

    def __init__(self, user, website):
        """
        Args:
            user (User): The user requesting the password reset.
            website (Website): The tenant context.
        """
        self.user = user
        self.website = website

    def _generate_otp(self):
        """
        Generates a 6-digit numeric OTP code.

        Returns:
            str: A 6-digit OTP as string.
        """
        return f"{random.randint(100000, 999999)}"

    def generate_reset_token(self):
        """
        Creates a new password reset request.

        Returns:
            PasswordResetRequest: The created reset request.
        """
        token = secrets.token_urlsafe(32)
        otp_code = self._generate_otp()
        return PasswordResetRequest.objects.create(
            user=self.user,
            website=self.website,
            token=token,
            otp_code=otp_code
        )

    def validate_token(self, token):
        """
        Validates a token for this user and website.

        Args:
            token (str): The token to validate.

        Returns:
            PasswordResetRequest: Validated request.

        Raises:
            ValidationError: If invalid or expired.
        """
        try:
            request = PasswordResetRequest.objects.get(
                user=self.user,
                website=self.website,
                token=token,
                is_used=False
            )
        except PasswordResetRequest.DoesNotExist:
            raise ValidationError("Invalid or used reset token.")

        if request.is_expired():
            raise ValidationError("Reset token has expired.")

        return request

    def validate_otp(self, otp_code):
        """
        Validates an OTP for this user and website.

        Args:
            otp_code (str): The OTP to validate.

        Returns:
            PasswordResetRequest: Validated request.

        Raises:
            ValidationError: If invalid or expired.
        """
        try:
            request = PasswordResetRequest.objects.get(
                user=self.user,
                website=self.website,
                otp_code=otp_code,
                is_used=False
            )
        except PasswordResetRequest.DoesNotExist:
            raise ValidationError("Invalid or used OTP.")

        if request.is_expired():
            raise ValidationError("OTP has expired.")

        return request

    def mark_token_used(self, token):
        """
        Marks the given token as used.

        Args:
            token (str): Token to mark as used.
        """
        PasswordResetRequest.objects.filter(
            user=self.user,
            website=self.website,
            token=token
        ).update(is_used=True, created_at=timezone.now())

    def mark_otp_used(self, otp_code):
        """
        Marks the given OTP as used.

        Args:
            otp_code (str): OTP to mark as used.
        """
        PasswordResetRequest.objects.filter(
            user=self.user,
            website=self.website,
            otp_code=otp_code
        ).update(is_used=True, created_at=timezone.now())