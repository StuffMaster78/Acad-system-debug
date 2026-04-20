"""
Pricing snapshot models for the order_pricing_core app.

These models store frozen pricing data created from finalized quotes.
"""

from __future__ import annotations

from decimal import Decimal

from django.db import models


class PricingSnapshot(models.Model):
    """
    Stores a frozen pricing record for a finalized quote.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="order_pricing_snapshots",
    )
    service = models.ForeignKey(
        "order_pricing_core.ServiceCatalogItem",
        on_delete=models.PROTECT,
        related_name="pricing_snapshots",
    )
    quote = models.OneToOneField(
        "order_pricing_core.PricingQuote",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="snapshot",
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )
    currency = models.CharField(max_length=10, default="USD")
    input_data = models.JSONField(default=dict, blank=True)
    breakdown = models.JSONField(default=list, blank=True)
    related_object_type = models.CharField(max_length=100, blank=True)
    related_object_id = models.CharField(max_length=64, blank=True)
    created_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_order_pricing_snapshots",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_pricing_snapshot"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"Snapshot {self.pk} | {self.final_price}"


class PricingSnapshotLine(models.Model):
    """
    Stores frozen snapshot breakdown lines.
    """

    snapshot = models.ForeignKey(
        PricingSnapshot,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    line_type = models.CharField(max_length=20)
    code = models.CharField(max_length=100, blank=True)
    label = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    metadata = models.JSONField(default=dict, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        """
        Model metadata.
        """

        db_table = "order_pricing_core_pricing_snapshot_line"
        ordering = ("sort_order", "id")

    def __str__(self) -> str:
        """
        Return a readable representation.
        """
        return f"{self.label} | {self.amount}"