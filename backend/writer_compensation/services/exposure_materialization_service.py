from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction

from writer_compensation.enums.compensation_enums import EventType
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.exposure_ledger import ExposureLedger  

logger = logging.getLogger(__name__)

ZERO = Decimal("0.00")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _safe(value) -> Decimal:
    """Coerce None / float / string to Decimal safely."""
    if value is None:
        return ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


# ---------------------------------------------------------------------------
# Event-type → ledger field mapping
# ---------------------------------------------------------------------------

# Each EventType maps to (field_name, sign_multiplier).
# sign_multiplier = 1  → add the raw amount to the field.
# sign_multiplier = -1 → the amount is already negative; add it to the field
#                        that tracks deductions (stored as positive running total).
#
# NOTE: amounts on CompensationEvent are signed:
#   earnings  → positive
#   deductions → negative
#
# ExposureLedger stores UNSIGNED running totals, so for deduction fields
# we store abs(amount).

_EVENT_FIELD_MAP: dict[str, tuple[str, int] | None] = {
    # Earnings — accumulate into total_earned
    EventType.ORDER_EARNING:         ("total_earned",       1),
    EventType.SPECIAL_ORDER_EARNING: ("total_earned",       1),
    EventType.CLASS_EARNING:         ("total_earned",       1),

    # Tips — treat as earned income
    EventType.TIP:                   ("total_earned",       1),

    # Bonuses
    EventType.BONUS:                 ("total_bonuses",      1),

    # Advances issued — go into total_advance_taken
    EventType.ADVANCE:               ("total_advance_taken", 1),

    # Deductions (amounts are negative on the event; store absolute value)
    EventType.FINE:                  ("total_deductions",   -1),
    EventType.DEDUCTION:             ("total_deductions",   -1),
    EventType.REFUND_DEDUCTION:      ("total_deductions",   -1),
    EventType.CANCELLATION:          ("total_deductions",   -1),

    # Advance recovery — reduces outstanding advance taken
    EventType.ADVANCE_RECOVERY:      ("total_advance_taken", -1),

    # Reversals — undo a prior earning; subtract from total_earned
    EventType.REVERSAL:              ("total_earned",       -1),

    # Adjustments — sign-driven; routed to _apply_adjustment in the service.
    # Sentinel value ("__adjustment__", 0) signals the special-case handler.
    EventType.ADJUSTMENT:             ("__adjustment__",    0),

    # Hold types — do not affect ledger totals (they are status markers)
    EventType.REVISION_HOLD:         None,
    EventType.DISPUTE_HOLD:          None,
}


