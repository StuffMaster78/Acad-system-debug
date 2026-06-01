from dataclasses import dataclass

from django.db.models import QuerySet

from audit_logging.models.audit_dead_letter import AuditDeadLetter
from audit_logging.models.audit_event import AuditEvent

from audit_logging.services.query.audit_query_service import (
    AuditQueryService,
)
from audit_logging.services.query.audit_query_types import (
    AuditEventQuery,
)


@dataclass(frozen=True)
class AuditQueryPolicy:
    """
    Single authorization enforcement layer
    for ALL audit queries.

    RULES:
    - no writes
    - no side effects
    - deterministic
    - tenant-safe
    """

    user: object

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    def search_events(
        self,
        query: AuditEventQuery,
    ) -> QuerySet[AuditEvent]:

        qs = AuditQueryService.search_events(query)

        return self._apply_sensitivity(qs)

    def timeline_for_object(
        self,
        object_type: str,
        object_id: str,
    ) -> QuerySet[AuditEvent]:

        qs = AuditQueryService.timeline_for_object(
            object_type=object_type,
            object_id=object_id,
        )

        return self._apply_sensitivity(qs)

    def timeline_for_actor(
        self,
        actor_id: int,
    ) -> QuerySet[AuditEvent]:

        qs = AuditQueryService.timeline_for_actor(
            actor_id=actor_id,
        )

        return self._apply_sensitivity(qs)

    def trace_by_correlation(
        self,
        correlation_id: str,
    ) -> QuerySet[AuditEvent]:

        qs = AuditQueryService.trace_by_correlation(
            correlation_id=correlation_id,
        )

        return self._apply_sensitivity(qs)

    # --------------------------------------------------
    # DLQ
    # --------------------------------------------------

    def user_dlq_backlog(
        self,
    ) -> QuerySet[AuditDeadLetter]:

        return AuditQueryService.dlq_backlog()

    def user_dlq_stuck(
        self,
    ) -> QuerySet[AuditDeadLetter]:

        return AuditQueryService.dlq_stuck()

    def user_dlq_high_risk(
        self,
    ) -> QuerySet[AuditDeadLetter]:

        return AuditQueryService.dlq_high_risk()

    def user_visible_events(self, qs):
        return self._apply_sensitivity(qs)

    # --------------------------------------------------
    # INTERNAL
    # --------------------------------------------------

    def can_view_sensitive_events(self) -> bool:

        if getattr(self.user, "is_superuser", False):
            return True

        return bool(
            self.user.has_perm( # type: ignore[attr-defined]
                "audit_logging.view_sensitive_audit_logs"
            )
        )

    def _apply_sensitivity(
        self,
        qs: QuerySet[AuditEvent],
    ) -> QuerySet[AuditEvent]:

        if self.can_view_sensitive_events():
            return qs

        return qs.filter(is_sensitive=False)