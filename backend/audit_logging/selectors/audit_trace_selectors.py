from audit_logging.storage.models import AuditEvent


class AuditTraceSelectors:

    @staticmethod
    def by_correlation(correlation_id):
        return AuditEvent.objects.filter(
            correlation_id=correlation_id
        ).order_by("timestamp")

    @staticmethod
    def object_timeline(object_type, object_id):
        return AuditEvent.objects.filter(
            object_type=object_type,
            object_id=object_id
        ).order_by("timestamp")

    @staticmethod
    def actor_lifecycle(actor_id):
        return AuditEvent.objects.filter(
            actor_id=actor_id
        ).order_by("timestamp")