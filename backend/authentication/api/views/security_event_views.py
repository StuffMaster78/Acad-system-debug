from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.api.serializers.security_events_serializers import (
    SecurityEventSerializer,
)
from authentication.selectors.security_event_selectors import (
    list_user_security_events,
)


class SecurityEventListView(APIView):
    """
    List security events for the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        website = getattr(request, "website", None)
        events = list_user_security_events(
            user=request.user,
            website=website,
        )
        serializer = SecurityEventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)