import csv
import io

from django.db.models import Count, QuerySet
from django.http import StreamingHttpResponse
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    # --------------------------------------------------
    # Trust Center: sensitive summary
    # --------------------------------------------------

    @action(detail=False, methods=["get"], url_path="sensitive-summary")
    def sensitive_summary(self, request):
        """
        Aggregated counts for the Trust Center dashboard.
        Returns event counts by severity, sensitivity_level, and top actions.
        """
        qs = self.get_queryset()
        params = request.query_params

        # Optional time window (default last 30 days)
        days = int(params.get("days", 30))
        since = timezone.now() - timezone.timedelta(days=days)
        qs = qs.filter(occurred_at__gte=since)

        sensitive_qs = qs.filter(is_sensitive=True)

        by_severity = dict(
            qs.values_list("severity")
            .annotate(n=Count("id"))
            .values_list("severity", "n")
        )
        by_sensitivity = dict(
            sensitive_qs.exclude(sensitivity_level__isnull=True)
            .values_list("sensitivity_level")
            .annotate(n=Count("id"))
            .values_list("sensitivity_level", "n")
        )
        top_actions = list(
            qs.values_list("action")
            .annotate(n=Count("id"))
            .order_by("-n")
            .values_list("action", "n")[:15]
        )
        recent_critical = list(
            qs.filter(severity__in=["warning", "critical"])
            .order_by("-occurred_at")
            .values("id", "action", "object_type", "object_id",
                    "actor_id", "severity", "occurred_at", "metadata")[:20]
        )

        return Response({
            "window_days": days,
            "total_events": qs.count(),
            "sensitive_events": sensitive_qs.count(),
            "by_severity": by_severity,
            "by_sensitivity_level": by_sensitivity,
            "top_actions": [{"action": a, "count": n} for a, n in top_actions],
            "recent_critical": recent_critical,
        })

    # --------------------------------------------------
    # Per-object timeline
    # --------------------------------------------------

    @action(detail=False, methods=["get"], url_path="object-timeline")
    def object_timeline(self, request):
        """
        Ordered timeline for a specific object (object_type + object_id).
        Used by order detail, user detail, and config audit drawers.
        """
        object_type = request.query_params.get("object_type")
        object_id = request.query_params.get("object_id")
        if not object_type or not object_id:
            return Response(
                {"detail": "object_type and object_id are required."},
                status=400,
            )
        qs = (
            self.get_queryset()
            .filter(object_type=object_type, object_id=str(object_id))
            .order_by("occurred_at")
        )
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(qs[:200], many=True, context={"request": request})
        return Response({"object_type": object_type, "object_id": object_id, "events": serializer.data})

    # --------------------------------------------------
    # CSV export
    # --------------------------------------------------

    @action(detail=False, methods=["get"], url_path="export")
    def export(self, request):
        """
        Stream filtered audit events as a CSV download.
        Respects all filters from the standard list endpoint.
        Capped at 10,000 rows for safety.
        """
        qs = self.filter_queryset(self.get_queryset())[:10_000]

        def rows():
            buf = io.StringIO()
            writer = csv.writer(buf)
            writer.writerow([
                "id", "occurred_at", "action", "actor_id",
                "object_type", "object_id", "severity",
                "is_sensitive", "sensitivity_level",
                "service_name", "status",
            ])
            yield buf.getvalue()
            buf.truncate(0)
            buf.seek(0)

            for ev in qs.iterator(chunk_size=500):
                writer.writerow([
                    ev.id, ev.occurred_at.isoformat(),
                    ev.action, ev.actor_id,
                    ev.object_type, ev.object_id,
                    ev.severity, ev.is_sensitive,
                    ev.sensitivity_level, ev.service_name,
                    ev.status,
                ])
                yield buf.getvalue()
                buf.truncate(0)
                buf.seek(0)

        filename = f"audit-export-{timezone.now().strftime('%Y%m%d-%H%M%S')}.csv"
        response = StreamingHttpResponse(rows(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response