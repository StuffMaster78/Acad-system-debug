from __future__ import annotations

from typing import Callable

from django.utils import timezone

from notifications_system.services.notification_service import NotificationService

from tips.enums.tip_events import TipEvents
from tips.models.tip_outbox_event import TipOutboxEvent
from tips.services.tip_settlement_engine import TipSettlementEngine


class TipOutboxWorker:
    """
    Processes durable outbox events.

    SINGLE RULE:
        Event = source of truth
        Worker = side-effect executor
    """

    HANDLERS: dict[str, Callable] = {}

    @classmethod
    def process(cls, event: TipOutboxEvent) -> None:

        handler = cls.HANDLERS.get(event.event_type)

        if handler is None:
            event.mark_failed(f"No handler for event: {event.event_type}")
            return

        try:
            handler(event)
            event.mark_processed()

        except Exception as exc:
            event.mark_failed(str(exc))

    # ------------------------------------------------------------ #
    # HANDLERS
    # ------------------------------------------------------------ #

    @staticmethod
    def handle_tip_succeeded(event: TipOutboxEvent) -> None:
        """
        1. Settle financials (ledger becomes source of truth)
        2. Notify stakeholders
        """

        tip = event.tip

        # 1. FINANCIAL SETTLEMENT FIRST (idempotent internally)
        TipSettlementEngine.settle_tip(
            tip=tip,
            triggered_by=None,
        )

        # 2. NOTIFICATIONS (non-blocking side effect)
        NotificationService.notify(
            website=getattr(tip.sender, "website", None),
            event_key=TipEvents.SUCCEEDED,
            recipient=tip.receiver,
            context={
                "tip_id": tip.pk,
                "amount": str(tip.gross_amount),
            },
            channels=["email", "in_app"],
            is_critical=False,
        )

    @staticmethod
    def handle_tip_failed(event: TipOutboxEvent) -> None:

        tip = event.tip

        NotificationService.notify(
            website=getattr(tip.sender, "website", None),
            event_key=TipEvents.FAILED,
            recipient=tip.sender,
            context={
                "tip_id": tip.pk,
            },
            channels=["email", "in_app"],
            is_critical=True,
        )


TipOutboxWorker.HANDLERS = {
    TipEvents.SUCCEEDED: TipOutboxWorker.handle_tip_succeeded,
    TipEvents.FAILED: TipOutboxWorker.handle_tip_failed,
}