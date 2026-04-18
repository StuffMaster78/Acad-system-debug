from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderAdjustmentEventType
from websites.models.websites import Website


class OrderAdjustmentEvent(models.Model):
    """
    Record immutable business events for adjustment requests.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_adjustment_events",
        help_text="Tenant website that owns this event.",
    )
    adjustment_request = models.ForeignKey(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="events",
        help_text="Adjustment request this event belongs to.",
    )
    proposal = models.ForeignKey(
        "orders.OrderAdjustmentProposal",
        on_delete=models.SET_NULL,
        related_name="events",
        null=True,
        blank=True,
        help_text="Related proposal for the event, if applicable.",
    )
    event_type = models.CharField(
        max_length=64,
        choices=OrderAdjustmentEventType.choices,
        help_text="Type of business event.",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_adjustment_events",
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
        Configure ordering and indexes for adjustment events.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "adjustment_request"]),
            models.Index(fields=["adjustment_request", "event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable event description.

        Returns:
            str:
                Human readable event representation.
        """
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderAdjustmentEvent request={request_pk} "
            f"type={self.event_type}"
        )

    def clean(self) -> None:
        """
        Validate event invariants.

        Raises:
            ValidationError:
                Raised when website or proposal linkage is invalid.
        """
        if (
            self.adjustment_request is not None
            and self.website is not None
            and self.website.pk != self.adjustment_request.website.pk
        ):
            raise ValidationError(
                "Event website must match adjustment website."
            )

        if self.proposal is not None:
            if self.adjustment_request is None:
                raise ValidationError(
                    "Proposal cannot be set without a request."
                )

            if self.proposal.adjustment_request is None:
                raise ValidationError(
                    "Event proposal must belong to a request."
                )

            if (
                self.proposal.adjustment_request.pk
                != self.adjustment_request.pk
            ):
                raise ValidationError(
                    "Event proposal must belong to the same request."
                )