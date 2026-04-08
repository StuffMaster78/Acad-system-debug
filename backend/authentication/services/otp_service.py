from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from authentication.models.otp_code import OTPCode
from authentication.services.token_service import TokenService
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)

class OTPService:
    """
    Handle generation, validation, and consumption of short lived OTPs.
    """

    DEFAULT_EXPIRY_MINUTES = 10
    DEFAULT_MAX_ATTEMPTS = 5

    def __init__(self, user, website):
        if website is None:
            raise ValueError("Website context is required.")

        self.user = user
        self.website = website

    @transaction.atomic
    def create_otp(
        self,
        *,
        purpose: str,
        expiry_minutes: int = DEFAULT_EXPIRY_MINUTES,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> tuple[OTPCode, str]:
        """
        Create a fresh OTP for the given purpose.

        Existing unused OTPs for the same purpose are removed first.
        """
        OTPCode.objects.filter(
            user=self.user,
            website=self.website,
            purpose=purpose,
            used_at__isnull=True,
        ).delete()

        AccountAccessPolicyService.validate_auth_access(
            user=self.user,
            website=self.website,
        )

        raw_code, code_hash = TokenService.generate_hashed_otp()

        otp = OTPCode.objects.create(
            user=self.user,
            website=self.website,
            purpose=purpose,
            code_hash=code_hash,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
            max_attempts=max_attempts,
        )

        return otp, raw_code

    def validate_otp(
        self,
        *,
        purpose: str,
        raw_code: str,
    ) -> OTPCode:
        """
        Validate an OTP without consuming it.
        """
        code_hash = TokenService.hash_value(raw_code)

        otp = OTPCode.objects.filter(
            user=self.user,
            website=self.website,
            purpose=purpose,
            code_hash=code_hash,
            used_at__isnull=True,
        ).order_by("-created_at").first()

        if otp is None:
            self._record_failed_attempt_for_latest(purpose=purpose)
            raise ValidationError("Invalid OTP.")

        if not otp.is_valid:
            raise ValidationError("OTP is expired, used, or locked.")

        return otp

    @transaction.atomic
    def consume_otp(
        self,
        *,
        purpose: str,
        raw_code: str,
    ) -> OTPCode:
        """
        Validate and consume an OTP.
        """
        otp = self.validate_otp(
            purpose=purpose,
            raw_code=raw_code,
        )
        otp.mark_as_used()
        return otp

    def _record_failed_attempt_for_latest(
        self,
        *,
        purpose: str,
    ) -> None:
        otp = OTPCode.objects.filter(
            user=self.user,
            website=self.website,
            purpose=purpose,
            used_at__isnull=True,
        ).order_by("-created_at").first()

        if otp is not None and otp.attempts < otp.max_attempts:
            otp.record_attempt()