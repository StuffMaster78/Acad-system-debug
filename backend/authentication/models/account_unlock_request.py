from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountUnlockRequest(models.Model):
    """
    Represents an unlock-account verification request.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_unlock_requests",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_unlock_requests",
    )
    token_hash = models.CharField(
        max_length=255,
        unique=True,
    )
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "website", "created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    @property
    def is_valid(self) -> bool:
        return (
            self.used_at is None
            and timezone.now() < self.expires_at
        )

    def mark_as_used(self) -> None:
        if self.used_at is None:
            self.used_at = timezone.now()
            self.save(update_fields=["used_at"])