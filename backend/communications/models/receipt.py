from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationReadReceipt(models.Model):
    """
    Tracks when a user read a message.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_read_receipts",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="read_receipts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="communication_read_receipts",
    )

    read_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "user"]),
            models.Index(fields=["website", "message", "user"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_read_receipt_per_message_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.id} read message {self.message.pk}"