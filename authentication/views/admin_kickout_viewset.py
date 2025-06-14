# viewsets/admin_kickout_viewset.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from authentication.services.kickout_service import KickoutService
from authentication.serializers import (
    AdminKickoutSerializer
)

User = get_user_model()


class AdminKickoutViewSet(viewsets.ViewSet):
    """
    Allows admins to kick users from sessions.
    """

    permission_classes = [IsAdminUser]

    def create(self, request):
        """
        POST /api/kickout/
        {
            "user_id": 3,
            "ip_address": "192.168.0.1",     # Optional
            "reason": "Suspicious activity"  # Optional
        }
        """
        serializer = AdminKickoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["target_user"]
        ip_address = serializer.validated_data.get("ip_address")
        reason = serializer.validated_data.get("reason", "")
        website = request.user.website  # for multitenancy

        service = KickoutService(website)
        sessions_killed = service.kick_user(
            user=user,
            performed_by=request.user,
            ip_address=ip_address,
            reason=reason
        )

        return Response({
            "detail": f"{sessions_killed} session(s) terminated.",
            "user": {
                "id": user.id,
                "username": user.username
            },
            "reason": reason or "unspecified",
            "sessions_killed": sessions_killed
        }, status=status.HTTP_200_OK)