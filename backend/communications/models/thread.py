from __future__ import annotations

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from communications.constants import (
    CommunicationThreadKind,
    CommunicationThreadStatus,
)


class CommunicationThread(models.Model):
    """
    Conversation attached to a domain object.

    Examples:
        Order
        ClassOrder
        SpecialOrder
        RevisionRequest
        Dispute
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_threads",
    )

    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="communication_threads",
    )
    target_object_id = models.PositiveBigIntegerField()
    target = GenericForeignKey(
        "target_content_type",
        "target_object_id",
    )

    kind = models.CharField(
        max_length=40,
        choices=CommunicationThreadKind.CHOICES,
    )
    status = models.CharField(
        max_length=20,
        choices=CommunicationThreadStatus.CHOICES,
        default=CommunicationThreadStatus.OPEN,
    )

    subject = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=80, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_communication_threads",
    )

    last_message_at = models.DateTimeField(null=True, blank=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "kind", "status"]),
            models.Index(
                fields=[
                    "website",
                    "target_content_type",
                    "target_object_id",
                ],
            ),
            models.Index(fields=["website", "last_message_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "website",
                    "target_content_type",
                    "target_object_id",
                    "kind",
                ],
                name="unique_thread_per_target_and_kind",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind} thread #{self.pk}"