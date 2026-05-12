from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from writer_compensation.models.payout_reconciliation_report import (
    PayoutReconciliationReport,
)


class ReconciliationService:
    """
    Deterministic payout reconciliation engine.

    Core principle:
        Ledger = expected truth
        Clearance = external truth
        Payout = system intent execution

    This service only compares and reports differences.
    """

    STATUS_OPEN = "OPEN"
    STATUS_OK = "OK"

    # -----------------------------
    # REPORT GENERATION
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def create_report(
        *,
        website: Any,
        batch: Any,
        ledger_total: Decimal,
        payout_total: Decimal,
        cleared_total: Decimal,
    ) -> PayoutReconciliationReport:
        """
        Create or update reconciliation report for a payout batch.

        This is idempotent:
        repeated runs overwrite the same logical report instead of duplicating it.
        """

        ledger_total = ledger_total or Decimal("0.00")
        payout_total = payout_total or Decimal("0.00")
        cleared_total = cleared_total or Decimal("0.00")

        # -----------------------------
        # CORE RECONCILIATION LOGIC
        # -----------------------------
        mismatch_amount = payout_total - cleared_total

        is_balanced = mismatch_amount == Decimal("0.00")

        status = (
            ReconciliationService.STATUS_OK
            if is_balanced
            else ReconciliationService.STATUS_OPEN
        )

        # -----------------------------
        # IDENTITY (prevents duplicate reports per batch)
        # -----------------------------
        report, _created = PayoutReconciliationReport.objects.get_or_create(
            website=website,
            payout_batch=batch,
            defaults={
                "total_ledger_amount": ledger_total,
                "total_payout_amount": payout_total,
                "total_cleared_amount": cleared_total,
                "mismatch_amount": mismatch_amount,
                "status": status,
            },
        )

        if not _created:
            report.total_ledger_amount = ledger_total
            report.total_payout_amount = payout_total
            report.total_cleared_amount = cleared_total
            report.mismatch_amount = mismatch_amount
            report.status = status
            report.save(
                update_fields=[
                    "total_ledger_amount",
                    "total_payout_amount",
                    "total_cleared_amount",
                    "mismatch_amount",
                    "status",
                ]
            )

        return report