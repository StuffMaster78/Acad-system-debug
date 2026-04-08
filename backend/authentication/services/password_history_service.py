"""
Password history service.

Manage password history storage and validation to prevent recent
password reuse.
"""

from django.core.exceptions import ValidationError
from django.db import transaction

from authentication.models.password_security import PasswordHistory


class PasswordHistoryService:
    """
    Manage password history for a user on a website.
    """

    DEFAULT_HISTORY_DEPTH = 5

    def __init__(self, user, website):
        """
        Initialize the password history service.

        Args:
            user: User instance.
            website: Website instance.

        Raises:
            ValueError: If website is not provided.
        """
        if website is None:
            raise ValueError(
                "Website context is required for password history."
            )

        self.user = user
        self.website = website

    @transaction.atomic
    def save_current_password_to_history(
        self,
        *,
        history_depth: int | None = None,
    ) -> PasswordHistory:
        """
        Save the user's current password hash to password history.

        Args:
            history_depth: Number of recent password hashes to retain.

        Returns:
            Created PasswordHistory instance.
        """
        history_depth = history_depth or self.DEFAULT_HISTORY_DEPTH

        history_entry = PasswordHistory.objects.create(
            user=self.user,
            website=self.website,
            password_hash=self.user.password,
        )

        stale_entries = list(
            PasswordHistory.objects.filter(
                user=self.user,
                website=self.website,
            ).order_by("-created_at")[history_depth:]
        )

        if stale_entries:
            PasswordHistory.objects.filter(
                pk__in=[entry.pk for entry in stale_entries]
            ).delete()

        return history_entry

    def is_password_reused(
        self,
        *,
        raw_password: str,
        check_last_n: int | None = None,
    ) -> bool:
        """
        Determine whether a password matches recent password history.

        Args:
            raw_password: Plain-text password to test.
            check_last_n: Number of recent password hashes to check.

        Returns:
            True if password was recently used, otherwise False.
        """
        from django.contrib.auth.hashers import check_password

        check_last_n = check_last_n or self.DEFAULT_HISTORY_DEPTH

        recent_passwords = PasswordHistory.objects.filter(
            user=self.user,
            website=self.website,
        ).order_by("-created_at")[:check_last_n]

        for entry in recent_passwords:
            if check_password(raw_password, entry.password_hash):
                return True

        return False

    def validate_password_not_reused(
        self,
        *,
        raw_password: str,
        check_last_n: int | None = None,
    ) -> None:
        """
        Validate that the password was not recently used.

        Args:
            raw_password: Plain-text password to validate.
            check_last_n: Number of recent password hashes to check.

        Raises:
            ValidationError: If the password was recently used.
        """
        if self.is_password_reused(
            raw_password=raw_password,
            check_last_n=check_last_n,
        ):
            raise ValidationError(
                "This password was recently used. Please choose a "
                "different password."
            )

    def get_history_count(self) -> int:
        """
        Return the number of stored password history entries.

        Returns:
            Number of history rows.
        """
        return PasswordHistory.objects.filter(
            user=self.user,
            website=self.website,
        ).count()

    @transaction.atomic
    def clear_history(self) -> int:
        """
        Delete all password history entries for the user and website.

        Returns:
            Number of deleted rows.
        """
        deleted_count, _ = PasswordHistory.objects.filter(
            user=self.user,
            website=self.website,
        ).delete()

        return deleted_count