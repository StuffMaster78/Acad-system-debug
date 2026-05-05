from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from communications.constants import CommunicationParticipantRole


class CommunicationParticipant(models.Model):
    """
    Explicit user membership in a communication thread.

    This model decides who can view, send, upload, or observe inside
    a thread. Services should enforce the actual access rules.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_participants",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="participants",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="communication_participations",
    )

    role = models.CharField(
        max_length=30,
        choices=CommunicationParticipantRole.CHOICES,
    )

    can_view = models.BooleanField(default=True)
    can_send = models.BooleanField(default=True)
    can_upload = models.BooleanField(default=True)
    is_observer = models.BooleanField(default=False)

    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_communication_participants",
    )

    joined_at = models.DateTimeField(default=timezone.now)
    removed_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "user"]),
            models.Index(fields=["website", "user", "can_view"]),
            models.Index(fields=["website", "role"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["thread", "user"],
                name="unique_user_per_communication_thread",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.pk} in thread {self.thread.pk}"