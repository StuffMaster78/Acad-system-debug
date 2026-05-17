from __future__ import annotations

from audit_logging.models.audit_event import AuditEvent
from event_system.models.event_outbox import EventOutbox


class ReplayEngine:
    """
    Reconstructs governance execution timeline.
    """

    @staticmethod
    def replay_command(
        command_id: str,
    ) -> dict:

        audit_logs = AuditEvent.objects.filter(
            object_id=command_id,
        ).order_by("created_at")

        events = EventOutbox.objects.filter(
            payload__contains={
                "command_id": command_id,
            }
        ).order_by("created_at")

        return {
            "command_id": command_id,
            "audit_logs": [
                {
                    "action": log.action,
                    "timestamp": getattr(
                        log,
                        "created_at",
                        None,
                    ),
                }
                for log in audit_logs
            ],
            "events": [
                {
                    "event_type": event.event_type,
                    "timestamp": getattr(
                        event,
                        "created_at",
                        None,
                    ),
                }
                for event in events
            ],
        }