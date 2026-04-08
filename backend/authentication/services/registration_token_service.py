from datetime import timedelta
from django.utils import timezone

import requests
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now

from authentication.models.registration_token import RegistrationToken
from authentication.models.otp_code import OTPCode
from authentication.services.auth_notification_bridge_service import (
    AuthNotificationBridgeService,
)
from authentication.services.token_service import TokenService
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)
from authentication.services.otp_service import OTPService
from authentication.services.token_service import TokenService
from core.urls.frontend_url import get_frontend_link

class RegistrationTokenService:
    """
    Manage registration token lifecycle for a user and website.
    """

    TOKEN_VALIDITY_HOURS = 24
    OTP_EXPIRY_MINUTES = 10
    VERIFY_PATH = "/auth/register/confirm"

    def __init__(self, user, website):
        """
        Initialize the registration token service.

        Args:
            user: User instance.
            website: Website instance.
        """
        if website is None:
            raise ValueError(
                "Website context is required for registration token service."
            )

        self.user = user
        self.website = website

    @transaction.atomic
    def create_token(self) -> tuple[RegistrationToken, str]:
        """
        Create a registration token and return the raw token once.

        Returns:
            Tuple of:
                - RegistrationToken instance
                - raw token string
        """
        RegistrationToken.objects.filter(
            user=self.user,
            website=self.website,
            used_at__isnull=True,
        ).delete()

        raw_token, token_hash = TokenService.generate_hashed_token()
        
        token = RegistrationToken.objects.create(
            user=self.user,
            website=self.website,
            token_hash=token_hash,
            expires_at=now() + timedelta(hours=self.TOKEN_VALIDITY_HOURS),
        )
        AccountAccessPolicyService.validate_auth_access(
            user=self.user,
            website=self.website,
        )

        # AuthNotificationBridgeService.send_registration_verification_notification(
        #     user=self.user,
        #     website=self.website,
        #     verification_link=verification_link,
        #     raw_token=raw_token,
        #     expiry_minutes=service.OTP_EXPIRY_MINUTES,
        # )

        return token, raw_token

    def validate_token(self, raw_token: str) -> RegistrationToken:
        """
        Validate a registration token.

        Args:
            raw_token: Raw token string.

        Returns:
            RegistrationToken instance.

        Raises:
            ValidationError: If invalid, used, or expired.
        """
        token_hash = TokenService.hash_value(raw_token)

        try:
            token = RegistrationToken.objects.get(
                user=self.user,
                website=self.website,
                token_hash=token_hash,
                used_at__isnull=True,
            )
        except RegistrationToken.DoesNotExist as exc:
            raise ValidationError(
                "Invalid or used registration token."
            ) from exc

        if token.is_expired:
            raise ValidationError("Registration token has expired.")

        return token

    @transaction.atomic
    def mark_token_used(self, raw_token: str) -> None:
        """
        Mark a registration token as used.

        Args:
            raw_token: Raw token string.
        """
        token = self.validate_token(raw_token)
        token.used_at = now()
        token.save(update_fields=["used_at"])

    @transaction.atomic
    def confirm_registration(
        self,
        *,
        raw_token: str,
        otp_code: str,
        otp_service,
    ) -> bool:
        """
        Confirm registration using both token and OTP.

        Args:
            raw_token: Raw registration token.
            otp_code: OTP code.
            otp_service: OTP service instance.

        Returns:
            True if successful.
        """
        self.validate_token(raw_token)
        otp_service.validate_otp(otp_code)

        self.mark_token_used(raw_token)
        otp_service.mark_otp_used(otp_code)

        return True

    @staticmethod
    def verify_captcha(captcha_token: str) -> None:
        """
        Validate reCAPTCHA token from frontend.

        Args:
            captcha_token: CAPTCHA response token.

        Raises:
            ValidationError: If CAPTCHA is invalid.
        """
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={
                "secret": settings.RECAPTCHA_SECRET_KEY,
                "response": captcha_token,
            },
            timeout=5,
        )
        result = response.json()

        if not result.get("success"):
            raise ValidationError("Invalid CAPTCHA.")

    @staticmethod
    def log_confirmation_attempt(
        *,
        user,
        website,
        request,
        success: bool,
    ) -> None:
        """
        Log a registration confirmation attempt.

        Args:
            user: User instance.
            website: Website instance.
            request: HTTP request object.
            success: Whether confirmation succeeded.
        """
        from authentication.models.registration_token import (
            RegistrationConfirmationLog,
        )

        RegistrationConfirmationLog.objects.create(
            user=user,
            website=website,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            success=success,
        )


    @staticmethod
    def hash_token_value(raw_token: str) -> str:
        """
        Has a raw registration token.
        """
        return TokenService.hash_value(raw_token)
    
    def _build_verification_link(self, raw_token: str) -> str:
        """
        Build the frontend verification link.
        """
        return get_frontend_link(
            website=self.website,
            path=self.VERIFY_PATH,
            query_params={"token": raw_token},
        )


    @transaction.atomic
    def create_verification_bundle(
        self,
    ) -> tuple[RegistrationToken, str, str, str]:
        """
        Create registration token + OTP + frontend link.

        Returns:
            Tuple of:
                - RegistrationToken instance
                - raw registration token
                - raw OTP code
                - verification link
        """
        token, raw_token = self.create_token()

        otp_service = OTPService(
            user=self.user,
            website=self.website,
        )
        _otp_obj, raw_otp = otp_service.create_otp(
            purpose=OTPCode.Purpose.REGISTRATION,
            expiry_minutes=self.OTP_EXPIRY_MINUTES,
        )

        verification_link = self._build_verification_link(raw_token)

        return token, raw_token, raw_otp, verification_link

    
    @classmethod
    def request_registration_verification(
        cls,
        *,
        user,
        website,
    ) -> dict:
        """
        Create registration verification artifacts and notify user.
        """
        service = cls(user=user, website=website)
        token, _raw_token, raw_otp, verification_link = (
            service.create_verification_bundle()
        )

        AuthNotificationBridgeService.send_registration_verification_notification(
            user=user,
            website=website,
            verification_link=verification_link,
            # otp_code=raw_otp,
            raw_token=_raw_token,
            expiry_minutes=service.OTP_EXPIRY_MINUTES,
        )

        return {
            "success": True,
            "token_id": token.pk,
        }
    
    @classmethod
    def resend_registration_verification(
        cls,
        *,
        email: str,
        website,
    ) -> dict:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user = User.objects.filter(
            email=email,
            website=website,
            is_active=False,
        ).first()

        if user is None:
            return {
                "success": True,
                "message": "If the account exists, verification instructions were sent.",
            }

        cls.request_registration_verification(
            user=user,
            website=website,
        )

        return {
            "success": True,
            "message": "If the account exists, verification instructions were sent.",
        }