# tips/api/views/admin_tip_audit_views.py


from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminOrSuperAdmin

from audit_logging.models.audit_event import (
    AuditEvent,
)


class AdminTipAuditAPIView(APIView):

    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):

        logs = (
            AuditEvent.objects
            .filter(action__icontains="tip")
            .order_by("-created_at")[:200]
        )

        data = [
            {
                "id": log.pk,
                "action": log.action,
                "actor_id": getattr(
                    log.actor,
                    "pk",
                    None,
                ),
                "created_at": log.created_at,
                "metadata": log.metadata,
            }
            for log in logs
        ]

        return Response(data)