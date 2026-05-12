from __future__ import annotations

from decimal import Decimal

from django.db import models

from websites.models.websites import Website


class PayoutReconciliationReport(models.Model):
    """
    Audit report comparing:
        ledger vs payout vs clearance vs wallet mirror
    """

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="payout_reconciliation_reports",
    )

    payout_batch = models.ForeignKey(
        "writer_compensation.PayoutBatch",
        on_delete=models.PROTECT,
        related_name="reconciliation_reports",
    )

    total_ledger_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_payout_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    total_cleared_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    mismatch_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    status = models.CharField(
        max_length=32,
        default="PENDING",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(default=dict, blank=True)