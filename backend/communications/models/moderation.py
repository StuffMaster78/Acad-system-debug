from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

class CommunicationModerationStatus:
    """
    Moderation flag lifecycle states.
    """

    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

    CHOICES = (
        (OPEN, "Open"),
        (RESOLVED, "Resolved"),
        (DISMISSED, "Dismissed"),
    )


class CommunicationModerationSeverity:
    """
    Severity levels for message moderation flags.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    CHOICES = (
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    )


class CommunicationModerationFlag(models.Model):
    """
    Stores moderation flags raised against a message.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_moderation_flags",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="moderation_flags",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="moderation_flags",
    )
    status = models.CharField(
        max_length=20,
        choices=CommunicationModerationStatus.CHOICES,
        default=CommunicationModerationStatus.OPEN,
    )
    severity = models.CharField(
        max_length=20,
        choices=CommunicationModerationSeverity.CHOICES,
        default=CommunicationModerationSeverity.LOW,
    )

    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_communication_flags",
    )

    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_communication_flags",
    )

    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_note = models.TextField(blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["website", "thread", "status"]),
            models.Index(fields=["website", "message", "status"]),
            models.Index(fields=["website", "severity", "status"]),
            models.Index(fields=["website", "created_at"]),
            models.Index(fields=["website", "resolved_at"]),
        ]

    def __str__(self) -> str:
        return f"Moderation flag #{self.pk}"