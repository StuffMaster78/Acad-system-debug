import time
from dataclasses import dataclass
from django.db.models import Count, Avg
from django.utils import timezone

from event_system.models.event_outbox import EventOutbox, EventStatus

@dataclass
class EventMetrics:
    event_type: str
    duration_ms: int
    status: str


class EventMetricsService:

    @staticmethod
    def start():
        return time.time()

    @staticmethod
    def end(start_time: float) -> int:
        return int((time.time() - start_time) * 1000)
    
    @classmethod
    def snapshot(cls) -> dict:
        """
        Returns real-time system health metrics.
        """

        base_qs = EventOutbox.objects.all()

        total = base_qs.count()

        processed = base_qs.filter(status=EventStatus.PROCESSED).count()
        failed = base_qs.filter(status=EventStatus.FAILED).count()
        dead_letter = base_qs.filter(status=EventStatus.DEAD_LETTER).count()
        ignored = base_qs.filter(status=EventStatus.IGNORED).count()

        processing_rate = (processed / total) if total else 0.0
        failure_rate = (failed / total) if total else 0.0

        # optional latency if you track timestamps properly
        avg_processing_time = base_qs.filter(
            processed_at__isnull=False
        ).aggregate(
            avg=Avg("attempts")
        )["avg"]

        return {
            "total_events": total,
            "processed": processed,
            "failed": failed,
            "dead_letter": dead_letter,
            "ignored": ignored,
            "processing_rate": processing_rate,
            "failure_rate": failure_rate,
            "avg_processing_time_ms": float(avg_processing_time) if avg_processing_time else None,
            "last_updated": timezone.now(),
        }