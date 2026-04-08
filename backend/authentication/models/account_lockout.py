from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountLockout(models.Model):
    """
    Represent an account lockout event due to suspicious activity,
    automated security policy, or administrative action.
    """

    class LockType(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        ADMIN = "admin", "Admin"
        RISK = "risk", "Risk-Based"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_lockouts",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_lockouts",
    )
    reason = models.TextField(
        help_text="Reason the user account was locked.",
    )
    lock_type = models.CharField(
        max_length=20,
        choices=LockType.choices,
        default=LockType.AUTOMATIC,
        help_text="Type of account lockout.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_account_lockouts",
        help_text="Admin user who created the lockout, if applicable.",
    )
    locked_at = models.DateTimeField(
        auto_now_add=True,
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the lockout ends."
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the lockout expires, if temporary.",
    )
    unlocked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="The time when the account is unlocked."
    )
    cleared_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the lockout was cleared.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this lockout is currently active.",
    )
    is_locked = models.BooleanField(
        default=False,
        help_text="Whether the account is locked or not."
    )

    class Meta:
        ordering = ["-locked_at"]
        verbose_name = "Account Lockout"
        verbose_name_plural = "Account Lockouts"
        indexes = [
            models.Index(fields=["user", "website", "is_active"]),
            models.Index(fields=["website", "locked_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the lockout.
        """
        return (
            f"Lockout for {self.user} on {self.website} "
            f"(active={self.is_active})"
        )

    @property
    def is_expired(self) -> bool:
        """
        Return whether this lockout has expired.
        """
        if self.expires_at is None:
            return False

        return timezone.now() >= self.expires_at

    @property
    def is_effective(self) -> bool:
        """
        Return whether this lockout should still be enforced.
        """
        return self.is_active and not self.is_expired

    def clear(self) -> None:
        """
        Clear this lockout.
        """
        if self.is_active:
            self.is_active = False
            self.cleared_at = timezone.now()
            self.save(update_fields=["is_active", "cleared_at"])