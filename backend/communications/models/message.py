from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from communications.constants import (
    CommunicationMessageStatus,
    CommunicationMessageType,
)


class CommunicationMessage(models.Model):
    """
    A message inside a communication thread.

    Business rules such as moderation, notification, and read receipt creation
    should live in services, not in this model.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_messages",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_communication_messages",
    )

    message_type = models.CharField(
        max_length=30,
        choices=CommunicationMessageType.CHOICES,
        default=CommunicationMessageType.USER,
    )
    status = models.CharField(
        max_length=30,
        choices=CommunicationMessageStatus.CHOICES,
        default=CommunicationMessageStatus.ACTIVE,
    )

    body = models.TextField(blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="replies",
    )

    is_internal = models.BooleanField(default=False)
    is_system_generated = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)

    edited_at = models.DateTimeField(null=True, blank=True)
    hidden_at = models.DateTimeField(null=True, blank=True)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "created_at"]),
            models.Index(fields=["website", "sender", "created_at"]),
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "is_internal"]),
        ]
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"Message #{self.pk} in thread {self.thread.pk}"