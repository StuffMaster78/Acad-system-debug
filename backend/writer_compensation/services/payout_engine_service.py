from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction

from django.utils import timezone

from writer_compensation.models.payout_batch import PayoutBatch
from writer_compensation.models.payout_record import PayoutRecord
from writer_compensation.models.compensation_event import CompensationEvent

from writer_compensation.enums.compensation_enums import (
    EventStatus,
    PayoutItemStatus,
    WindowStatus,
)
from writer_compensation.exceptions.exceptions import (
    InvalidPayoutItemTransitionError,
    InvalidWindowTransitionError,
)
class PayoutEngineService:
    """
    Payout intent builder.

    RULES:
        1. Batch = grouping container
        2. Record = payout intent per writer wallet
        3. Never executes money movement here
        4. Must be idempotent
    """

    STATUS_PENDING = "PENDING"

    # -----------------------------
    # CREATE BATCH
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def create_batch(
        *,
        website: Any,
        processed_by: Any | None = None,
        reference: str | None = None,
    ) -> PayoutBatch:
        """
        Create a payout batch (idempotent safe container).
        """

        batch = PayoutBatch.objects.create(
            website=website,
            processed_by=processed_by,
            status=PayoutEngineService.STATUS_PENDING,
            reference=reference,
        )

        return batch

    # -----------------------------
    # ADD RECORD
    # -----------------------------
    @staticmethod
    @transaction.atomic
    def add_record(
        *,
        batch: PayoutBatch,
        writer_wallet: Any,
        amount: Decimal,
        reference: str | None = None,
    ) -> PayoutRecord:
        """
        Add payout intent record to batch.

        Safety rules:
            - amount must be > 0
            - no duplicate wallet entry per batch
        """

        if amount <= Decimal("0.00"):
            raise ValueError("Payout amount must be greater than zero")

        # Prevent duplicate payouts for same wallet in same batch
        existing = PayoutRecord.objects.filter(
            batch=batch,
            writer_wallet=writer_wallet,
        ).first()

        if existing:
            return existing

        return PayoutRecord.objects.create(
            batch=batch,
            writer_wallet=writer_wallet,
            amount=amount,
            status=PayoutEngineService.STATUS_PENDING,
            reference=reference,
        )
    


    @staticmethod
    @transaction.atomic
    def confirm_record(
        record: PayoutRecord,
        confirmed_by,
    ) -> PayoutRecord:
        """
        PENDING → CONFIRMED.
        Admin has reviewed this writer's total and agrees it is correct.
        """
        if record.status != PayoutItemStatus.PENDING:
            raise InvalidPayoutItemTransitionError(
                f"Item {record.pk} is {record.status}. Only PENDING items can be confirmed."
            )
        if record.batch.window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING to confirm payout items."
            )
 
        record.status       = PayoutItemStatus.CONFIRMED
        record.confirmed_at = timezone.now()
        record.confirmed_by = confirmed_by
        record.save(update_fields=["status", "confirmed_at", "confirmed_by"])
 
        return record
 
    @staticmethod
    @transaction.atomic
    def mark_record_paid(
        record: PayoutRecord,
        paid_by,
        notes: str = "",
    ) -> PayoutRecord:
        """
        CONFIRMED → PAID.
 
        Admin has paid this writer externally.
        Stamps all linked CONFIRMED CompensationEvents as PAID.
        """
        if record.status != PayoutItemStatus.CONFIRMED:
            raise InvalidPayoutItemTransitionError(
                f"Item {record.pk} is {record.status}. Confirm before marking paid."
            )
 
        now = timezone.now()
        record.status  = PayoutItemStatus.PAID
        record.paid_at = now
        record.paid_by = paid_by
        if notes:
            record.notes = notes
        record.save(update_fields=["status", "paid_at", "paid_by", "notes"])
 
        # Stamp the underlying events.
        CompensationEvent.objects.filter(
            writer=record.writer,
            window=record.batch.window,
            status=EventStatus.CONFIRMED,
        ).update(status=EventStatus.PAID)
 
        # Fire notification signal.
        from writer_compensation.signals import payout_record_paid
        payout_record_paid.send(sender=PayoutRecord, record=record)
 
        return record
 
    @staticmethod
    @transaction.atomic
    def hold_record(
        record: PayoutRecord,
        reason: str,
        held_by,
    ) -> PayoutRecord:
        """
        PENDING | CONFIRMED → HELD.
        Other writers in the same batch are completely unaffected.
        """
        if record.status == PayoutItemStatus.PAID:
            raise InvalidPayoutItemTransitionError(
                f"Item {record.pk} is already PAID and cannot be held."
            )
 
        record.status      = PayoutItemStatus.HELD
        record.hold_reason = reason
        record.save(update_fields=["status", "hold_reason"])
 
        # Fire notification signal (generic message — reason never shown to writer).
        from writer_compensation.signals import payout_record_held
        payout_record_held.send(sender=PayoutRecord, record=record)
 
        return record
 
    @staticmethod
    @transaction.atomic
    def release_held_record(
        record: PayoutRecord,
        released_by,
    ) -> PayoutRecord:
        """
        HELD → PENDING.
        Admin releases a hold so the item can be reviewed again.
        """
        if record.status != PayoutItemStatus.HELD:
            raise InvalidPayoutItemTransitionError(
                f"Item {record.pk} is {record.status}. Only HELD items can be released."
            )
 
        record.status = PayoutItemStatus.PENDING
        record.hold_reason = ""
        record.save(update_fields=["status", "hold_reason"])
 
        return record
 
    @staticmethod
    @transaction.atomic
    def bulk_confirm_all(
        batch: PayoutBatch,
        confirmed_by,
    ) -> int:
        """
        Confirm all PENDING items in one action.
        Returns count of items confirmed.
        """
        if batch.payment_window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING for bulk confirm."
            )
 
        now = timezone.now()
        count = (
            PayoutRecord.objects
            .filter(batch=batch, status=PayoutItemStatus.PENDING)
            .update(
                status=PayoutItemStatus.CONFIRMED,
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
        Mark all CONFIRMED items as paid.
        Stamps underlying CompensationEvents as PAID per writer.
        Returns count of items paid.
        """
        if batch.payment_window.status != WindowStatus.PROCESSING:
            raise InvalidWindowTransitionError(
                "Window must be PROCESSING for bulk pay."
            )
 
        confirmed_records = (
            PayoutRecord.objects
            .filter(batch=batch, status=PayoutItemStatus.CONFIRMED)
            .select_related("writer")
        )
 
        now   = timezone.now()
        count = 0
 
        for record in confirmed_records:
            record.status  = PayoutItemStatus.PAID
            record.paid_at = now
            record.paid_by = paid_by
            record.save(update_fields=["status", "paid_at", "paid_by"])
 
            CompensationEvent.objects.filter(
                writer=record.writer,
                window=batch.payment_window,
                status=EventStatus.CONFIRMED,
            ).update(status=EventStatus.PAID)
 
            from writer_compensation.signals import payout_record_paid
            payout_record_paid.send(sender=PayoutRecord, record=record)
 
            count += 1
 
        return count