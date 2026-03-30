from __future__ import annotations

from django.db import models


class ProfileReminderType(models.TextChoices):
    """Supported phone reminder types."""
    MISSING_PHONE = "missing_phone", "Missing Phone"
    MISSING_DISPLAY_NAME = "missing_display_name", "Missing Display Name"
    INCOMPLETE_PROFILE = "incomplete_profile", "Incomplete Profile"


class ProfileReminderStatus(models.TextChoices):
    """Status of reminder attempt."""
    SENT = "sent", "Sent"
    SKIPPED = "skipped", "Skipped"
    FAILED = "failed", "Failed"


class ProfileReminder(models.Model):
    """Stores reminder history for profile completeness nudges."""
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="profile_reminders",
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="profile_reminders",
    )
    reminder_type = models.CharField(
        max_length=50,
        choices=ProfileReminderType.choices,
        db_index=True,
    )
    channel = models.CharField(
        max_length=30,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=ProfileReminderStatus.choices,
        default=ProfileReminderStatus.SENT,
        db_index=True,
    )
    metadata = models.JSONField(default=dict, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["user", "reminder_type", "sent_at"]),
            models.Index(fields=["website", "reminder_type", "sent_at"]),
        ]

    def __str__(self) -> str:
        return (
            f"ProfileReminder<user={self.user.pk}, "
            f"type={self.reminder_type}, status={self.status}>"
        )