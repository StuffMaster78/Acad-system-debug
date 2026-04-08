from django.conf import settings
from django.db import models
from django.utils import timezone


class ImpersonationToken(models.Model):
    """
    Represent a temporary token that allows an authorized user to
    impersonate another user.

    Raw impersonation tokens must never be stored directly. Only the
    hashed token value should be persisted.
    """

    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="issued_impersonation_tokens",
        on_delete=models.CASCADE,
    )
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="received_impersonation_tokens",
        on_delete=models.CASCADE,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="impersonation_tokens",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="SHA-256 hash of the raw impersonation token.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the impersonation token was used.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Impersonation Token"
        verbose_name_plural = "Impersonation Tokens"
        indexes = [
            models.Index(fields=["admin_user", "website", "created_at"]),
            models.Index(fields=["target_user", "website", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the impersonation
        token.
        """
        return (
            f"Impersonation token from {self.admin_user} "
            f"to {self.target_user}"
        )

    @property
    def is_used(self) -> bool:
        """
        Return whether this impersonation token has already been used.
        """
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        """
        Return whether this impersonation token has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Return whether this impersonation token is still valid.
        """
        return not self.is_used and not self.is_expired

    def mark_as_used(self) -> None:
        """
        Mark this impersonation token as used.
        """
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])