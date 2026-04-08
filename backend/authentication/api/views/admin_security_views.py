from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.permissions.impersonation_permissions import (
    NotImpersonatingPermission,
)
from authentication.api.serializers.admin_security_serializers import (
    AdminKickoutResponseSerializer,
    AdminKickoutSerializer,
    AdminUnlockResponseSerializer,
)
from authentication.services.lockout_admin_service import (
    LockoutAdminService,
)

User = get_user_model()


class AdminUnlockUserView(APIView):
    """
    Unlock a target user's account and clear failed login state.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, user_id, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = User.objects.filter(
            pk=user_id,
            website=website,
        ).first()

        if target_user is None:
            return Response(
                {"detail": "Target user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        LockoutAdminService.unlock_user(
            target_user=target_user,
            website=website,
            performed_by=request.user,
        )

        serializer = AdminUnlockResponseSerializer(
            {
                "success": True,
                "user_id": target_user.pk,
                "message": "User unlocked successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminKickoutUserView(APIView):
    """
    Revoke all active sessions for a target user.
    """

    permission_classes = [
        IsAuthenticated,
        IsAdminUser,
        NotImpersonatingPermission,
    ]

    def post(self, request, user_id, *args, **kwargs):
        serializer = AdminKickoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = cast(
            dict[str, Any],
            serializer.validated_data,
        )

        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = User.objects.filter(
            pk=user_id,
            website=website,
        ).first()

        if target_user is None:
            return Response(
                {"detail": "Target user not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        revoked_count = LockoutAdminService.kickout_user(
            target_user=target_user,
            website=website,
            performed_by=request.user,
            reason=validated_data.get("reason", ""),
        )

        serializer = AdminKickoutResponseSerializer(
            {
                "success": True,
                "user_id": target_user.pk,
                "revoked_sessions_count": revoked_count,
                "message": "User sessions revoked successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)