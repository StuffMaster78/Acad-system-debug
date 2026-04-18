from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderDisputeEventType(models.TextChoices):
    """
    Represent immutable dispute event types.
    """

    OPENED = "opened", "Opened"
    REVIEW_STARTED = "review_started", "Review Started"
    ESCALATED = "escalated", "Escalated"
    COMMENT_ADDED = "comment_added", "Comment Added"
    WRITER_NOTIFIED = "writer_notified", "Writer Notified"
    CLIENT_NOTIFIED = "client_notified", "Client Notified"
    DEADLINE_EXTENDED = "deadline_extended", "Deadline Extended"
    WRITER_REASSIGNED = "writer_reassigned", "Writer Reassigned"
    RESOLVED = "resolved", "Resolved"
    CLOSED = "closed", "Closed"
    CANCELLED = "cancelled", "Cancelled"


class OrderDisputeEvent(models.Model):
    """
    Record immutable business events for order disputes.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_dispute_events",
        help_text="Tenant website that owns this dispute event.",
    )
    dispute = models.ForeignKey(
        "orders.OrderDispute",
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Dispute this event belongs to.",
    )
    event_type = models.CharField(
        max_length=32,
        choices=OrderDisputeEventType,
        help_text="Type of dispute business event.",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_dispute_events",
        null=True,
        blank=True,
        help_text="Actor associated with the event.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured event metadata payload.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the event occurred.",
    )

    class Meta:
        """
        Configure ordering and indexes for dispute events.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "dispute"]),
            models.Index(fields=["dispute", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable dispute event description.

        Returns:
            str:
                Human readable dispute event representation.
        """
        dispute_pk = self.dispute.pk if self.dispute is not None else None
        return f"OrderDisputeEvent dispute={dispute_pk}"

    def clean(self) -> None:
        """
        Validate dispute event invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.dispute is not None and self.website is not None:
            if self.website.pk != self.dispute.website.pk:
                raise ValidationError(
                    "Dispute event website must match dispute website."
                )

        if self.actor is not None and self.website is not None:
            actor_website_id = getattr(self.actor, "website_id", None)
            if (
                actor_website_id is not None
                and actor_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Dispute event actor website must match dispute "
                    "website."
                )