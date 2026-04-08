"""
Phone verification service.

Handle phone verification challenge creation and code verification
for a user on a website.
"""

import logging
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from authentication.models.phone_verification import (
    PhoneVerification,
)
from authentication.services.token_service import TokenService


logger = logging.getLogger(__name__)


class PhoneVerificationService:
    """
    Manage phone verification workflows for a user on a website.
    """

    DEFAULT_EXPIRY_MINUTES = 10

    def __init__(self, user, website):
        """
        Initialize the phone verification service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for phone verification."
            )

        self.user = user
        self.website = website

    @transaction.atomic
    def create_verification(
        self,
        *,
        phone_number: str,
    ) -> tuple[PhoneVerification, str]:
        """
        Create a new phone verification challenge.

        Any prior pending verification attempts for the same phone
        number are invalidated before the new one is created.

        Args:
            phone_number: Phone number to verify.

        Returns:
            Tuple of:
                - PhoneVerification instance
                - raw verification code
        """
        self.cancel_pending_verifications(phone_number=phone_number)

        raw_code, code_hash = TokenService.generate_hashed_otp()

        verification = PhoneVerification.objects.create(
            user=self.user,
            website=self.website,
            phone_number=phone_number,
            code_hash=code_hash,
            expires_at=TokenService.build_expiry(
                minutes=self.DEFAULT_EXPIRY_MINUTES,
            ),
        )

        return verification, raw_code

    @transaction.atomic
    def verify_code(
        self,
        *,
        phone_number: str,
        raw_code: str,
    ) -> PhoneVerification:
        """
        Verify a phone verification code.

        Args:
            phone_number: Phone number being verified.
            raw_code: Submitted verification code.

        Returns:
            Verified PhoneVerification instance.

        Raises:
            ValidationError: If no valid verification exists or the
                code is invalid.
        """
        verification = self.get_pending_verification(
            phone_number=phone_number,
        )

        if verification is None:
            raise ValidationError(
                "No pending verification found for this phone number."
            )

        if verification.is_expired:
            raise ValidationError(
                "Verification code has expired. Please request a new code."
            )

        if verification.is_exhausted:
            raise ValidationError(
                "Maximum verification attempts exceeded. "
                "Please request a new code."
            )

        verification.attempts += 1

        submitted_hash = TokenService.hash_value(raw_code)

        if verification.code_hash != submitted_hash:
            verification.save(update_fields=["attempts"])

            remaining_attempts = max(
                0,
                verification.max_attempts - verification.attempts,
            )

            if verification.is_exhausted:
                raise ValidationError(
                    "Maximum verification attempts exceeded. "
                    "Please request a new code."
                )

            raise ValidationError(
                "Invalid verification code. "
                f"{remaining_attempts} attempts remaining."
            )

        verification.is_verified = True
        verification.verified_at = timezone.now()
        verification.save(
            update_fields=[
                "attempts",
                "is_verified",
                "verified_at",
            ],
        )

        self._update_user_phone_number(phone_number=phone_number)

        return verification

    @transaction.atomic
    def cancel_pending_verifications(
        self,
        *,
        phone_number: str,
    ) -> int:
        """
        Invalidate existing pending phone verifications for a phone
        number.

        Args:
            phone_number: Phone number whose pending verifications
                should be invalidated.

        Returns:
            Number of updated verification records.
        """
        return PhoneVerification.objects.filter(
            user=self.user,
            website=self.website,
            phone_number=phone_number,
            is_verified=False,
        ).update(
            expires_at=timezone.now(),
            attempts=models.F("max_attempts"),
        )

    def get_pending_verification(
        self,
        *,
        phone_number: str,
    ) -> Optional[PhoneVerification]:
        """
        Retrieve the most recent pending verification for a phone
        number.

        Args:
            phone_number: Phone number being verified.

        Returns:
            Pending PhoneVerification instance or None.
        """
        return PhoneVerification.objects.filter(
            user=self.user,
            website=self.website,
            phone_number=phone_number,
            is_verified=False,
        ).order_by("-created_at").first()

    def get_verified_phone(self) -> Optional[str]:
        """
        Retrieve the most recently verified phone number for the user.

        Returns:
            Verified phone number or None.
        """
        verified = PhoneVerification.objects.filter(
            user=self.user,
            website=self.website,
            is_verified=True,
        ).order_by("-verified_at").first()

        return verified.phone_number if verified else None

    def _update_user_phone_number(
        self,
        *,
        phone_number: str,
    ) -> None:
        """
        Update the user's phone number if the user model supports it.

        Args:
            phone_number: Verified phone number.
        """
        if hasattr(self.user, "phone_number"):
            self.user.phone_number = phone_number
            self.user.save(update_fields=["phone_number"])