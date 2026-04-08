from django.conf import settings
from django.db import models
from django.utils import timezone


class MagicLink(models.Model):
    """
    Represent a single-use, expirable magic link for passwordless login.

    This model stores only the hashed token value. The raw token should
    be generated in the service layer, sent to the user, and never
    persisted directly in the database.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="magic_links",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="magic_links",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="SHA-256 hash of the raw magic-link token.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the magic link was created.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_magic_links",
        help_text="Optional actor who generated the magic link.",
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when the magic link becomes invalid.",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the magic link was used.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which the magic link was requested.",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent from which the magic link was requested.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Magic Link"
        verbose_name_plural = "Magic Links"
        indexes = [
            models.Index(fields=["user", "website", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the magic link.
        """
        return (
            f"Magic link for user_id={self.user.pk}, "
            f"website_id={self.website.pk}"
        )

    @property
    def is_used(self) -> bool:
        """
        Return whether this magic link has already been used.
        """
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        """
        Return whether this magic link has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Return whether this magic link is still valid.

        A magic link is valid if it has not been used and has not
        expired.
        """
        return (
            self.used_at is None
            and timezone.now() < self.expires_at
        )

    def mark_as_used(self) -> None:
        """
        Mark this magic link as used.
        """
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])