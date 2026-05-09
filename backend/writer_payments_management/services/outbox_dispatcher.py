from django.db import transaction
from django.utils import timezone

from writer_payments_management.models.outbox_event_models import OutboxEvent
from writer_payments_management.models.financial_event_models import FinancialEvent
from writer_payments_management.models.settlement_period_models import SettlementPeriod
from writer_payments_management.services.exposure_materialization_service import (
    ExposureMaterializationService,
)


class OutboxDispatcher:
    """
    Processes outbox events safely and deterministically.
    """

    @staticmethod
    def process_batch(limit: int = 100):
        events = (
            OutboxEvent.objects.filter(processed=False)
            .order_by("created_at")[:limit]
        )

        for event in events:
            try:
                with transaction.atomic():

                    if event.event_type == "FINANCIAL_EVENT_CREATED":
                        fe = FinancialEvent.objects.get(
                            id=event.payload["financial_event_id"]
                        )

                        period_id = event.payload.get("settlement_period_id")

                        if period_id is None:
                            raise ValueError(
                                "Missing settlement_period_id in outbox payload"
                            )

                        period = SettlementPeriod.objects.get(id=period_id)

                        # SAFE: no None possible now
                        ExposureMaterializationService.materialize_from_settlement(
                            period=period
                        )

                    event.processed = True
                    event.processed_at = timezone.now()
                    event.save()

            except Exception as e:
                event.retry_count += 1
                event.last_error = str(e)
                event.save()