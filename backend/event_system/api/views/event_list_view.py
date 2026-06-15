from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsAdminOrSuperAdmin


from event_system.models.event_outbox import EventOutbox
from event_system.api.serializers.event_outbox_serializer import (
    EventOutboxSerializer,
)

class EventListAPIView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        events = EventOutbox.objects.order_by("-created_at")[:100]
        serializer = EventOutboxSerializer(events, many=True)
        return Response(serializer.data)