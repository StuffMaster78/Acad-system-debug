from rest_framework import viewsets, permissions, filters
from audit_logging.models import AuditLogEntry
from audit_logging.serializers import AuditLogEntrySerializer


class AuditLogEntryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLogEntry.objects.all()
    serializer_class = AuditLogEntrySerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['action', 'target', 'actor__username']
    ordering_fields = ['timestamp', 'action']
    ordering = ['-timestamp']
