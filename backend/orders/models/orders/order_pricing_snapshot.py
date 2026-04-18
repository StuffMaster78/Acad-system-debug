from __future__ import annotations

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from websites.models.websites import Website


class OrderPricingSnapshot(models.Model):
    """
    Persist a pricing snapshot for an order.

    This records how current commercial totals were derived at a
    specific point in time.
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="order_pricing_snapshots",
        help_text="Tenant website that owns this pricing snapshot.",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="pricing_snapshots",
        help_text="Order this pricing snapshot belongs to.",
    )
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the current active snapshot.",
    )
    currency = models.CharField(
        max_length=8,
        default="",
        help_text="Currency used for this pricing snapshot.",
    )
    pricing_policy_version = models.CharField(
        max_length=64,
        blank=True,
        help_text="Version of the pricing policy used.",
    )
    subtotal_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Subtotal before discounts and adjustments.",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount amount applied at snapshot time.",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final total amount at snapshot time.",
    )
    writer_compensation_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Writer compensation at snapshot time.",
    )
    pricing_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed pricing breakdown payload.",
    )
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="created_order_pricing_snapshots",
        null=True,
        blank=True,
        help_text="Actor who generated the pricing snapshot.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the snapshot was created.",
    )

    class Meta:
        """
        Configure ordering, indexes, and constraints.
        """

        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["order", "is_current"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(subtotal_amount__gte=0),
                name="orders_price_snap_subtotal_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(discount_amount__gte=0),
                name="orders_price_snap_discount_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(total_amount__gte=0),
                name="orders_price_snap_total_gte_zero",
            ),
            models.CheckConstraint(
                condition=models.Q(
                    writer_compensation_amount__gte=0
                ),
                name="orders_price_snap_writer_comp_gte_zero",
            ),
        ]

    def __str__(self) -> str:
        """
        Return a readable pricing snapshot description.

        Returns:
            str:
                Human readable snapshot representation.
        """
        order_pk = self.order.pk if self.order is not None else None
        return (
            f"OrderPricingSnapshot order={order_pk} "
            f"current={self.is_current}"
        )

    def clean(self) -> None:
        """
        Validate pricing snapshot invariants.

        Raises:
            ValidationError:
                Raised when website linkage is invalid.
        """
        if self.order is not None and self.website is not None:
            if self.website.pk != self.order.website.pk:
                raise ValidationError(
                    "Pricing snapshot website must match order website."
                )