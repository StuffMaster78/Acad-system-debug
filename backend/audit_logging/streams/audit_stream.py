from audit_logging.models.audit_event import AuditEvent


class AuditStream:

    @staticmethod
    def latest(limit: int = 50):
        return AuditEvent.objects.order_by("-occurred_at")[:limit]

    @staticmethod
    def since(timestamp):
        return AuditEvent.objects.filter(
            occurred_at__gte=timestamp
        ).order_by("occurred_at")