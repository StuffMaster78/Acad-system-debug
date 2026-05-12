from django.db import transaction
from django.utils import timezone
import logging

from writer_compensation.models.outbox_event_models import OutboxEvent
from writer_compensation.models.settlement_period import SettlementPeriod
from writer_compensation.services.exposure_materialization_service import (
    ExposureMaterializationService,
)

logger = logging.getLogger(__name__)


class OutboxDispatcher:

    @staticmethod
    def process_batch(limit: int = 100):

        now = timezone.now()

        # STEP 1: CLAIM EVENTS SAFELY
        with transaction.atomic():

            events = (
                OutboxEvent.objects
                .select_for_update(skip_locked=True)
                .filter(processed=False, status=OutboxEvent.Status.PENDING)
                .order_by("created_at")[:limit]
            )

            # mark as processing immediately (prevents double pickup)
            for event in events:
                event.status = OutboxEvent.Status.PROCESSING

            OutboxEvent.objects.bulk_update(events, ["status"])

        # STEP 2: PROCESS OUTSIDE LOCK
        for event in events:

            try:
                payload = event.payload

                if event.event_type == "FINANCIAL_EVENT_CREATED":

                    period_id = payload.get("settlement_period_id")

                    if not period_id:
                        raise ValueError("Missing settlement_period_id")

                    period = SettlementPeriod.objects.get(id=period_id)

                    ExposureMaterializationService.materialize_from_settlement(
                        period=period
                    )

                # SUCCESS
                event.processed = True
                event.status = OutboxEvent.Status.DONE
                event.processed_at = now

                event.save(update_fields=[
                    "processed",
                    "status",
                    "processed_at",
                ])

            except Exception as e:

                event.retry_count += 1
                event.last_error = str(e)

                if event.retry_count >= OutboxEvent.MAX_RETRIES:
                    event.status = OutboxEvent.Status.DEAD
                    logger.error(f"Dead-letter event {event.pk}: {e}")
                else:
                    event.status = OutboxEvent.Status.PENDING

                event.save(update_fields=[
                    "retry_count",
                    "last_error",
                    "status",
                ])

                logger.exception(
                    f"Outbox processing failed for event {event.pk}"
                )