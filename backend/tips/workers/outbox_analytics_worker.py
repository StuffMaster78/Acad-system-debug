from django.utils import timezone
from django.db import transaction

from tips.models.tip_outbox_event import TipOutboxEvent
from tips.models.tip_analytics_daily import TipAnalyticsDaily


class TipOutboxAnalyticsWorker:
    """
    Consumes outbox events and builds analytics aggregates.
    """

    @staticmethod
    @transaction.atomic
    def process_batch(limit: int = 100):

        events = (
            TipOutboxEvent.objects
            .select_for_update(skip_locked=True)
            .filter(processed=False)
            .order_by("created_at")[:limit]
        )

        for event in events:
            TipOutboxAnalyticsWorker._process(event)
            event.mark_processed()

    # ---------------------------- #

    @staticmethod
    def _process(event: TipOutboxEvent):

        date = event.created_at.date()

        row, _ = TipAnalyticsDaily.objects.get_or_create(date=date)

        if event.event_type == "tip.succeeded":
            row.total_successful_tips += 1

            payload = event.payload or {}
            amount = payload.get("amount_cents", 0)

            row.total_volume_cents += amount

            writer = payload.get("writer_share_cents", 0)
            fee = payload.get("platform_fee_cents", 0)

            row.writer_earnings_cents += writer
            row.platform_fee_cents += fee

        elif event.event_type == "tip.failed":
            row.total_failed_tips += 1

        elif event.event_type == "tip.created":
            row.total_tips += 1

        row.save()