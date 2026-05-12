from __future__ import annotations

from decimal import Decimal

from django.db import models

from websites.models.websites import Website


class ExposureLedger(models.Model):
    """
    Tracks financial exposure per writer.

    This is the CONTROL CENTER for:
        - advances
        - unpaid earnings
        - risk caps
        - recoveries
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="exposure_ledgers",
    )

    writer = models.ForeignKey(
        "writer_management.WriterProfile",
        on_delete=models.CASCADE,
        related_name="exposure_ledgers",
    )

    total_earned = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_settled = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_advance_taken = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    recoverable_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    risk_cap_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("30.00"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["writer"]),
        ]
        unique_together = (
            "website",
            "writer",
        )
