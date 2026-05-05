from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationDeliveryReceipt(models.Model):
    """
    Tracks that a message was delivered to a user's inbox or stream.

    This is not device delivery. It means the backend made the message
    available to the recipient.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_delivery_receipts",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="delivery_receipts",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="delivery_receipts",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="communication_delivery_receipts",
    )

    delivered_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "user"]),
            models.Index(fields=["website", "message", "user"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["message", "user"],
                name="unique_delivery_receipt_per_message_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.pk} delivered message {self.message.pk}"