from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.db import transaction
from django.utils import timezone

from writer_compensation.enums.compensation_enums import (
    EventStatus,
    EventType,
    SettlementStatus,
)
from writer_compensation.models.compensation_event import CompensationEvent
from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.models.settlement_item import SettlementItem
from writer_compensation.services.settlement_validation_layer import (
    SettlementValidationService,
)
from writer_compensation.services.wallet_sync_service import (
    CompensationWalletSyncService,
)


try:
    from writer_compensation.tasks.settlement_tasks import (
        materialize_exposure_from_settlement,
    )
except ImportError:
    materialize_exposure_from_settlement = None  # type: ignore


class SettlementEngineService:
    """
    Deterministic settlement engine.

    Core invariants:
        CompensationEvent = truth
        SettlementPeriod  = snapshot
        SettlementItem    = breakdown
    """

    @staticmethod
    def create_settlement_period(
        *,
        website: Any,
        writer: Any,
        payment_window: Any,
    ) -> SettlementPeriod:
        period, _ = SettlementPeriod.objects.get_or_create(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )
        return period

    @staticmethod
    def compute_financial_events(*, period: SettlementPeriod):
        """
        FIX: was filtering on created_at__range using DateField values against
        a DateTimeField — events at end of day were included/excluded inconsistently.
        Now filters on payment_window FK directly — the FK is the canonical truth.
        """
        return CompensationEvent.objects.filter(
            payment_window=period.payment_window,           # FIX: was created_at__range
            settlement_period__isnull=True,
            status=EventStatus.MATURED,                     # FIX: was FinancialEventStatus.MATURED
        )

    @staticmethod
    def build_settlement_snapshot(*, period: SettlementPeriod) -> SettlementPeriod:
        qs = SettlementEngineService.compute_financial_events(period=period)

        gross       = Decimal("0.00")
        tips        = Decimal("0.00")
        bonuses     = Decimal("0.00")
        adjustments = Decimal("0.00")
        fines       = Decimal("0.00")
        deductions  = Decimal("0.00")
        advances    = Decimal("0.00")
        reversals   = Decimal("0.00")
        count       = 0

        for event in qs.iterator():
            count  += 1
            amount  = event.amount
            t       = event.event_type

            # FIX: all EventType refs now from unified compensation_enums
            if t in {
                EventType.ORDER_EARNING,
                EventType.SPECIAL_ORDER_EARNING,
                EventType.CLASS_EARNING,
            }:
                gross += amount

            elif t == EventType.TIP:
                tips += amount

            elif t == EventType.BONUS:
                bonuses += amount

            elif t == EventType.ADJUSTMENT:
                adjustments += amount

            elif t == EventType.FINE:
                fines += amount

            elif t == EventType.DEDUCTION:
                deductions += amount

            elif t in {
                EventType.ADVANCE,
                EventType.ADVANCE_RECOVERY,
            }:
                # advances accumulates signed amounts:
                # ADVANCE is positive, ADVANCE_RECOVERY is negative
                advances += amount

            elif t == EventType.REVERSAL:
                # reversal amounts are already negative on the event —
                # accumulate signed; net formula adds this (subtracting effectively)
                reversals += amount

        net = (
            gross
            + tips
            + bonuses
            + adjustments
            - abs(fines)        # fines stored as negative; force deduction
            - abs(deductions)   # same
            + advances          # signed: positive advance, negative recovery
            + reversals         # already negative amounts
        )

        period.gross_earnings          = gross
        period.total_tips              = tips
        period.total_bonuses           = bonuses
        period.total_adjustments       = adjustments
        period.total_fines             = fines
        period.total_deductions        = deductions
        period.total_advances          = advances
        period.total_reversals         = reversals
        period.net_payable             = net
        period.total_financial_events  = count

        period.save()
        return period

    @staticmethod
    @transaction.atomic                                     # FIX: was missing
    def finalize_settlement_period(
        *,
        period: SettlementPeriod,
        actor: Any | None = None,
    ) -> SettlementPeriod:
        """
        Locks the settlement period, stamps all linked events, and
        triggers exposure materialization.

        FIX: wrapped in @transaction.atomic — previously three DB operations
        ran without a transaction; a failure mid-way left the period marked
        COMPLETED while events remained unstamped.
        """
        now = timezone.now()

        period.is_locked    = True
        period.locked_at    = now
        period.finalized_at = now
        period.status       = SettlementStatus.COMPLETED   # FIX: was raw string
        period.save()

        # Stamp all matured events in this window as included in settlement.
        CompensationEvent.objects.filter(
            website=period.website,
            writer=period.writer,
            payment_window=period.payment_window,           # FIX: was no window filter
            settlement_period__isnull=True,
            status=EventStatus.MATURED,                     # FIX: was FinancialEventStatus
        ).update(
            settlement_period=period,
            status=EventStatus.INCLUDED_IN_SETTLEMENT,
        )

        CompensationWalletSyncService.credit_settlement_to_wallet(
            period=period,
            actor=actor,
        )

        # Fire Celery task safely — import guard at top handles missing module.
        if materialize_exposure_from_settlement is not None:
            task = getattr(materialize_exposure_from_settlement, "delay", None)
            if callable(task):
                task(period.pk)

        return period

    @staticmethod
    def create_settlement_items(*, period: SettlementPeriod) -> list:
        qs = SettlementEngineService.compute_financial_events(period=period)

        items = [
            SettlementItem(
                settlement_period=period,
                financial_event=event,
                amount=event.amount,
            )
            for event in qs
        ]

        SettlementItem.objects.bulk_create(items)

        period.total_settlement_items = len(items)
        period.save(update_fields=["total_settlement_items"])

        return items

    @staticmethod
    def run_settlement_pipeline(*, period: SettlementPeriod) -> SettlementPeriod:
        SettlementEngineService.build_settlement_snapshot(period=period)
        SettlementValidationService.assert_valid(period=period)
        SettlementEngineService.create_settlement_items(period=period)
        SettlementEngineService.finalize_settlement_period(period=period)
        return period
