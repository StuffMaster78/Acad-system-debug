from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.mfa_challenge import MFAChallenge
from authentication.models.mfa_device import MFADevice
from authentication.services.token_service import TokenService
from authentication.services.account_access_policy_service import (
    AccountAccessPolicyService,
)

class MFAChallengeService:
    """
    Handle MFA challenge generation, validation, and consumption.
    """

    DEFAULT_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5
    DEFAULT_OTP_LENGTH = 6

    @staticmethod
    @transaction.atomic
    def create_challenge(
        *,
        user,
        website,
        device: MFADevice,
        ip_address: str | None = None,
        user_agent: str | None = None,
        expiry_minutes: int = DEFAULT_EXPIRY_MINUTES,
    ) -> tuple[MFAChallenge, str]:
        """
        Create a new MFA challenge for a device.

        Existing active challenges for the same device are removed
        before the new one is created.

        Args:
            user: User instance.
            website: Website instance.
            device: MFA device instance.
            ip_address: Optional source IP address.
            user_agent: Optional source user agent.
            expiry_minutes: Challenge expiry in minutes.

        Returns:
            A tuple of:
                - MFAChallenge instance
                - raw OTP code
        """
        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )
        MFAChallenge.objects.filter(
            user=user,
            website=website,
            device=device,
            used_at__isnull=True,
        ).delete()

        raw_code, code_hash = TokenService.generate_hashed_otp(
            length=MFAChallengeService.DEFAULT_OTP_LENGTH,
        )

        challenge = MFAChallenge.objects.create(
            user=user,
            website=website,
            device=device,
            code_hash=code_hash,
            expires_at=TokenService.build_expiry(
                minutes=expiry_minutes,
            ),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return challenge, raw_code

    @staticmethod
    def get_valid_challenge(
        *,
        user,
        website,
        device: MFADevice,
        raw_code: str,
    ) -> MFAChallenge:
        """
        Retrieve and validate an MFA challenge by raw code.

        Args:
            user: User instance.
            website: Website instance.
            device: MFA device instance.
            raw_code: Raw challenge code provided by the user.

        Returns:
            Valid MFAChallenge instance.

        Raises:
            ValidationError: If the challenge is invalid, expired,
                already used, or exceeded maximum attempts.
        """
        code_hash = TokenService.hash_value(raw_code)

        try:
            challenge = MFAChallenge.objects.get(
                user=user,
                website=website,
                device=device,
                code_hash=code_hash,
                used_at__isnull=True,
            )
        except MFAChallenge.DoesNotExist as exc:
            raise ValidationError("Invalid MFA challenge code.") from exc

        if not challenge.is_valid:
            raise ValidationError("MFA challenge has expired.")

        if challenge.attempt_count >= MFAChallengeService.MAX_ATTEMPTS:
            raise ValidationError("Maximum MFA attempts exceeded.")

        return challenge

    @staticmethod
    @transaction.atomic
    def verify_challenge(
        *,
        user,
        website,
        device: MFADevice,
        raw_code: str,
    ) -> MFAChallenge:
        """
        Verify and consume an MFA challenge.

        Args:
            user: User instance.
            website: Website instance.
            device: MFA device instance.
            raw_code: Raw challenge code provided by the user.

        Returns:
            Consumed MFAChallenge instance.

        Raises:
            ValidationError: If the challenge is invalid.
        """
        AccountAccessPolicyService.validate_auth_access(
            user=user,
            website=website,
        )
        challenge = MFAChallengeService.get_valid_challenge(
            user=user,
            website=website,
            device=device,
            raw_code=raw_code,
        )

        challenge.mark_as_used()
        device.mark_as_used()

        return challenge

    @staticmethod
    @transaction.atomic
    def register_failed_attempt(
        *,
        challenge: MFAChallenge,
    ) -> MFAChallenge:
        """
        Register a failed verification attempt for an MFA challenge.

        Args:
            challenge: MFAChallenge instance.

        Returns:
            Updated MFAChallenge instance.
        """
        challenge.increment_attempt_count()
        return challenge