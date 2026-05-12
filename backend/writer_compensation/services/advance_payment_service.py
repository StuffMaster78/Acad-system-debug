"""
writer_compensation/services/advance_payment_service.py

Fixes applied:
  1. select_for_update() on ledger read — prevents race condition when
     two concurrent advance approvals read the same total_advance_taken,
     both add to it, and one write is silently lost.

  2. CompensationEvent now fired via EventIntakeService.record() after
     ledger update — previously the ledger was updated but no event was
     created, meaning settlement never saw the advance. The event log
     and the ledger were out of sync.

  3. ADVANCE_RECOVERY path added — AdvanceRecovery.record() creates the
     negative ADVANCE_RECOVERY CompensationEvent that settlement deducts
     from the writer's payout window.

  4. website + writer + created_by added as required params to apply_advance
     so the CompensationEvent can be created with full context.

  5. select_for_update() wraps both ledger paths (apply + recovery) to
     prevent concurrent writes from corrupting running totals.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_compensation.enums.compensation_enums import EventType
from writer_compensation.exceptions.exceptions import ZeroAmountError
from writer_compensation.models.advance_payment import (
    AdvancePaymentRequest,
    AdvanceRecovery,
)
from writer_compensation.models.exposure_ledger import ExposureLedger
from writer_compensation.services.event_intake_service import EventIntakeService
from writer_compensation.services.risk_engine_service import RiskEngineService


class AdvancePaymentService:
    """
    Handles writer advance issuance and recovery.

    Core financial rules:
        - Advances are liabilities against future earnings.
        - Issuance increases exposure and fires an ADVANCE CompensationEvent.
        - Recovery decreases exposure and fires an ADVANCE_RECOVERY event
          into the current open window so settlement deducts it from payout.
        - Never mutates historical events.
        - All ledger updates use select_for_update() to prevent races.
    """

    # ------------------------------------------------------------------
    # Eligibility check (read-only, no lock needed)
    # ------------------------------------------------------------------

    @staticmethod
    def can_request(
        *,
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> bool:
        """
        Returns True if the writer can request an advance of this amount.
        Pure read — does not modify any state.
        """
        if amount <= Decimal("0.00"):
            return False

        return RiskEngineService.can_issue_advance(
            ledger=ledger,
            amount=amount,
        )

    # ------------------------------------------------------------------
    # Issuance
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def apply_advance(
        *,
        website: Any,
        writer: Any,
        ledger: ExposureLedger,
        amount: Decimal,
        created_by: Any | None = None,
        advance_request: AdvancePaymentRequest | None = None,
    ) -> ExposureLedger:
        """
        Issue an advance to a writer.

        Steps:
            1. Validate amount > 0
            2. Lock ledger row (select_for_update)
            3. Check risk capacity against live locked values
            4. Update ledger counters
            5. Fire ADVANCE CompensationEvent into current open window

        Returns the updated ExposureLedger.

        Raises:
            ZeroAmountError  — amount is zero
            ValueError       — amount exceeds risk capacity
        """
        if amount <= Decimal("0.00"):
            raise ZeroAmountError("Advance amount must be greater than zero.")

        # FIX 1: Lock the row before reading — prevents concurrent writes
        # from both seeing the same total_advance_taken and double-spending.
        ledger = (
            ExposureLedger.objects
            .select_for_update()
            .get(pk=ledger.pk)
        )

        if not RiskEngineService.can_issue_advance(ledger=ledger, amount=amount):
            cap = RiskEngineService.get_advance_cap(ledger=ledger)
            raise ValueError(
                f"Advance of {amount} exceeds available capacity {cap}."
            )

        ledger.total_advance_taken += amount
        ledger.recoverable_balance = max(
            Decimal("0.00"),
            ledger.recoverable_balance - amount,
        )
        ledger.save(update_fields=[
            "total_advance_taken",
            "recoverable_balance",
            "last_updated",
        ])

        # FIX 2: Fire CompensationEvent so settlement sees the advance.
        # Previously this was missing — ledger updated but event log empty.
        request_ref = f"-req{advance_request.pk}" if advance_request else ""
        idempotency_key = (
            f"advance-{writer.pk}-{amount}-{timezone.now().date()}{request_ref}"
        )

        EventIntakeService.record(
            website=website,
            writer=writer,
            event_type=EventType.ADVANCE,
            amount=amount,
            source_type="advance_request" if advance_request else "",
            source_id=advance_request.pk if advance_request else None,
            title=f"Advance issued — ${amount}",
            notes=f"Advance approved. Request: {advance_request.pk if advance_request else 'manual'}",
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        return ledger

    # ------------------------------------------------------------------
    # Recovery
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def record_recovery(
        *,
        website: Any,
        writer: Any,
        ledger: ExposureLedger,
        advance_request: AdvancePaymentRequest,
        amount: Decimal,
        settlement_period: Any | None = None,
        notes: str = "",
        created_by: Any | None = None,
    ) -> AdvanceRecovery:
        """
        Record a repayment instalment against an advance.

        Steps:
            1. Validate amount > 0 and does not exceed outstanding balance
            2. Lock ledger row
            3. Reduce total_advance_taken
            4. Create AdvanceRecovery record
            5. Fire ADVANCE_RECOVERY CompensationEvent (negative amount)
               so settlement deducts it from the writer's next payout

        Returns the created AdvanceRecovery.

        Raises:
            ZeroAmountError — amount is zero
            ValueError      — amount exceeds outstanding advance balance
        """
        if amount <= Decimal("0.00"):
            raise ZeroAmountError("Recovery amount must be greater than zero.")

        outstanding = advance_request.outstanding_balance
        if amount > outstanding:
            raise ValueError(
                f"Recovery amount {amount} exceeds outstanding balance {outstanding}."
            )

        # FIX 1: Lock ledger row for recovery update too.
        ledger = (
            ExposureLedger.objects
            .select_for_update()
            .get(pk=ledger.pk)
        )

        ledger.total_advance_taken = max(
            Decimal("0.00"),
            ledger.total_advance_taken - amount,
        )
        ledger.recoverable_balance += amount
        ledger.save(update_fields=[
            "total_advance_taken",
            "recoverable_balance",
            "last_updated",
        ])

        # Update the advance request recovered amount.
        advance_request.recovered_amount += amount
        if advance_request.recovered_amount >= advance_request.approved_amount:
            from writer_compensation.enums.compensation_enums import AdvancePaymentStatus
            advance_request.status = AdvancePaymentStatus.RECOVERED
        else:
            from writer_compensation.enums.compensation_enums import AdvancePaymentStatus
            advance_request.status = AdvancePaymentStatus.PARTIALLY_RECOVERED
        advance_request.save(update_fields=["recovered_amount", "status", "updated_at"])

        # Create the AdvanceRecovery audit record.
        recovery = AdvanceRecovery.objects.create(
            advance_request=advance_request,
            settlement_period=settlement_period,
            amount=amount,
            notes=notes,
        )

        # FIX 3: Fire negative ADVANCE_RECOVERY CompensationEvent.
        # Settlement picks this up and deducts it from the payout window.
        idempotency_key = (
            f"advance-recovery-{advance_request.pk}-{recovery.pk}"
        )
        EventIntakeService.record(
            website=website,
            writer=writer,
            event_type=EventType.ADVANCE_RECOVERY,
            amount=-amount,                     # negative — deduction from payout
            source_type="advance_request",
            source_id=advance_request.pk,
            title=f"Advance recovery — ${amount}",
            notes=notes or f"Recovery instalment against advance #{advance_request.pk}",
            idempotency_key=idempotency_key,
            created_by=created_by,
        )

        return recovery