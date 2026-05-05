from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationMessageEdit(models.Model):
    """
    Immutable edit history for a message.

    Never silently overwrite communication evidence.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_message_edits",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="message_edit_records",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="edit_records",
    )

    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_message_edits",
    )

    previous_body = models.TextField()
    new_body = models.TextField()

    edited_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "edited_at"]),
            models.Index(fields=["website", "message", "edited_at"]),
            models.Index(fields=["website", "edited_by", "edited_at"]),
        ]

    def __str__(self) -> str:
        return f"Edit for message {self.message.pk}"