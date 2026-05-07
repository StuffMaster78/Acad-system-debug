from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

from audit_logging.models.audit_event import AuditEvent
from audit_logging.models.audit_dead_letter import AuditDeadLetter


class AuditMetricsService:
    """
    Lightweight operational metrics for audit system health.

    All metrics are:
    - tenant-aware (website scoped)
    - time-aware (optional window)
    - safe for dashboards
    """

    def __init__(self, website=None):
        self.website = website

    # -------------------------
    # Helpers
    # -------------------------
    def _event_qs(self):
        qs = AuditEvent.objects.all()
        if self.website:
            qs = qs.filter(website=self.website)
        return qs

    def _dlq_qs(self):
        qs = AuditDeadLetter.objects.all()
        return qs

    # -------------------------
    # Core metrics
    # -------------------------
    def get_event_volume(self):
        return self._event_qs().count()

    def get_recent_activity(self, limit: int = 100):
        return (
            self._event_qs()
            .order_by("-timestamp")[:limit]
        )

    # -------------------------
    # Failure metrics
    # -------------------------
    def get_failure_count(self):
        return self._dlq_qs().filter(is_resolved=False).count()

    def get_resolved_failures(self):
        return self._dlq_qs().filter(is_resolved=True).count()

    # -------------------------
    # System pressure
    # -------------------------
    def get_retry_pressure(self):
        return self._dlq_qs().aggregate(
            total=Count("id"),
            stuck=Count(
                "id",
                filter=Q(retry_count__gte=3, is_resolved=False),
            ),
        )

    # -------------------------
    # Time-based insight (NEW)
    # -------------------------
    def get_last_24h_volume(self):
        since = timezone.now() - timedelta(hours=24)
        return self._event_qs().filter(timestamp__gte=since).count()

    def get_last_24h_failures(self):
        since = timezone.now() - timedelta(hours=24)
        return self._dlq_qs().filter(created_at__gte=since).count()