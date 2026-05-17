from event_system.models.event_outbox import EventOutbox


class EventFailureService:
    """
    Reads failure history for events.

    This is observability-only.
    No mutations.
    """

    @staticmethod
    def get_failures(event_id: str):
        event = EventOutbox.objects.filter(id=event_id).first()

        if not event:
            return []

        # Single-event failure view (extend later to real failure logs table)
        if event.status in ["failed", "dead_letter"]:
            return [
                {
                    "event_id": str(event.id),
                    "attempts": event.attempts,
                    "last_error": event.last_error,
                    "status": event.status,
                    "updated_at": event.updated_at,
                }
            ]

        return []