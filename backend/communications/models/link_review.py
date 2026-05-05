from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class CommunicationLinkReviewStatus:
    """
    Link review lifecycle states.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BLOCKED = "blocked"

    CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (BLOCKED, "Blocked"),
    )


class CommunicationLinkReview(models.Model):
    """
    Review record for links shared inside messages.

    Links should remain suspicious until admin or superadmin approves them.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="communication_link_reviews",
    )
    thread = models.ForeignKey(
        "communications.CommunicationThread",
        on_delete=models.CASCADE,
        related_name="link_reviews",
    )
    message = models.ForeignKey(
        "communications.CommunicationMessage",
        on_delete=models.CASCADE,
        related_name="link_reviews",
    )

    url = models.TextField()
    domain = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=CommunicationLinkReviewStatus.CHOICES,
        default=CommunicationLinkReviewStatus.PENDING,
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="submitted_communication_links",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_communication_links",
    )

    reviewed_at = models.DateTimeField(null=True, blank=True)
    decision_note = models.TextField(blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "thread", "status"]),
            models.Index(fields=["website", "message"]),
            models.Index(fields=["website", "domain"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.domain or self.url} [{self.status}]"