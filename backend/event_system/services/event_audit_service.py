from django.core.cache import cache

from event_system.models.event_audit_log import EventAuditLog


class EventAuditService:
    """
    Dual-layer audit system:

    - Cache: fast inspection / debugging / UI telemetry
    - DB: durable audit trail for compliance + replay analysis
    """

    @staticmethod
    def log(
        *,
        event_id: str,
        event_type: str,
        stage: str,
        message: str = "",
        worker_id: str | None = None,
        duration_ms: float | None = None,
        payload: dict | None = None,
        correlation_id: str | None = None,
        retry_count: int | None = None,
        event_status: str | None = None,
    ) -> None:
        # 1. FAST LAYER (ephemeral observability)
        cache_key = f"audit:{event_id}:{stage}"

        cache.set(
            cache_key,
            {
                "event_type": event_type,
                "stage": stage,
                "message": message,
                "duration_ms": duration_ms,
                "payload": payload or {},
                "worker_id": worker_id,
                "correlation_id": correlation_id,
                "retry_count": retry_count,
                "event_status": event_status,
            },
            timeout=86400,
        )

        # 2. DURABLE LAYER (source of truth)
        EventAuditLog.objects.create(
            event_id=event_id,
            event_type=event_type,
            stage=stage,
            message=message,
            worker_id=worker_id,
            duration_ms=duration_ms,
            correlation_id=correlation_id,
            retry_count=retry_count,
            event_status=event_status,
        )