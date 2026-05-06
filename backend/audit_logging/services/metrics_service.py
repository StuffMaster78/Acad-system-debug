from django.db.models import Count, Q
from audit_logging.storage.models import AuditEvent
from audit_logging.storage.models_dlq import AuditDeadLetter


class AuditMetricsService:
    """
    Lightweight operational metrics for audit system health.
    """

    def get_event_volume(self):
        return AuditEvent.objects.count()

    def get_recent_activity(self, limit=100):
        return AuditEvent.objects.all().order_by("-timestamp")[:limit]

    def get_failure_count(self):
        return AuditDeadLetter.objects.filter(is_resolved=False).count()

    def get_resolved_failures(self):
        return AuditDeadLetter.objects.filter(is_resolved=True).count()

    def get_retry_pressure(self):
        return AuditDeadLetter.objects.aggregate(
            total=Count("id"),
            stuck=Count("id", filter=Q(retry_count__gte=3, is_resolved=False)),
        )