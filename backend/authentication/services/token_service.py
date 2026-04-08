import hashlib
import random
import secrets
from datetime import timedelta
from typing import Final

from django.utils import timezone


class TokenService:
    """
    Provide shared helpers for generating and hashing authentication
    credentials.

    This service centralizes low-level token operations used across
    authentication workflows such as password reset, magic links,
    and email verification.

    Responsibilities:
        - generate secure URL-safe tokens
        - generate numeric OTP codes
        - hash token-like values before persistence
        - calculate expiry timestamps
    """

    DEFAULT_TOKEN_BYTES: Final[int] = 32
    DEFAULT_OTP_LENGTH: Final[int] = 6

    @staticmethod
    def hash_value(raw_value: str) -> str:
        """
        Return a SHA-256 hash for a raw token-like value.

        Args:
            raw_value: Raw token, OTP, or verification value.

        Returns:
            A hexadecimal SHA-256 hash string.
        """
        return hashlib.sha256(
            raw_value.encode("utf-8")
        ).hexdigest()

    @classmethod
    def generate_token(
        cls,
        *,
        nbytes: int | None = None,
    ) -> str:
        """
        Generate a secure URL-safe token.

        Args:
            nbytes: Number of random bytes to use. If omitted,
                the default size is used.

        Returns:
            A secure URL-safe token string.
        """
        token_bytes = nbytes or cls.DEFAULT_TOKEN_BYTES
        return secrets.token_urlsafe(token_bytes)

    @classmethod
    def generate_otp(
        cls,
        *,
        length: int | None = None,
    ) -> str:
        """
        Generate a numeric OTP code.

        Args:
            length: Number of digits in the OTP. If omitted,
                the default length is used.

        Returns:
            A zero-padded numeric OTP string.

        Raises:
            ValueError: If the requested OTP length is less than 1.
        """
        otp_length = length or cls.DEFAULT_OTP_LENGTH

        if otp_length < 1:
            raise ValueError(
                "OTP length must be greater than zero."
            )

        lower_bound = 10 ** (otp_length - 1)
        upper_bound = (10 ** otp_length) - 1

        if otp_length == 1:
            lower_bound = 0

        return str(
            random.randint(lower_bound, upper_bound)
        ).zfill(otp_length)

    @staticmethod
    def build_expiry(
        *,
        minutes: int | None = None,
        hours: int | None = None,
        days: int | None = None,
    ):
        """
        Build an expiry timestamp relative to the current time.

        Args:
            minutes: Minutes to add to the current time.
            hours: Hours to add to the current time.
            days: Days to add to the current time.

        Returns:
            A timezone-aware expiry timestamp.

        Raises:
            ValueError: If all duration values are missing or invalid.
        """
        delta = timedelta(
            minutes=minutes or 0,
            hours=hours or 0,
            days=days or 0,
        )

        if delta.total_seconds() <= 0:
            raise ValueError(
                "Expiry duration must be greater than zero."
            )

        return timezone.now() + delta

    @classmethod
    def generate_hashed_token(
        cls,
        *,
        nbytes: int | None = None,
    ) -> tuple[str, str]:
        """
        Generate a raw token and its hash.

        Args:
            nbytes: Number of random bytes to use.

        Returns:
            A tuple of:
                - raw token
                - hashed token
        """
        raw_token = cls.generate_token(nbytes=nbytes)
        return raw_token, cls.hash_value(raw_token)

    @classmethod
    def generate_hashed_otp(
        cls,
        *,
        length: int | None = None,
    ) -> tuple[str, str]:
        """
        Generate a raw OTP and its hash.

        Args:
            length: Number of digits in the OTP.

        Returns:
            A tuple of:
                - raw OTP
                - hashed OTP
        """
        raw_otp = cls.generate_otp(length=length)
        return raw_otp, cls.hash_value(raw_otp)