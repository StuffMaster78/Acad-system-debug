from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from ledger.constants import ReconciliationStatus
from ledger.models.reconciliation_record import ReconciliationRecord


class LedgerReconciliationService:
    """
    Tracks and updates reconciliation records.
    """

    @staticmethod
    @transaction.atomic
    def create_record(
        *,
        website,
        expected_amount: Decimal,
        currency: str = "KES",
        journal_entry=None,
        user=None,
        actual_amount: Decimal | None = None,
        reference: str = "",
        external_reference: str = "",
        payment_intent_reference: str = "",
        source_app: str = "",
        source_model: str = "",
        source_object_id: str = "",
        metadata: dict | None = None,
    ) -> ReconciliationRecord:
        variance_amount = Decimal("0.00")
        matched_amount = Decimal("0.00")

        if actual_amount is not None:
            matched_amount = min(expected_amount, actual_amount)
            variance_amount = expected_amount - actual_amount

        return ReconciliationRecord.objects.create(
            website=website,
            journal_entry=journal_entry,
            user=user,
            currency=currency,
            expected_amount=expected_amount,
            actual_amount=actual_amount,
            matched_amount=matched_amount,
            variance_amount=variance_amount,
            reference=reference,
            external_reference=external_reference,
            payment_intent_reference=payment_intent_reference,
            source_app=source_app,
            source_model=source_model,
            source_object_id=source_object_id,
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def reconcile(
        *,
        record: ReconciliationRecord,
        actual_amount: Decimal,
    ) -> ReconciliationRecord:
        record.actual_amount = actual_amount

        if actual_amount == record.expected_amount:
            record.mark_matched(actual_amount)
        elif actual_amount > Decimal("0.00"):
            record.mark_partially_matched(min(record.expected_amount, actual_amount))
        else:
            record.mark_mismatched("No actual amount matched.")

        record.save()
        return record

    @staticmethod
    @transaction.atomic
    def mark_mismatched(
        *,
        record: ReconciliationRecord,
        reason: str,
    ) -> ReconciliationRecord:
        record.mark_mismatched(reason)
        record.save(update_fields=["status", "mismatch_reason", "variance_amount", "updated_at"])
        return record

    @staticmethod
    @transaction.atomic
    def mark_resolved(
        *,
        record: ReconciliationRecord,
        resolved_by=None,
    ) -> ReconciliationRecord:
        record.mark_resolved(resolved_by=resolved_by)
        record.save(
            update_fields=[
                "status",
                "resolved_by",
                "resolved_at",
                "reconciled_at",
                "updated_at",
            ]
        )
        return record