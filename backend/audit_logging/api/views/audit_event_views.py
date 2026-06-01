from django.db.models import QuerySet

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated

from audit_logging.api.filters.audit_filters import AuditEventFilter
from audit_logging.api.pagination.audit_pagination import (
    AuditCursorPagination,
)
from audit_logging.api.permissions.audit_permissions import (
    CanViewAuditLogs,
)
from audit_logging.api.serializers.audit_event_serializer import (
    AuditEventSerializer,
    SensitiveAuditEventSerializer,
)
from audit_logging.models.audit_event import AuditEvent

from audit_logging.services.query.audit_query_policy import (
    AuditQueryPolicy,
)
from audit_logging.services.query.audit_query_types import (
    AuditEventQuery,
)


class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):

    pagination_class = AuditCursorPagination

    permission_classes = (
        IsAuthenticated,
        CanViewAuditLogs,
    )

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_class = AuditEventFilter

    ordering = (
        "-occurred_at",
    )

    search_fields = (
        "action",
        "object_type",
        "object_id",
        "correlation_id",
        "span_id",
    )

    # --------------------------------------------------
    # Queryset
    # --------------------------------------------------

    def get_queryset( # type: ignore[override]
        self,
    ) -> QuerySet[AuditEvent]:

        params = getattr(
            self.request,
            "query_params",
            {},
        )

        website = getattr(
            self.request,
            "website",
            None,
        )

        query = AuditEventQuery(
            website_id=getattr(website, "id", None),
            actor_id=params.get("actor_id"),
            action=params.get("action"),
            action_contains=params.get("search"),
            object_type=params.get("object_type"),
            object_id=params.get("object_id"),
            correlation_id=params.get("correlation_id"),
            span_id=params.get("span_id"),
            status=params.get("status"),
            limit=int(params.get("limit", 100)),
        )

        policy = AuditQueryPolicy(
            user=self.request.user,
        )

        return policy.search_events(query)

    # --------------------------------------------------
    # Serializer
    # --------------------------------------------------

    def get_serializer_class( # type: ignore[override]
        self,
    ):

        policy = AuditQueryPolicy(
            user=self.request.user,
        )

        if policy.can_view_sensitive_events():
            return SensitiveAuditEventSerializer

        return AuditEventSerializer