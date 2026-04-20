"""
Composite quote models for the order_pricing_core app.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.db import models


class CompositePricingQuote(models.Model):
    """
    Parent quote that groups multiple component quotes into one
    client-facing pricing session.
    """

    session_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="composite_pricing_quotes",
    )
    currency = models.CharField(max_length=10, default="USD")
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_final = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_composite_pricing_quotes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "order_pricing_core_composite_pricing_quote"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Composite quote {self.session_id}"


class CompositePricingQuoteItem(models.Model):
    """
    One priced component inside a composite pricing quote.
    """

    composite_quote = models.ForeignKey(
        CompositePricingQuote,
        on_delete=models.CASCADE,
        related_name="items",
    )
    pricing_quote = models.ForeignKey(
        "order_pricing_core.PricingQuote",
        on_delete=models.PROTECT,
        related_name="composite_items",
    )
    service = models.ForeignKey(
        "order_pricing_core.ServiceCatalogItem",
        on_delete=models.PROTECT,
        related_name="composite_quote_items",
    )
    component_label = models.CharField(
        max_length=255,
        blank=True,
    )
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_pricing_core_composite_pricing_quote_item"
        ordering = ("sort_order", "id")
        unique_together = ("composite_quote", "pricing_quote")

    def __str__(self) -> str:
        return f"{self.composite_quote.pk} -> {self.service.name}"