from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class PasswordResetRequest(models.Model):
    """
    Represent a one-time password reset request for a user.

    This model stores hashed password reset credentials for both:
        1. Link-based reset via a reset token
        2. OTP-based reset via a one-time code

    Raw tokens and OTP codes must never be stored in the database.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="password_reset_requests",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_requests",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="SHA-256 hash of the raw reset token.",
    )
    otp_hash = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        help_text="SHA-256 hash of the raw OTP code.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the reset request was created.",
    )
    expires_at = models.DateTimeField(
        help_text="Timestamp when the reset request becomes invalid.",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the reset request was used.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Password Reset Request"
        verbose_name_plural = "Password Reset Requests"
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=Q(used_at__isnull=True),
                name="unique_active_password_reset_request_per_user",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the reset request.
        """
        return f"Password reset request for user_id={self.user.pk}"

    @property
    def is_used(self) -> bool:
        """
        Return whether this reset request has been used.
        """
        return self.used_at is not None

    @property
    def is_expired(self) -> bool:
        """
        Return whether this reset request has expired.
        """
        return timezone.now() >= self.expires_at

    @property
    def is_valid(self) -> bool:
        """
        Return whether this reset request is valid.

        A request is valid if it has not been used and has not expired.
        """
        return not self.is_used and not self.is_expired

    def mark_as_used(self) -> None:
        """
        Mark this reset request as used.

        This method sets the `used_at` timestamp if it has not already
        been set.
        """
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])