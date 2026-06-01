from django.db.models import QuerySet

from event_system.models.event_audit_log import EventAuditLog
from event_system.models.event_outbox import EventOutbox

class EventTimelineService:
    """
    Reconstructs the full lifecycle of an event.

    Think:
        "What actually happened to this event?"
    """

    @classmethod
    def get_event_timeline(cls, *, event_id: str) -> QuerySet:
        """
        Returns ordered lifecycle of an event.
        """

        return EventAuditLog.objects.filter(
            event_id=event_id,
        ).order_by("created_at")

    @classmethod
    def get_latest_stage(cls, *, event_id: str):
        """
        Returns most recent known state.
        """

        return (
            EventAuditLog.objects.filter(event_id=event_id)
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def get_failed_events(cls, limit: int = 100):
        """
        Fast operational view for debugging failures.
        """

        return EventAuditLog.objects.filter(
            event_status="FAILED"
        ).order_by("-created_at")[:limit]

    # ----------------------------
    # 2. RECONSTRUCTED TIMELINE
    # ----------------------------

    @classmethod
    def build_event_timeline(
        cls,
        *,
        event_id: str | None = None,
        correlation_id: str | None = None,
    ) -> list[dict]:

        if correlation_id:
            events = EventOutbox.objects.filter(
                correlation_id=correlation_id
            ).order_by("created_at")

            timeline: list[dict] = []

            for event in events:
                timeline.append(
                    {
                        "type": "event_created",
                        "event_id": str(event.id),
                        "correlation_id": correlation_id,
                        "event_type": event.event_type,
                        "status": event.status,
                        "timestamp": event.created_at,
                    }
                )

                if event.processed_at:
                    timeline.append(
                        {
                            "type": "processed",
                            "event_id": str(event.id),
                            "timestamp": event.processed_at,
                        }
                    )

                if event.ignored_at:
                    timeline.append(
                        {
                            "type": "ignored",
                            "event_id": str(event.id),
                            "timestamp": event.ignored_at,
                        }
                    )

                if event.last_error:
                    timeline.append(
                        {
                            "type": "failure",
                            "event_id": str(event.id),
                            "error": event.last_error,
                            "timestamp": event.updated_at,
                        }
                    )

            return sorted(timeline, key=lambda x: x["timestamp"])

        # fallback: single event timeline
        if not event_id:
            return []

        event = EventOutbox.objects.filter(id=event_id).first()

        if not event:
            return []

        timeline: list[dict] = [
            {
                "type": "event_created",
                "event_id": str(event.id),
                "event_type": event.event_type,
                "status": event.status,
                "timestamp": event.created_at,
            }
        ]

        if event.processed_at:
            timeline.append(
                {
                    "type": "processed",
                    "event_id": str(event.id),
                    "timestamp": event.processed_at,
                    "attempts": event.attempts,
                }
            )

        if event.ignored_at:
            timeline.append(
                {
                    "type": "ignored",
                    "event_id": str(event.id),
                    "timestamp": event.ignored_at,
                }
            )

        if event.last_error:
            timeline.append(
                {
                    "type": "failure",
                    "event_id": str(event.id),
                    "error": event.last_error,
                    "timestamp": event.updated_at,
                }
            )

        return sorted(timeline, key=lambda x: x["timestamp"])