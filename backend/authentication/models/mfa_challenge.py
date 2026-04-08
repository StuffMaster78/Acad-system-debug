from django.conf import settings
from django.db import models
from django.utils import timezone


class MFAChallenge(models.Model):
    """
    Represent a single MFA verification challenge.

    This model stores a one-time MFA challenge issued to a user for a
    specific device. Raw challenge codes must never be stored directly.
    Only hashed values should be persisted.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mfa_challenges",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="mfa_challenges",
    )
    device = models.ForeignKey(
        "authentication.MFADevice",
        on_delete=models.CASCADE,
        related_name="challenges",
    )
    code_hash = models.CharField(
        max_length=255,
        help_text="SHA-256 hash of the issued MFA challenge code.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when this challenge becomes invalid.",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when this challenge was successfully used.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which the challenge was initiated.",
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="User agent from which the challenge was initiated.",
    )
    attempt_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of attempts made against this challenge.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "MFA Challenge"
        verbose_name_plural = "MFA Challenges"
        indexes = [
            models.Index(fields=["user", "website", "created_at"]),
            models.Index(fields=["device", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the MFA challenge.
        """
        return (
            f"MFA challenge for {self.user} "
            f"via device '{self.device.name}'"
        )

    @property
    def is_used(self) -> bool:
        """
        Return whether this challenge has already been used.
        """
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        """
        Return whether this challenge has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Return whether this challenge is still valid.
        """
        return not self.is_used and not self.is_expired

    def mark_as_used(self) -> None:
        """
        Mark the challenge as used.
        """
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])

    def increment_attempt_count(self) -> None:
        """
        Increment the number of challenge verification attempts.
        """
        self.attempt_count += 1
        self.save(update_fields=["attempt_count"])