from activity.selectors.activity_selectors import AuditTraceSelectors
from activity.services.deduplication_service import DeduplicationService


class TimelineBuilder:

    def build_object_timeline(self, object_type, object_id):

        events = AuditTraceSelectors.by_object(object_type, object_id)

        events = DeduplicationService.deduplicate(events)

        return [
            {
                "action": e.action,
                "actor": e.actor_id,
                "timestamp": e.timestamp,
                "span": e.span_name,
                "duration_ms": e.span_duration_ms,
                "correlation_id": e.correlation_id,
            }
            for e in events
        ]