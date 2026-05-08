import django_filters

from audit_logging.models.audit_event import AuditEvent
from audit_logging.models.audit_dead_letter import (
    AuditDeadLetter,
)


class AuditEventFilter(django_filters.FilterSet):

    occurred_after = django_filters.IsoDateTimeFilter(
        field_name="occurred_at",
        lookup_expr="gte",
    )

    occurred_before = django_filters.IsoDateTimeFilter(
        field_name="occurred_at",
        lookup_expr="lte",
    )

    class Meta:
        model = AuditEvent

        fields = {
            "status": ["exact"],
            "severity": ["exact"],
            "is_sensitive": ["exact"],
            "action": ["exact", "icontains"],
            "actor_id": ["exact"],
            "object_type": ["exact"],
            "object_id": ["exact"],
            "correlation_id": ["exact"],
            "span_id": ["exact"],
            "service_name": ["exact"],
        }


class AuditDeadLetterFilter(django_filters.FilterSet):

    created_after = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )

    created_before = django_filters.IsoDateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    class Meta:
        model = AuditDeadLetter

        fields = {
            "is_resolved": ["exact"],
            "retry_count": ["exact", "gte"],
            "event_id": ["exact"],
        }