from __future__ import annotations

from django.conf import settings
from django.db import models

from class_management.constants import ClassTimelineEventType


class ClassTimelineEvent(models.Model):
    """
    Immutable timeline event for class order history.
    """

    class_order = models.ForeignKey(
        "class_management.ClassOrder",
        on_delete=models.CASCADE,
        related_name="timeline_events",
    )

    event_type = models.CharField(
        max_length=60,
        choices=ClassTimelineEventType.choices,
        db_index=True,
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="class_timeline_events",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["class_order", "created_at"]),
            models.Index(fields=["event_type"]),
        ]