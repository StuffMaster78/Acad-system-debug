from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderHoldStatus
from websites.models.websites import Website


class OrderHold(models.Model):
    """
    Represent an order hold with frozen time tracking.

    Holds are operational pauses approved by staff. They preserve enough
    timing data to support deadline freeze and resume logic in services.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_holds",
        help_text="Tenant website that owns this hold record.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="holds",
        help_text="Order placed on hold.",
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="requested_order_holds",
        null=True,
        blank=True,
        help_text="Actor who requested the hold.",
    )
    placed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="placed_order_holds",
        null=True,
        blank=True,
        help_text="Staff actor who placed the hold.",
    )
    placed_at = models.DateTimeField(
    null=True,
    blank=True,
    help_text="When the hold was activated.",
    )

    released_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the hold was released.",
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the hold request was cancelled.",
    )

    remaining_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Remaining order time when the hold was activated.",
    )

    internal_notes = models.TextField(
        blank=True,
        help_text="Internal staff notes for the hold workflow.",
    )
    released_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="released_order_holds",
        null=True,
        blank=True,
        help_text="Staff actor who released the hold.",
    )
    status = models.CharField(
        max_length=24,
        choices=OrderHoldStatus.choices,
        default=OrderHoldStatus.PENDING,
        help_text="Lifecycle state of the hold.",
    )
    reason = models.TextField(
        help_text="Reason the order was put on hold.",
    )
    remaining_seconds_snapshot = models.PositiveIntegerField(
        default=0,
        help_text="Remaining deadline seconds captured at hold start.",
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the hold was requested.",
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the hold became active.",
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the hold was released.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metadata for hold workflow.",
    )

    class Meta:
        """
        Configure ordering and indexes for holds.
        """

        ordering = ("-requested_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["status", "requested_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order"],
                condition=models.Q(status=OrderHoldStatus.ACTIVE),
                name="orders_one_active_hold_per_order",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable hold representation.

        Returns:
            str:
                Human readable hold string.
        """
        order_pk = self.order.pk if self.order is not None else None
        return f"OrderHold order={order_pk} status={self.status}"

    def clean(self) -> None:
        """
        Validate hold invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.order.website.pk != self.website.pk:
                raise ValidationError(
                    "Hold website must match order website."
                )