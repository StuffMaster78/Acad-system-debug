from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountDeletionRequest(models.Model):
    """
    Represent a user request to delete or deactivate an account, including
    access, revocation, undo window, and retention lifecycle.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        SCHEDULED = "scheduled", "Scheduled"
        RETAINED = "retained", "Retained"
        CANCELLED = "cancelled", "Cancelled"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"
        PURGED = "purged", "Purged"

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="account_deletion_requests",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_deletion_requests",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    rejected_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    scheduled_deletion_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    retained_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the retained-deleted window ends.",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    purged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When data was permanently purged.",
    )
    undo_token_hash = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        unique=True,
    )
    undo_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    access_revoked_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    reason = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_deletion_at"]),
            models.Index(fields=["status", "retained_until"]),
            models.Index(fields=["user", "website", "status"]),
        ]

    @property
    def is_undo_token_valid(self) -> bool:
        """
        Return whether the undo token is still valid.
        """
        return bool(
            self.undo_token_hash
            and self.undo_token_expires_at
            and timezone.now() < self.undo_token_expires_at
        )
    @property
    def blocks_auth_access(self) -> bool:
        """
        Return whether this deletion request should block account access.
        """
        return self.status in {
            self.Status.SCHEDULED,
            self.Status.RETAINED,
            self.Status.COMPLETED,
        }

    @property
    def is_retention_expired(self) -> bool:
        return bool(
            self.retained_until
            and timezone.now() >= self.retained_until
        )

    def __str__(self) -> str:
        """
        Return a human-readable representation of the deletion request.
        """
        return (
            f"Deletion request for {self.user} "
            f"({self.status})"
        )