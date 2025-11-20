from django.conf import settings
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from audit_logging.models import AuditLogEntry
from audit_logging.serializers import AuditLogEntrySerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class AuditLogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API endpoint for viewing audit log entries.
    Admin-only access.
    """
    queryset = AuditLogEntry.objects.select_related("actor").all()
    serializer_class = AuditLogEntrySerializer
    permission_classes = [permissions.IsAdminUser]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = [
        "action", "actor", "target",
        "target_id", "request_id"
    ]
    search_fields = [
        "action", "target", "actor__username",
        "notes", "metadata", "metadata__note",
        "ip_address", "user_agent", "metadata__status"
    ]
    ordering_fields = [
        "timestamp", "action", "actor", "target"
    ]
    ordering = ["-timestamp"]


    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Support impersonation via query param or header
        impersonated_id = self.request.query_params.get("impersonated_user_id") \
            or self.request.headers.get("X-Original-User")

        if impersonated_id and user.is_staff:
            return queryset.filter(actor__id=impersonated_id)
        
        if self.request.query_params.get("mine") == "true":
            return queryset.filter(actor=self.request.user)
        return queryset

    @action(detail=False, methods=["get"], url_path="my-logs")
    def my_logs(self, request):
        """
        Custom route to get logs for the current user.
        Equivalent to ?mine=true but more explicit.
        """
        logs = self.queryset.filter(actor=request.user)
        page = self.paginate_queryset(logs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
