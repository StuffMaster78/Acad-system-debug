from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderTimelineEventType
from websites.models.websites import Website


class OrderTimelineEvent(models.Model):
    """
    Record immutable business timeline events for orders.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_timeline_events",
        help_text="Tenant website that owns this event.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="timeline_events",
        help_text="Order this event belongs to.",
    )
    event_type = models.CharField(
        max_length=64,
        choices=OrderTimelineEventType.choices,
        help_text="Type of business event.",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_timeline_events",
        null=True,
        blank=True,
        help_text="Actor associated with the event.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured event metadata.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the event occurred.",
    )

    class Meta:
        """
        Configure ordering and indexes for timeline events.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable timeline event description.

        Returns:
            str:
                Human readable event representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return (
            f"OrderTimelineEvent order={order_pk} "
            f"type={self.event_type}"
        )

    def clean(self) -> None:
        """
        Validate timeline event invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Timeline event website must match order website."
                )