from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import OrderInterestStatus, OrderInterestType
from websites.models.websites import Website


class OrderInterest(models.Model):
    """
    Represent writer staffing intent for an order.

    This model captures pool bids, requests to take an order, and
    preferred writer invitation responses. It is not the same thing as
    an active assignment.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_interests",
        help_text="Tenant website that owns this interest record.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="interests",
        help_text="Order the writer expressed interest in.",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_interests",
        help_text="Writer who expressed interest or received invitation.",
    )
    interest_type = models.CharField(
        max_length=32,
        choices=OrderInterestType.choices,
        help_text="Type of staffing intent or invitation.",
    )
    status = models.CharField(
        max_length=24,
        choices=OrderInterestStatus.choices,
        default=OrderInterestStatus.PENDING,
        help_text="Lifecycle state of this interest record.",
    )
    message = models.TextField(
        blank=True,
        help_text="Optional writer or staff message attached to interest.",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="reviewed_order_interests",
        null=True,
        blank=True,
        help_text="Actor who reviewed the interest record.",
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the interest was reviewed.",
    )
    withdrawn_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the interest was withdrawn.",
    )
    last_preferred_writer_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last preferred writer reminder was sent.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured metadata for staffing workflow.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the interest record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the interest record was last updated.",
    )

    class Meta:
        """
        Configure ordering, indexes, and uniqueness rules.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["writer", "status"]),
            models.Index(fields=["interest_type", "status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "writer", "interest_type"],
                condition=models.Q(
                    status__in=[
                        OrderInterestStatus.PENDING,
                        OrderInterestStatus.ACCEPTED,
                    ]
                ),
                name="orders_interest_one_open_per_type",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable interest description.

        Returns:
            str:
                Human readable interest representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        writer_pk = self.writer.pk if self.writer is not None else None
        return f"OrderInterest order={order_pk} writer={writer_pk}"

    def clean(self) -> None:
        """
        Validate interest invariants.

        Raises:
            ValidationError:
                Raised when linked objects cross tenants.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Interest website must match order website."
                )

        if self.writer is not None and self.website is not None:
            writer_website_id = getattr(self.writer, "website_id", None)
            if (
                writer_website_id is not None
                and writer_website_id != self.website.pk
            ):
                raise ValidationError(
                    "Writer website must match interest website."
                )