from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from event_system.services.event_metrics_service import EventMetricsService
from event_system.api.serializers.event_metrics_serializer import (
    EventMetricsSerializer,
)


class EventMetricsAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        metrics = EventMetricsService.snapshot()

        return Response(
            EventMetricsSerializer(metrics).data
        )