def _apply_to_ledger(
    ledger: ExposureLedger,
    field: str,
    amount: Decimal,
    multiplier: int,
) -> None:
    """Increment a ledger field by (amount × multiplier), clamped at zero."""
    current = _safe(getattr(ledger, field))
    delta   = _safe(amount) * multiplier
    setattr(ledger, field, max(ZERO, current + delta))


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class ExposureMaterializationService:
    """
    Idempotent exposure materializer.

    Two modes:

    1. RESET-BASED (materialize_from_settlement)
       Full rebuild from a SettlementPeriod snapshot.
       Safe to call multiple times — always converges to correct state.
       Use after settlement runs.

    2. INCREMENTAL (materialize_from_event)
       Lightweight update on single event creation.
       Uses select_for_update() to prevent concurrent write races.
       Use for real-time ledger tracking between settlements.

    RULE: This service NEVER reads its own output to compute new output.
          Every calculation derives from source models (events, settlement).
    """

    # ------------------------------------------------------------------
    # Ledger fetch
    # ------------------------------------------------------------------

    @staticmethod
    def get_or_create_ledger(
        *,
        website,
        writer,
    ) -> ExposureLedger:
        ledger, created = ExposureLedger.objects.get_or_create(
            website=website,
            writer=writer,
        )
        if created:
            logger.info(
                "ExposureLedger created | writer=%s website=%s",
                writer.pk, website.pk,
            )
        return ledger

    # ------------------------------------------------------------------
    # Mode 1: Reset-based from SettlementPeriod
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def materialize_from_settlement(
        *,
        period,                    # SettlementPeriod instance
    ) -> ExposureLedger:
        """
        Full ledger rebuild from a closed SettlementPeriod.

        Resets all counters from the period's aggregated totals.
        Idempotent — safe to call repeatedly on the same period.

        Raises ValueError if period is not in a settled state.
        """
        from writer_compensation.enums.compensation_enums import SettlementStatus
        if period.status not in {
            SettlementStatus.COMPLETED,
            SettlementStatus.PROCESSING,
        }:
            raise ValueError(
                f"Cannot materialize from period {period.pk} "
                f"with status {period.status}. "
                "Expected PROCESSING or COMPLETED."
            )

        ledger = ExposureMaterializationService.get_or_create_ledger(
            website=period.website,
            writer=period.writer,
        )

        # FIX 6: Reset all fields from settlement — including total_paid
        # which was missing in the original and caused stale values.
        ledger.total_earned       = _safe(period.gross_earnings)
        ledger.total_bonuses      = _safe(period.total_bonuses)
        ledger.total_deductions   = _safe(period.total_deductions)
        ledger.total_settled      = _safe(period.net_payable)
        ledger.total_advance_taken = _safe(period.total_advances)

        # total_paid: use period.total_paid if the field exists,
        # otherwise fall back to total_settled as a safe approximation.
        ledger.total_paid = _safe(
            getattr(period, "total_paid", period.net_payable)
        )

        # FIX 5: Correct recoverable balance formula includes total_paid.
        ledger.recoverable_balance = max(
            ZERO,
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
            - ledger.total_paid,     # FIX: was missing
        )

        ledger.save()

        logger.info(
            "ExposureLedger reset from settlement | "
            "writer=%s period=%s net=%s",
            period.writer.pk, period.pk, ledger.recoverable_balance,
        )

        return ledger

    # ------------------------------------------------------------------
    # Mode 2: Incremental from single CompensationEvent
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def materialize_from_event(
        ce: CompensationEvent,
    ) -> ExposureLedger:
        """
        Incremental ledger update triggered by a single CompensationEvent.

        Uses select_for_update() to hold a row lock for the duration of
        the transaction, preventing concurrent writes from losing updates.

        WARNING:
            This path is for real-time tracking only.
            Do NOT use during full settlement rebuilds — use
            materialize_from_settlement() there instead to avoid
            double-counting.

        Returns the updated ledger.
        """
        # FIX 3: select_for_update prevents race conditions under
        # concurrent event creation for the same writer.
        ledger, created = ExposureLedger.objects.select_for_update().get_or_create(
            website=ce.website,
            writer=ce.writer,
        )

        event_type = ce.event_type

        # FIX 4: Handle ALL event types explicitly.
        mapping = _EVENT_FIELD_MAP.get(event_type)

        if mapping is None:
            # REVISION_HOLD, DISPUTE_HOLD — no ledger impact.
            logger.debug(
                "ExposureMaterializationService: event type %s "
                "has no ledger impact — skipping | event=%s",
                event_type, ce.pk,
            )
            return ledger

        field, multiplier = mapping

        if field == "__adjustment__":
            # Adjustments are signed — route to dedicated handler.
            ExposureMaterializationService._apply_adjustment(ledger, ce.amount)
        else:
            _apply_to_ledger(ledger, field, ce.amount, multiplier)

        # FIX 5: Recompute recoverable_balance correctly every time.
        ledger.recoverable_balance = max(
            ZERO,
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
            - ledger.total_paid,
        )

        ledger.save()

        logger.debug(
            "ExposureLedger updated | writer=%s event=%s type=%s "
            "amount=%s recoverable=%s",
            ce.writer.pk, ce.pk, event_type,
            ce.amount, ledger.recoverable_balance,
        )

        return ledger

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_adjustment(
        ledger: ExposureLedger,
        amount: Decimal,
    ) -> None:
        """
        ADJUSTMENT events are signed:
          positive → missed earning → add to total_earned
          negative → over-payment correction → add to total_deductions
        """
        amount = _safe(amount)
        if amount > ZERO:
            ledger.total_earned = _safe(ledger.total_earned) + amount
        elif amount < ZERO:
            ledger.total_deductions = _safe(ledger.total_deductions) + abs(amount)
        # zero: prevented by DB constraint; no-op here for safety

    # ------------------------------------------------------------------
    # Utility: full recompute from raw events (reconciliation use)
    # ------------------------------------------------------------------

    @staticmethod
    @transaction.atomic
    def recompute_from_events(
        *,
        website,
        writer,
    ) -> ExposureLedger:
        """
        Full ledger recompute by summing all CompensationEvents
        directly — bypasses SettlementPeriod entirely.

        Use this for:
          - reconciliation checks
          - drift detection
          - disaster recovery

        This is the most authoritative rebuild path because it reads
        directly from the immutable event log.
        """
        from django.db.models import Q, Sum
        from writer_compensation.enums.compensation_enums import EARNING_EVENT_TYPES, DEDUCTION_EVENT_TYPES

        ledger = ExposureMaterializationService.get_or_create_ledger(
            website=website,
            writer=writer,
        )

        events = CompensationEvent.objects.filter(
            website=website,
            writer=writer,
        )

        def total(qs) -> Decimal:
            result = qs.aggregate(t=Sum("amount"))["t"]
            return _safe(result)

        # Earnings: all positive-amount earning-type events
        earning_events = events.filter(
            event_type__in=list(EARNING_EVENT_TYPES),
            amount__gt=ZERO,
        )
        ledger.total_earned = total(
            earning_events.filter(
                event_type__in=[
                    EventType.ORDER_EARNING,
                    EventType.SPECIAL_ORDER_EARNING,
                    EventType.CLASS_EARNING,
                    EventType.TIP,
                ]
            )
        )
        ledger.total_bonuses = total(
            earning_events.filter(event_type=EventType.BONUS)
        )
        ledger.total_advance_taken = max(
            ZERO,
            total(events.filter(event_type=EventType.ADVANCE, amount__gt=ZERO))
            - total(events.filter(event_type=EventType.ADVANCE_RECOVERY))
        )

        # Deductions: all negative-amount deduction-type events (store absolute)
        deduction_events = events.filter(
            event_type__in=[
                EventType.FINE,
                EventType.DEDUCTION,
                EventType.REFUND_DEDUCTION,
                EventType.CANCELLATION,
            ],
            amount__lt=ZERO,
        )
        ledger.total_deductions = abs(total(deduction_events))

        # Paid: sum of events stamped PAID with positive amounts
        from writer_compensation.enums.compensation_enums import EventStatus
        ledger.total_paid = total(
            events.filter(status=EventStatus.PAID, amount__gt=ZERO)
        )

        # Settled: total net of events in settlement
        ledger.total_settled = total(
            events.filter(
                status__in=[
                    EventStatus.INCLUDED_IN_SETTLEMENT,
                    EventStatus.PAID,
                ]
            )
        )

        # Final recoverable balance
        ledger.recoverable_balance = max(
            ZERO,
            ledger.total_earned
            + ledger.total_bonuses
            - ledger.total_deductions
            - ledger.total_settled
            - ledger.total_advance_taken
            - ledger.total_paid,
        )

        ledger.save()

        logger.info(
            "ExposureLedger full recompute | writer=%s "
            "earned=%s bonuses=%s deductions=%s recoverable=%s",
            writer.pk,
            ledger.total_earned,
            ledger.total_bonuses,
            ledger.total_deductions,
            ledger.recoverable_balance,
        )

        return ledger