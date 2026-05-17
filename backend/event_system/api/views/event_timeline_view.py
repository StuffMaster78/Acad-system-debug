from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from event_system.services.event_timeline_service import EventTimelineService
from event_system.api.serializers.event_timeline_serializer import (
    EventTimelineSerializer,
)


class EventTimelineAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        event_id = request.query_params.get("event_id")
        correlation_id = request.query_params.get("correlation_id")

        if not event_id and not correlation_id:
            return Response(
                {"error": "event_id or correlation_id is required"},
                status=400,
            )

        timeline = EventTimelineService.build_event_timeline(
            event_id=event_id,
            correlation_id=correlation_id,
        )

        return Response(
            EventTimelineSerializer(timeline, many=True).data
        )