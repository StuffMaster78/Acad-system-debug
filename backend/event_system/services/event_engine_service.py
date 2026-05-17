from django.utils import timezone
from django.db import transaction

from event_system.models.event_outbox import EventOutbox, EventStatus
from event_system.router.event_router import EventRouter
from event_system.services.idempotency_service import IdempotencyService
from event_system.services.event_claim_service import EventClaimService
from event_system.services.event_execution_record_service import EventExecutionRecordService
from event_system.services.event_metrics_service import EventMetricsService
from event_system.services.event_audit_service import EventAuditService


class EventEngine:
    """
    Central event execution engine.
    """

    @classmethod
    def process(cls, event: EventOutbox) -> None:
        event_id = str(event.id)

        # 1. FAST SKIP
        if IdempotencyService.is_processed(event_id):
            event.status = EventStatus.PROCESSED
            event.processed_at = timezone.now()
            event.save(update_fields=["status", "processed_at"])
            return

        # 2. CLAIM
        claimed = EventClaimService.claim(event_id)
        if not claimed:
            return

        event = claimed

        handler = EventRouter.get(event.event_type)
        if handler is None:
            event.status = EventStatus.IGNORED
            event.ignored_at = timezone.now()
            event.save(update_fields=["status", "ignored_at"])
            return

        # 3. EXECUTION SAFETY
        if EventExecutionRecordService.has_run(event_id):
            return

        start = EventMetricsService.start()

        try:
            with transaction.atomic():
                handler(event)

                EventExecutionRecordService.mark_run(event_id)

                event.status = EventStatus.PROCESSED
                event.processed_at = timezone.now()
                event.updated_at = timezone.now()

                event.save(update_fields=["status", "processed_at", "updated_at"])

                IdempotencyService.mark_processed(event_id)

                EventAuditService.log(
                    event_id=event_id,
                    event_type=event.event_type,
                    stage="dispatched",
                    duration_ms=EventMetricsService.end(start),
                )

        except Exception as exc:
            EventMetricsService.end(start)

            event.attempts += 1
            event.last_error = str(exc)

            event.status = (
                EventStatus.DEAD_LETTER
                if event.attempts >= event.max_attempts
                else EventStatus.FAILED
            )

            event.save(update_fields=["attempts", "status", "last_error"])

            raise