from __future__ import annotations

from decimal import Decimal

from django.db import models

from writer_compensation.models.compensation_event import (
    CompensationEvent,
)
from writer_compensation.models.settlement_period import (
    SettlementPeriod,
)


class SettlementItem(models.Model):
    """
    Connects matured financial events
    into a settlement period.
    """

    settlement_period = models.ForeignKey(
        SettlementPeriod,
        on_delete=models.CASCADE,
        related_name="items",
    )

    financial_event = models.ForeignKey(
        CompensationEvent,
        on_delete=models.CASCADE,
        related_name="settlement_items",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    included_at = models.DateTimeField(
        auto_now_add=True,
    )

    notes = models.TextField(
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        unique_together = [
            (
                "settlement_period",
                "financial_event",
            ),
        ]
        ordering = [
            "-included_at",
        ]

    def __str__(self) -> str:
        return (
            f"{self.settlement_period.pk} | "
            f"{self.financial_event.pk}"
        )

    @property
    def is_positive(self) -> bool:
        return self.amount >= Decimal("0.00")