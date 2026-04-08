from django.conf import settings
from django.db import models
from django.utils.timezone import now


class RegistrationToken(models.Model):
    """
    Represent a registration verification token for a user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registration_tokens",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="registration_tokens",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        help_text="Hashed registration token.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        default=now,
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "created_at"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["token_hash"]),
        ]

    @property
    def is_expired(self) -> bool:
        """
        Return whether the registration token has expired.
        """
        return now() >= self.expires_at

    @property
    def is_used(self) -> bool:
        """
        Return whether the registration token has been used.
        """
        return self.used_at is not None

    @property
    def is_valid(self) -> bool:
        """
        Return whether the token is still valid.
        """
        return not self.is_used and not self.is_expired

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
            f"Registration token for {self.user.email} "
            f"on {self.website}"
        )
    
class RegistrationConfirmationLog(models.Model):
    """
    Log registration confirmation attempts.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registration_confirmation_logs",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="registration_confirmation_logs",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        blank=True,
    )
    confirmed_at = models.DateTimeField(
        auto_now_add=True,
    )
    success = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = ["-confirmed_at"]
        indexes = [
            models.Index(fields=["user", "website", "confirmed_at"]),
            models.Index(fields=["success", "confirmed_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the confirmation log.
        """
        status = "success" if self.success else "failure"
        return (
            f"Registration confirmation for {self.user.email} "
            f"({status})"
        )