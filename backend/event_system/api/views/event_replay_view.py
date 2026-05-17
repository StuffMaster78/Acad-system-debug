from typing import cast
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from event_system.models.event_outbox import EventOutbox
from event_system.services.event_inspection_service import(
    EventInspectionService,
)
from event_system.api.serializers.event_replay_serializer import (
    EventReplaySerializer,
)
from event_system.api.serializers.event_outbox_serializer import (
    EventOutboxSerializer,
)

class EventReplayAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = EventReplaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated = cast(dict, serializer.validated_data)

        event_id = validated["event_id"]

        EventInspectionService.replay_event(str(event_id))

        return Response({
            "status": "replayed",
            "event_id": str(event_id)
        })