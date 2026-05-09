from __future__ import annotations

from decimal import Decimal
from typing import Any

from django.utils import timezone

from writer_payments_management.enums.financial_event_enums import (
    FinancialEventStatus,
    FinancialEventType,
    SettlementStatus,
)

from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.models.settlement_period_models import SettlementPeriod
from writer_payments_management.models.settlement_item_models import SettlementItem
from writer_payments_management.models.payment_window_models import PaymentWindow
from writer_payments_management.services.settlement_validation_layer import (
    SettlementValidationService,
)
from writer_payments_management.tasks.settlement_tasks import (
    materialize_exposure_from_settlement,
)


class SettlementEngineService:
    """
    Deterministic settlement engine.

    Core invariants:
        FinancialEvent = truth
        SettlementPeriod = snapshot
        SettlementItem = breakdown
    """

    @staticmethod
    def create_settlement_period(
        *,
        website: Any,
        writer: Any,
        payment_window: PaymentWindow,
    ) -> SettlementPeriod:
        period, _ = SettlementPeriod.objects.get_or_create(
            website=website,
            writer=writer,
            payment_window=payment_window,
        )
        return period

    @staticmethod
    def compute_financial_events(*, period: SettlementPeriod):
        return FinancialEvent.objects.filter(
            website=period.website,
            writer=period.writer,
            settlement_period__isnull=True,
            status=FinancialEventStatus.MATURED,
            created_at__range=(
                period.payment_window.start_date,
                period.payment_window.end_date,
            ),
        )

    @staticmethod
    def build_settlement_snapshot(
        *,
        period: SettlementPeriod,
    ) -> SettlementPeriod:

        qs = SettlementEngineService.compute_financial_events(period=period)

        gross = Decimal("0.00")
        tips = Decimal("0.00")
        bonuses = Decimal("0.00")
        adjustments = Decimal("0.00")

        fines = Decimal("0.00")
        deductions = Decimal("0.00")
        advances = Decimal("0.00")
        reversals = Decimal("0.00")

        count = 0

        for event in qs.iterator():
            count += 1
            amount = event.amount
            t = event.event_type

            if t in {
                FinancialEventType.ORDER_EARNING,
                FinancialEventType.SPECIAL_ORDER_EARNING,
                FinancialEventType.CLASS_EARNING,
            }:
                gross += amount

            elif t == FinancialEventType.TIP:
                tips += amount

            elif t == FinancialEventType.BONUS:
                bonuses += amount

            elif t == FinancialEventType.ADJUSTMENT:
                adjustments += amount

            elif t == FinancialEventType.FINE:
                fines += amount

            elif t == FinancialEventType.DEDUCTION:
                deductions += amount

            elif t in {
                FinancialEventType.ADVANCE_PAYMENT,
                FinancialEventType.ADVANCE_RECOVERY,
            }:
                advances += amount

            elif t == FinancialEventType.REVERSAL:
                reversals += amount

        net = (
            gross
            + tips
            + bonuses
            + adjustments
            - fines
            - deductions
            - advances
            + reversals
        )

        period.gross_earnings = gross
        period.total_tips = tips
        period.total_bonuses = bonuses
        period.total_adjustments = adjustments
        period.total_fines = fines
        period.total_deductions = deductions
        period.total_advances = advances
        period.total_reversals = reversals
        period.net_payable = net
        period.total_financial_events = count

        period.save()
        return period

    @staticmethod
    def finalize_settlement_period(
        *,
        period: SettlementPeriod,
        actor: Any | None = None,
    ) -> SettlementPeriod:

        now = timezone.now()

        period.is_locked = True
        period.locked_at = now
        period.finalized_at = now
        period.status = SettlementStatus.COMPLETED
        period.save()

        FinancialEvent.objects.filter(
            website=period.website,
            writer=period.writer,
            settlement_period__isnull=True,
            status=FinancialEventStatus.MATURED,
        ).update(settlement_period=period)

        # SAFE CELERY CALL (no attribute shadowing risk)
        if hasattr(materialize_exposure_from_settlement, "delay"):
            task = getattr(materialize_exposure_from_settlement, "delay", None)

            if callable(task):
                task(period.pk)

        return period

    @staticmethod
    def create_settlement_items(*, period: SettlementPeriod):

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
    def run_settlement_pipeline(
        *,
        period: SettlementPeriod,
    ):
        SettlementEngineService.build_settlement_snapshot(period=period)
        SettlementValidationService.assert_valid(period=period)
        SettlementEngineService.create_settlement_items(period=period)

        return period