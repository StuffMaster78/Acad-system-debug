from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.logout_serializers import (
    LogoutAllOthersResponseSerializer,
    LogoutResponseSerializer,
)
from authentication.services.logout_service import LogoutService


class LogoutView(APIView):
    """
    Revoke the current authenticated session.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        success = LogoutService.logout_current_session(
            request=request,
        )

        serializer = LogoutResponseSerializer(
            {
                "success": success,
                "message": "Logged out successfully.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutAllOthersView(APIView):
    """
    Revoke all sessions except the current authenticated session.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        revoked_count = LogoutService.logout_all_other_sessions(
            request=request,
        )

        serializer = LogoutAllOthersResponseSerializer(
            {
                "success": True,
                "revoked_sessions_count": revoked_count,
                "message": "All other sessions were logged out.",
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)