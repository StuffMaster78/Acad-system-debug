from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationAttachment(models.Model):
    """
    Links a managed file to a communication message.

    Actual file storage, signed URLs, deletion policy, and moderation should
    remain in files_management.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_attachments",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="attachments",
    )

    file = models.ForeignKey(
        "files_management.ManagedFile",
        on_delete=models.PROTECT,
        related_name="communication_attachments",
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_communication_attachments",
    )

    is_visible = models.BooleanField(default=True)
    requires_moderation = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread"]),
            models.Index(fields=["website", "message"]),
            models.Index(fields=["website", "uploaded_by"]),
        ]

    def __str__(self) -> str:
        return f"Attachment #{self.pk} for message {self.message.pk}"