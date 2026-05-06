from rest_framework.views import APIView
from rest_framework.response import Response

from audit_logging.services.metrics_service import AuditMetricsService
from audit_logging.selectors.audit_selectors import AuditSelectors


class AuditHealthView(APIView):
    """
    System health overview for audit logging.
    """

    def get(self, request):
        service = AuditMetricsService()

        return Response({
            "total_events": service.get_event_volume(),
            "dlq_pending": service.get_failure_count(),
            "dlq_resolved": service.get_resolved_failures(),
            "retry_pressure": service.get_retry_pressure(),
        })


class AuditRecentView(APIView):
    """
    Recent audit activity (debug/admin use).
    """

    def get(self, request):
        events = AuditSelectors.feed(limit=50)

        return Response([
            {
                "action": e.action,
                "actor_id": e.actor_id,
                "object_type": e.object_type,
                "object_id": e.object_id,
                "timestamp": e.timestamp,
                "is_sensitive": e.is_sensitive,
            }
            for e in events
        ])