from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from core.models.timestamped_model import TimeStampedModel
from special_orders.constants import (
    SpecialOrderQuoteLineType,
    SpecialOrderQuoteStatus,
)


class SpecialOrderQuote(TimeStampedModel):
    """
    Negotiable quote for a special order.

    Exists only for QUOTED pricing mode.
    """

    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        related_name="special_order_quotes",
    )

    special_order = models.OneToOneField(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="quote",
    )

    status = models.CharField(
        max_length=50,
        choices=SpecialOrderQuoteStatus.CHOICES,
        default=SpecialOrderQuoteStatus.DRAFT,
    )

    currency = models.CharField(max_length=10, default="USD")

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    expires_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_special_order_quotes",
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["website", "status"]),
            models.Index(fields=["website", "expires_at"]),
        ]

    def __str__(self) -> str:
        return f"Quote({self.id})"

    if TYPE_CHECKING:
        id: int
        website_id: int
        special_order_id: int


class SpecialOrderQuoteLine(TimeStampedModel):
    """
    Line item within a quote.
    """

    quote = models.ForeignKey(
        "special_orders.SpecialOrderQuote",
        on_delete=models.CASCADE,
        related_name="lines",
    )

    line_type = models.CharField(
        max_length=50,
        choices=SpecialOrderQuoteLineType.CHOICES,
    )

    description = models.CharField(max_length=255)

    quantity = models.PositiveIntegerField(default=1)

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        ordering = ("id",)

    def __str__(self) -> str:
        return f"QuoteLine({self.pk})"