from django.utils import timezone

from event_system.models.event_outbox import EventOutbox
from event_system.services.event_engine_service import EventEngine
from event_system.models.event_outbox import EventStatus
from event_system.services.event_execution_record_service import (
    EventExecutionRecordService,
)
from event_system.services.event_audit_service import EventAuditService

class EventReplayService:
    """
    Safe replay mechanism for failed/dead-letter events.
    """

    @classmethod
    def replay(
        cls,
        event_id: str,
        reason: str = "manual_replay",
    ) -> None:
        event = EventOutbox.objects.get(id=event_id)

        # safety guard: only replay unsafe states
        if event.status not in [
            EventStatus.FAILED,
            EventStatus.DEAD_LETTER,
            EventStatus.IGNORED
        ]:
            return

        # reset execution state safely (NOT identity or payload)
        event.status = EventStatus.PENDING
        event.attempts = 0
        event.last_error = ""
        event.processed_at = None
        event.ignored_at = None
        event.updated_at = timezone.now()
        event.save(
            update_fields=[
                "attempts",
                "status",
                "last_error",
                "ignored_at",
                "processed_at",
                "updated_at",
            ],
        )

        # reset execution record (critical)
        EventExecutionRecordService.clear(event_id)

        EventAuditService.log(
            event_id=str(event.id),
            event_type=event.event_type,
            stage="replay_triggered",
            payload={"reason": reason},
            correlation_id=getattr(event, "correlation_id", None),
            retry_count=event.attempts,
            event_status=event.status,
        )

        # critical: clear execution lock
        EventExecutionRecordService.clear(event_id)

        EventEngine.process(event)