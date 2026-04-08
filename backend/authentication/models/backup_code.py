from django.conf import settings
from django.db import models
from django.utils import timezone


class BackupCode(models.Model):
    """
    Represent a single-use backup code for multi-factor authentication.

    Backup codes are used as a fallback authentication method when
    other MFA mechanisms are unavailable.

    Raw codes must never be stored. Only hashed values are persisted.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="backup_codes",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="backup_codes",
    )
    code_hash = models.CharField(
        max_length=255,
        help_text="SHA-256 hash of the backup code.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the code was used.",
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website"]),
        ]
        verbose_name = "Backup Code"
        verbose_name_plural = "Backup Codes"

    def __str__(self) -> str:
        """
        Return a human-readable representation of the backup code.
        """
        status = "used" if self.is_used else "unused"
        return f"Backup code for {self.user} ({status})"

    @property
    def is_used(self) -> bool:
        """
        Return whether this backup code has already been used.
        """
        return self.used_at is not None

    def mark_as_used(self) -> None:
        """
        Mark the backup code as used.
        """
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])