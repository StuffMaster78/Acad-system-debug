from event_system.models.event_outbox import EventOutbox
from event_system.services.event_engine_service import EventEngine


class EventInspectionService:
    """
    Safe tooling for debugging and replay.
    """

    @classmethod
    def replay_event(cls, event_id: str) -> None:
        event = EventOutbox.objects.get(id=event_id)

        # reset safe state only
        event.status = "PENDING"
        event.attempts = 0
        event.last_error = None
        event.save(update_fields=["status", "attempts", "last_error"])

        EventEngine.process(event)

    @classmethod
    def inspect_event(cls, event_id: str):
        from event_system.services.event_timeline_service import EventTimelineService

        return {
            "event": EventOutbox.objects.get(id=event_id),
            "timeline": list(
                EventTimelineService.get_event_timeline(event_id=event_id)
            ),
        }