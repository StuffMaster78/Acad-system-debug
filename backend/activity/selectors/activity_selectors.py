from audit_logging.models.audit_event import AuditEvent


class AuditTraceSelectors:

    @staticmethod
    def full_trace_by_actor(actor_id, limit=100):
        return (
            AuditEvent.objects
            .filter(actor_id=actor_id)
            .order_by("-timestamp")[:limit]
        )

    @staticmethod
    def by_correlation(correlation_id):
        return (
            AuditEvent.objects
            .filter(correlation_id=correlation_id)
            .order_by("timestamp")
        )

    @staticmethod
    def by_object(object_type, object_id):
        return (
            AuditEvent.objects
            .filter(object_type=object_type, object_id=object_id)
            .order_by("timestamp")
        )