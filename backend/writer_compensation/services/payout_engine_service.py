from __future__ import annotations
 
from decimal import Decimal
from typing import Any
 
from django.db import transaction
from django.utils import timezone
 
from writer_compensation.enums.compensation_enums import (
    EventStatus,
    PayoutRecordStatus,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    InvalidPayoutItemTransitionError,
    InvalidWindowTransitionError,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.models.payout_record import PayoutRecord
from writer_compensation.services.wallet_sync_service import (
    CompensationWalletSyncService,
)
 
 
class PayoutEngineService:
    """
    Payout intent builder and record state machine.
 
    Rules:
      1. Batch = grouping container (one per window)
      2. Record = payout intent per writer (one per writer per batch)
      3. Never executes money movement
      4. All state transitions are atomic
    """
 
    # ------------------------------------------------------------------
    # Record confirmation
    # ------------------------------------------------------------------
 
    @staticmethod
    @transaction.atomic
    def confirm_record(
        record: PayoutRecord,
        confirmed_by,
    ) -> PayoutRecord:
        """
        PENDING -> CONFIRMED.
        Admin has reviewed this writer's total and agrees it is correct.
        Window must be PROCESSING.
        """
        if record.status != PayoutRecordStatus.PENDING:
            raise InvalidPayoutItemTransitionError(
                f"Record {record.pk} is {record.status}. "
                "Only PENDING records can be confirmed."
            )
        if record.batch.payment_window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING to confirm payout records."
            )
 
        record.status = PayoutRecordStatus.CONFIRMED
        record.confirmed_at = timezone.now()
        record.confirmed_by = confirmed_by
        record.save(update_fields=["status", "confirmed_at", "confirmed_by"])
 
        return record
 
    # ------------------------------------------------------------------
    # Mark paid
    # ------------------------------------------------------------------
 
    @staticmethod
    @transaction.atomic
    def mark_record_paid(
        record: PayoutRecord,
        paid_by,
        notes: str = "",
        method: str = "",
        external_reference: str = "",
    ) -> PayoutRecord:
        """
        CONFIRMED → PAID.

        Admin has paid this writer externally.
        Stamps all linked MATURED CompensationEvents as PAID.
        """
        if record.status != PayoutRecordStatus.CONFIRMED:
            raise InvalidPayoutItemTransitionError(
                f"Record {record.pk} is {record.status}. "
                "Confirm before marking paid."
            )

        now = timezone.now()
        record.status = PayoutRecordStatus.PAID
        record.paid_at = now
        record.paid_by = paid_by
        if notes:
            record.notes = notes
        if method:
            record.method = method
        if external_reference:
            record.external_reference = external_reference
        record.save(update_fields=["status", "paid_at", "paid_by", "notes", "method", "external_reference"])

        CompensationWalletSyncService.settle_payout_record(
            record=record,
            actor=paid_by,
        )
 
        # Stamp underlying events as PAID.
        CompensationEvent.objects.filter(
            writer=record.writer,
            payment_window=record.batch.payment_window,   
            status=EventStatus.MATURED,
        ).update(status=EventStatus.PAID)
 
        from writer_compensation.signals import payout_record_paid
        payout_record_paid.send(sender=PayoutRecord, record=record)
 
        return record
 
    # ------------------------------------------------------------------
    # Hold
    # ------------------------------------------------------------------
 
    @staticmethod
    @transaction.atomic
    def hold_record(
        record: PayoutRecord,
        reason: str,
        held_by,
    ) -> PayoutRecord:
        """
        PENDING | CONFIRMED -> HELD.
        Other records in the same batch are completely unaffected.
        """
        if record.status == PayoutRecordStatus.PAID:
            raise InvalidPayoutItemTransitionError(
                f"Record {record.pk} is already PAID and cannot be held."
            )
 
        record.status = PayoutRecordStatus.HELD
        record.hold_reason = reason
        record.save(update_fields=["status", "hold_reason"])
 
        # Generic notification — hold_reason is NEVER shown to the writer.
        from writer_compensation.signals import payout_record_held
        payout_record_held.send(sender=PayoutRecord, record=record)
 
        return record
 
    # ------------------------------------------------------------------
    # Release hold
    # ------------------------------------------------------------------
 
    @staticmethod
    @transaction.atomic
    def release_held_record(
        record: PayoutRecord,
        released_by,
    ) -> PayoutRecord:
        """HELD -> PENDING. Admin releases the hold for re-review."""
        if record.status != PayoutRecordStatus.HELD:
            raise InvalidPayoutItemTransitionError(
                f"Record {record.pk} is {record.status}. "
                "Only HELD records can be released."
            )
 
        record.status = PayoutRecordStatus.PENDING
        record.hold_reason = ""
        record.save(update_fields=["status", "hold_reason"])
 
        return record
 
    # ------------------------------------------------------------------
    # Bulk operations
    # ------------------------------------------------------------------
 
    @staticmethod
    @transaction.atomic
    def bulk_confirm_all(
        batch: PayoutBatch,
        confirmed_by,
    ) -> int:
        """
        Confirm all PENDING records in one action.
        Returns count confirmed.
        """
        if batch.payment_window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING for bulk confirm."
            )
 
        now = timezone.now()
        count = (
            PayoutRecord.objects
            .filter(batch=batch, status=PayoutRecordStatus.PENDING)
            .update(
                status=PayoutRecordStatus.CONFIRMED,
                confirmed_at=now,
                confirmed_by=confirmed_by,
            )
        )
        return count
 
    @staticmethod
    @transaction.atomic
    def bulk_mark_paid(
        batch: PayoutBatch,
        paid_by,
    ) -> int:
        """
        Mark all CONFIRMED records as paid.
        Stamps underlying CompensationEvents as PAID per writer.
        Returns count paid.
        """
        if batch.payment_window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING for bulk pay."
            )
 
        confirmed_records = (
            PayoutRecord.objects
            .filter(batch=batch, status=PayoutRecordStatus.CONFIRMED)
            .select_related("writer")
        )
 
        now = timezone.now()
        count = 0
 
        for record in confirmed_records:
            record.status = PayoutRecordStatus.PAID
            record.paid_at = now
            record.paid_by = paid_by
            record.save(update_fields=["status", "paid_at", "paid_by"])

            CompensationWalletSyncService.settle_payout_record(
                record=record,
                actor=paid_by,
            )
 
            CompensationEvent.objects.filter(
                writer=record.writer,
                payment_window=batch.payment_window,   # FIX: was window
                status=EventStatus.MATURED,            # FIX: was CONFIRMED
            ).update(status=EventStatus.PAID)
 
            from writer_compensation.signals import payout_record_paid
            payout_record_paid.send(sender=PayoutRecord, record=record)
 
            count += 1
 
        return count
