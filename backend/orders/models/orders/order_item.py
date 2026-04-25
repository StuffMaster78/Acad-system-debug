"""
Order item model for composite and multi-component orders.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models

from orders.models.orders.enums import OrderScopeUnitType


class OrderItem(models.Model):
    """
    Represents one commercial component within an order.

    This model is intentionally dumb. It stores frozen item-level
    commercial truth copied from pricing snapshots and leaves business
    logic to services.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_items",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="items",
    )
    pricing_snapshot = models.ForeignKey(
        "order_pricing_core.PricingSnapshot",
        on_delete=models.PROTECT,
        related_name="order_items",
        null=True,
        blank=True,
        help_text=(
            "Frozen pricing snapshot used to create this order item."
        ),
    )
    unit_type = models.CharField(
        max_length=32,
        choices=OrderScopeUnitType.choices,
        default=OrderScopeUnitType.OTHER,
        help_text=(
            "Unit type for this item (e.g. Slides, Diagrams, Design, Pages)."
        ),
    )
    item_kind = models.CharField(
        max_length=32,
        blank=True,
        default="scope_unit",
        help_text=(
            "Item kind for this item (e.g. Base, Revision, Scope Unit, Extra Service)."
        ),
    )
    service_family = models.CharField(
        max_length=32,
        help_text="Pricing service family for this item.",
    )
    service_code = models.CharField(
        max_length=100,
        help_text="Pricing service code for this item.",
    )
    topic = models.CharField(
        max_length=255,
        blank=True,
        help_text="Readable item topic for admin and client display.",
    )

    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Commercial quantity for this item.",
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Subtotal before item-level discounts.",
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Discount amount applied to this item.",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Final frozen total for this item.",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            "Frozen item-specific metadata copied from pricing input "
            "or snapshot context."
        ),
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Display and processing order within the parent order.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "orders_order_item"
        ordering = ("sort_order", "id")
        indexes = [
            models.Index(fields=["website", "order"]),
            models.Index(fields=["website", "service_family"]),
            models.Index(fields=["website", "service_code"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        label = self.topic or self.service_code
        return f"OrderItem #{self.pk} for Order #{self.order.pk}: {label}"