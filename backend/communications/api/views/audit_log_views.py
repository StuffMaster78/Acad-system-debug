from __future__ import annotations

from rest_framework.viewsets import ReadOnlyModelViewSet

from communications.api.permissions import CanViewCommunicationAuditLogs
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationAuditLogSerializer
from communications.models.audit import CommunicationAuditLog
from communications.selectors.audit_log_selectors import (
    CommunicationAuditLogSelector,
)
from communications.api.pagination import CommunicationDefaultPagePagination

class CommunicationAuditLogViewSet(ReadOnlyModelViewSet):
    """
    API endpoints for communication audit logs.
    """

    serializer_class = CommunicationAuditLogSerializer
    permission_classes = [
        IsAuthenticatedForCommunications,
        CanViewCommunicationAuditLogs,
    ]
    pagination_class = CommunicationDefaultPagePagination

    def get_queryset(self): # type: ignore[override]
        """
        Return audit logs for admin and superadmin users.
        """
        website = getattr(self.request, "website", None)

        return (
            CommunicationAuditLogSelector.for_website(website=website)
            .select_related("website", "thread", "message", "actor")
            .order_by("-created_at", "-id")
        )