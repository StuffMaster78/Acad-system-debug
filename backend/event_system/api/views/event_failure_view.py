from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from event_system.services.event_failure_service import EventFailureService
from event_system.api.serializers.event_failure_serializer import (
    EventFailureSerializer,
)


class EventFailureAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, event_id: str):
        failures = EventFailureService.get_failures(event_id)

        return Response(
            EventFailureSerializer(failures, many=True).data
        )