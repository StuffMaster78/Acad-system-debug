from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsAdminOrSuperAdmin


from django.shortcuts import get_object_or_404

from event_system.models.event_outbox import EventOutbox
from event_system.services.event_timeline_service import EventTimelineService
from event_system.api.serializers.event_timeline_serializer import EventTimelineSerializer
from event_system.api.serializers.event_outbox_serializer import EventOutboxSerializer


class EventDetailAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request, event_id: str):
        event = get_object_or_404(EventOutbox, id=event_id)

        timeline = EventTimelineService.get_event_timeline(event_id=event_id)

        return Response({
            "event": EventOutboxSerializer(instance=event).data,
            "timeline": EventTimelineSerializer(instance=timeline, many=True).data,
        })