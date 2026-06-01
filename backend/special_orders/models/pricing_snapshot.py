from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel


class SpecialOrderPricingSnapshot(TimeStampedModel):
    """
    Immutable pricing snapshot at the moment a quote is accepted.

    This ensures:
        - Future config changes do not affect past orders
        - Ledger + funding calculations are stable
        - Auditing is accurate
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_pricing_snapshots",
    )

    special_order = models.OneToOneField(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="pricing_snapshot",
    )

    currency = models.CharField(max_length=10)

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    raw_data = models.JSONField(
        default=dict,
        help_text="Full serialized snapshot of quote lines and pricing.",
    )

    class Meta: # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"PricingSnapshot({self.id})"

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int