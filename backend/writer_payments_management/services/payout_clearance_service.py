from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_payments_management.models.payout_record_models import PayoutRecord
from writer_payments_management.models.payout_clearance_models import PayoutClearance


class PayoutClearanceService:
    """
    External payout finalization layer.

    RULES:
        1. PayoutRecord = intent
        2. Clearance = external truth proof
        3. Must be idempotent (webhook-safe)
        4. Must never double-apply financial state
    """

    STATUS_PROCESSING = "PROCESSING"
    STATUS_PAID = "PAID"
    STATUS_FAILED = "FAILED"

    # -----------------------------
    # PROCESSING STATE
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def mark_as_processing(
        *,
        payout_record: PayoutRecord,
        reference_code: str,
    ) -> PayoutRecord:
        """
        Move payout into external processing state.
        Safe for retries (idempotent update).
        """

        if payout_record.status == PayoutClearanceService.STATUS_PAID:
            return payout_record  # already finalized

        payout_record.status = PayoutClearanceService.STATUS_PROCESSING
        payout_record.external_reference = reference_code
        payout_record.updated_at = timezone.now()
        payout_record.save(update_fields=["status", "external_reference", "updated_at"])

        return payout_record

    # -----------------------------
    # SUCCESS STATE
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def mark_as_success(
        *,
        payout_record: PayoutRecord,
        external_transaction_id: str,
        amount_paid: Decimal,
        metadata: dict[str, Any] | None = None,
    ) -> PayoutClearance:
        """
        Confirm successful external payout execution.

        Idempotent:
            - If already cleared, returns existing clearance
        """

        existing = PayoutClearance.objects.filter(
            payout_record=payout_record,
            external_transaction_id=external_transaction_id,
            status=PayoutClearanceService.STATUS_PAID,
        ).first()

        if existing:
            return existing

        payout_record.status = PayoutClearanceService.STATUS_PAID
        payout_record.paid_at = timezone.now()
        payout_record.save(update_fields=["status", "paid_at"])

        return PayoutClearance.objects.create(
            payout_record=payout_record,
            external_transaction_id=external_transaction_id,
            amount_paid=amount_paid,
            status=PayoutClearanceService.STATUS_PAID,
            metadata=metadata or {},
            created_at=timezone.now(),
        )

    # -----------------------------
    # FAILURE STATE
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def mark_as_failed(
        *,
        payout_record: PayoutRecord,
        failure_reason: str,
        external_transaction_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> PayoutClearance:
        """
        Mark payout as failed and persist failure proof.

        This is safe for retries and webhook replays.
        """

        if payout_record.status == PayoutClearanceService.STATUS_PAID:
            raise ValueError("Cannot fail a completed payout")

        payout_record.status = PayoutClearanceService.STATUS_FAILED
        payout_record.updated_at = timezone.now()
        payout_record.save(update_fields=["status", "updated_at"])

        return PayoutClearance.objects.create(
            payout_record=payout_record,
            external_transaction_id=external_transaction_id or "",
            amount_paid=Decimal("0.00"),
            status=PayoutClearanceService.STATUS_FAILED,
            metadata={
                "reason": failure_reason,
                **(metadata or {}),
            },
            created_at=timezone.now(),
        )