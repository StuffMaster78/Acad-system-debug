from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class TipSettlementSnapshot(models.Model):
    """
    Immutable financial settlement snapshot for a tip.

    This model preserves the exact monetary outcome of a tip
    settlement at the moment settlement occurred.

    Historical settlement truth must never depend on mutable policy
    configuration.
    """

    tip = models.OneToOneField(
        "tips.Tip",
        on_delete=models.CASCADE,
        related_name="settlement_snapshot",
    )

    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    writer_tip_share = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    platform_tip_share = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
    )

    currency = models.CharField(
        max_length=3,
        default="USD",
        editable=False,
    )

    settled_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ["-settled_at"]
        indexes = [
            models.Index(
                fields=[
                    "settled_at",
                ],
                name="tip_settlement_date_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(gross_amount__gte=0),
                name="tip_snapshot_gross_positive",
            ),
            models.CheckConstraint(
                check=models.Q(writer_tip_share__gte=0),
                name="tip_snapshot_writer_positive",
            ),
            models.CheckConstraint(
                check=models.Q(platform_tip_share__gte=0),
                name="tip_snapshot_platform_positive",
            ),
        ]

    def __str__(self) -> str:
        return (
            f"Settlement Snapshot "
            f"for Tip {self.tip.pk}"
        )