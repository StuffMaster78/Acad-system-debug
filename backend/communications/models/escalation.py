from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationEscalationStatus:
    """
    Escalation lifecycle states.
    """

    OPEN = "open"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"

    CHOICES = (
        (OPEN, "Open"),
        (RESOLVED, "Resolved"),
        (CANCELLED, "Cancelled"),
    )


class CommunicationEscalation(models.Model):
    """
    Escalation record for a communication thread.

    Used when support needs admin, superadmin, finance, or senior staff
    to intervene.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_escalations",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="escalations",
    )

    status = models.CharField(
        max_length=20,
        choices=CommunicationEscalationStatus.CHOICES,
        default=CommunicationEscalationStatus.OPEN,
    )

    reason = models.TextField()
    resolution_note = models.TextField(blank=True)

    escalated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_escalations_created",
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_escalations_resolved",
    )

    escalated_at = models.DateTimeField(default=timezone.now)
    resolved_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "status"]),
            models.Index(fields=["website", "status", "escalated_at"]),
            models.Index(fields=["website", "escalated_by"]),
        ]

    def __str__(self) -> str:
        return f"Escalation {self.pk} for thread {self.thread.pk}"