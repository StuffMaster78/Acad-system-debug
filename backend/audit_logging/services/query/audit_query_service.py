from django.db.models import QuerySet

from audit_logging.models.audit_event import AuditEvent
from audit_logging.models.audit_dead_letter import AuditDeadLetter
from audit_logging.services.query.audit_query_types import AuditEventQuery


class AuditQueryService:
    """
    Single authoritative query layer for audit system.

    RULES:
    - no business logic
    - no side effects
    - all external queries MUST pass through this layer
    """

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    @staticmethod
    def search_events(query: AuditEventQuery) -> QuerySet[AuditEvent]:

        qs = AuditEvent.objects.all()

        if query.website_id:
            qs = qs.filter(website_id=query.website_id)

        if query.actor_id:
            qs = qs.filter(actor_id=query.actor_id)

        if query.action:
            qs = qs.filter(action=query.action)

        if query.action_contains:
            qs = qs.filter(action__icontains=query.action_contains)

        if query.object_type:
            qs = qs.filter(object_type=query.object_type)

        if query.object_id:
            qs = qs.filter(object_id=query.object_id)

        if query.correlation_id:
            qs = qs.filter(correlation_id=query.correlation_id)

        if query.span_id:
            qs = qs.filter(span_id=query.span_id)

        if query.is_sensitive is not None:
            qs = qs.filter(is_sensitive=query.is_sensitive)

        if query.status:
            qs = qs.filter(status=query.status)

        if query.occurred_after:
            qs = qs.filter(occurred_at__gte=query.occurred_after)

        if query.occurred_before:
            qs = qs.filter(occurred_at__lte=query.occurred_before)

        qs = qs.order_by("-occurred_at")

        return qs[: query.limit]

    # --------------------------------------------------
    # TIMELINE
    # --------------------------------------------------

    @staticmethod
    def timeline_for_object(object_type: str, object_id: str) -> QuerySet[AuditEvent]:
        return (
            AuditEvent.objects
            .filter(object_type=object_type, object_id=object_id)
            .order_by("occurred_at")
        )

    @staticmethod
    def timeline_for_actor(actor_id: int) -> QuerySet[AuditEvent]:
        return (
            AuditEvent.objects
            .filter(actor_id=actor_id)
            .order_by("occurred_at")
        )

    # --------------------------------------------------
    # TRACE
    # --------------------------------------------------

    @staticmethod
    def trace_by_correlation(correlation_id: str) -> QuerySet[AuditEvent]:
        return (
            AuditEvent.objects
            .filter(correlation_id=correlation_id)
            .order_by("occurred_at")
        )

    # --------------------------------------------------
    # DLQ
    # --------------------------------------------------

    @staticmethod
    def dlq_backlog() -> QuerySet[AuditDeadLetter]:
        return (
            AuditDeadLetter.objects
            .filter(is_resolved=False)
            .order_by("created_at")
        )

    @staticmethod
    def dlq_stuck() -> QuerySet[AuditDeadLetter]:
        return (
            AuditDeadLetter.objects
            .filter(is_resolved=False, retry_count__gte=3)
            .order_by("created_at")
        )

    @staticmethod
    def dlq_high_risk() -> QuerySet[AuditDeadLetter]:
        return (
            AuditDeadLetter.objects
            .filter(is_resolved=False)
            .order_by("created_at")
        )

    # --------------------------------------------------
    # SAFETY LAYER (DO NOT SKIP IN API)
    # --------------------------------------------------

    @staticmethod
    def apply_sensitivity_filter(qs: QuerySet, user):
        if user.is_superuser:
            return qs

        if user.has_perm("audit_logging.view_sensitive_audit_logs"):
            return qs

        return qs.filter(is_sensitive=False)