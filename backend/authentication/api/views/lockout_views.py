from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.lockout_serializers import (
    LockoutStatusResponseSerializer,
)
from authentication.selectors.lockout_selectors import (
    get_active_lockout,
)


class LockoutStatusView(APIView):
    """
    Return current lockout status for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        if website is None:
            return Response(
                {"detail": "Website context is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lockout = get_active_lockout(
            user=request.user,
            website=website,
        )

        if lockout is None:
            serializer = LockoutStatusResponseSerializer(
                {
                    "is_locked": False,
                    "locked_until": None,
                    "remaining_seconds": None,
                    "reason": "",
                }
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        locked_until = getattr(lockout, "locked_until", None)
        remaining_seconds = None

        if locked_until is not None:
            remaining_seconds = max(
                int((locked_until - timezone.now()).total_seconds()),
                0,
            )

        serializer = LockoutStatusResponseSerializer(
            {
                "is_locked": True,
                "locked_until": locked_until,
                "remaining_seconds": remaining_seconds,
                "reason": getattr(lockout, "reason", ""),
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)