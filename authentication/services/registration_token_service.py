import uuid
import requests
from django.conf import settings
from datetime import timedelta

from django.utils.timezone import now
from django.core.exceptions import ValidationError
from authentication.mailers import send_registration_email

from authentication.models.register import RegistrationToken


class RegistrationTokenService:
    """
    Manages registration token lifecycle with multitenancy support.
    """

    TOKEN_VALIDITY_HOURS = 24

    def __init__(self, user, website):
        """
        Args:
            user (User): The user to create the token for.
            website (Website): Tenant context for multitenancy.
        """
        self.user = user
        self.website = website

    def create_token(self):
        """
        Generates and saves a registration token.

        Returns:
            RegistrationToken: The created token instance.
        """
        expires_at = now() + timedelta(hours=self.TOKEN_VALIDITY_HOURS)
        token = RegistrationToken.objects.create(
            user=self.user,
            website=self.website,
            expires_at=expires_at
        )

        send_registration_email(self.user, token, self.website)

        return token

    def validate_token(self, token_str):
        """
        Validates a registration token.

        Args:
            token_str (str): UUID string of the token.

        Returns:
            RegistrationToken: The validated token.

        Raises:
            ValidationError: If token is invalid, used, or expired.
        """
        try:
            token = RegistrationToken.objects.get(
                user=self.user,
                website=self.website,
                token=uuid.UUID(token_str),
                is_used=False
            )
        except (RegistrationToken.DoesNotExist, ValueError):
            raise ValidationError("Invalid or used registration token.")

        if token.is_expired():
            raise ValidationError("Registration token has expired.")

        return token

    def mark_token_used(self, token_str):
        """
        Marks a registration token as used.

        Args:
            token_str (str): UUID string of the token.
        """
        RegistrationToken.objects.filter(
            user=self.user,
            website=self.website,
            token=token_str
        ).update(is_used=True, created_at=timezone.now())


    def confirm_registration(self, token, otp_code, otp_service):
        """
        Confirms registration using both a token and an OTP.

        Args:
            token (UUID): The registration token.
            otp_code (str): The OTP sent to the user.
            otp_service (OTPService): Instance to validate OTP.

        Returns:
            bool: True if successful.

        Raises:
            ValidationError: If validation fails.
        """
        self.validate_token(token)
        otp_service.validate_otp(otp_code)
        self.mark_token_used(token)
        otp_service.mark_otp_used(otp_code)
        return True

    def verify_captcha(captcha_token):
        """
        Validates reCAPTCHA token from frontend.
        """
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': captcha_token
            }
        )
        result = response.json()
        if not result.get('success'):
            raise ValidationError('Invalid CAPTCHA.')
        
    def log_confirmation_attempt(user, website, request, success):
        from authentication.models.register import RegistrationConfirmationLog
        RegistrationConfirmationLog.objects.create(
            user=user,
            website=website,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success
        )
