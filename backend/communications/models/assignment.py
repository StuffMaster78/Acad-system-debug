from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationThreadAssignment(models.Model):
    """
    Support or staff ownership record for a communication thread.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_thread_assignments",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="assignment_records",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assigned_communication_threads",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_assignments_made",
    )

    is_active = models.BooleanField(default=True)

    assigned_at = models.DateTimeField(default=timezone.now)
    unassigned_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "is_active"]),
            models.Index(fields=["website", "assigned_to", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["thread", "assigned_to", "is_active"],
                name="unique_active_assignment_per_thread_user",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.assigned_to.pk} assigned to {self.thread.pk}"