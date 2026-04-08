from django.conf import settings
from django.db import models
from django.utils.timezone import now


class SecureToken(models.Model):
    """
    Store server-side token records securely using hashed token values.
    """

    class Purpose(models.TextChoices):
        API_KEY = "api_key", "API Key"
        REFRESH_TOKEN = "refresh_token", "Refresh Token"
        UNLOCK_ACCOUNT = "unlock_account", "Unlock Account"
        OTHER = "other", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="secure_tokens",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="secure_tokens",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed token value.",
    )
    purpose = models.CharField(
        max_length=50,
        choices=Purpose.choices,
        help_text="Purpose of the token.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        help_text="When this token expires.",
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "purpose"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["token_hash"]),
        ]

    @property
    def is_expired(self) -> bool:
        """
        Return whether the token has expired.
        """
        return now() >= self.expires_at

    @property
    def is_revoked(self) -> bool:
        """
        Return whether the token has been revoked.
        """
        return self.revoked_at is not None

    @property
    def is_used(self) -> bool:
        """
        Return whether the token has been used.
        """
        return self.used_at is not None

    @property
    def is_active(self) -> bool:
        """
        Return whether the token is active and usable.
        """
        return not self.is_revoked and not self.is_expired

    def revoke(self) -> None:
        """
        Revoke the token.
        """
        if self.revoked_at is None:
            self.revoked_at = now()
            self.save(update_fields=["revoked_at"])

    def mark_as_used(self) -> None:
        """
        Mark the token as used.
        """
        if self.used_at is None:
            self.used_at = now()
            self.save(update_fields=["used_at"])

    def __str__(self) -> str:
        """
        Return a human-readable representation of the token record.
        """
        return (
            f"{self.user.email} | {self.purpose} | "
            f"active={self.is_active}"
        )