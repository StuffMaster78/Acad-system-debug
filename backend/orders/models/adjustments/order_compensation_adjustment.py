from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from orders.enums import (
    OrderCompensationAdjustmentStatus,
    OrderCompensationAdjustmentType,
)
from websites.models.websites import Website


class OrderCompensationAdjustment(models.Model):
    """
    Represent downstream writer compensation impact from a funded
    adjustment.

    This model does not credit writer wallet directly. It records the
    compensation delta to be recognized later by payout workflow.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_compensation_adjustments",
        help_text="Tenant website that owns this compensation record.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="compensation_adjustments",
        help_text="Order this compensation adjustment belongs to.",
    )
    adjustment_request = models.ForeignKey(
        "orders.OrderAdjustmentRequest",
        on_delete=models.CASCADE,
        related_name="compensation_adjustments",
        help_text="Adjustment request that created this compensation.",
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="order_compensation_adjustments",
        null=True,
        blank=True,
        help_text="Writer affected by the compensation delta.",
    )
    compensation_type = models.CharField(
        max_length=32,
        choices=OrderCompensationAdjustmentType.choices,
        help_text="Type of compensation delta.",
    )
    status = models.CharField(
        max_length=24,
        choices=OrderCompensationAdjustmentStatus.choices,
        default=OrderCompensationAdjustmentStatus.PENDING,
        help_text="Current compensation adjustment status.",
    )
    quantity_delta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Quantity delta associated with compensation.",
    )
    amount_delta = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Monetary delta for writer compensation.",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured compensation metadata.",
    )
    recognized_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the compensation was recognized.",
    )
    reversed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the compensation was reversed.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the compensation record was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the compensation record was last updated.",
    )

    class Meta:
        """
        Configure ordering, indexes, and constraints.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["order", "status"]),
            models.Index(fields=["writer", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_delta__gte=0),
                name="orders_comp_adj_amount_delta_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable compensation description.

        Returns:
            str:
                Human readable compensation representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        request_pk = (
            self.adjustment_request.pk
            if self.adjustment_request is not None
            else None
        )
        return (
            f"OrderCompensationAdjustment order={order_pk} "
            f"request={request_pk}"
        )

    def clean(self) -> None:
        """
        Validate compensation invariants.

        Raises:
            ValidationError:
                Raised when linked objects cross tenants.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Compensation website must match order website."
                )

        if (
            self.adjustment_request is not None
            and self.website is not None
            and self.website.pk != self.adjustment_request.website.pk
        ):
            raise ValidationError(
                "Compensation website must match adjustment website."
            )

        if (
            self.order is not None
            and self.adjustment_request is not None
            and self.adjustment_request.order is not None
            and self.adjustment_request.order.pk != self.order.pk
        ):
            raise ValidationError(
                "Compensation order must match adjustment order."
            )