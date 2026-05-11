# tips/api/views/admin_tip_outbox_views.py

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from tips.models.tip_outbox_event import TipOutboxEvent

from tips.services.tip_outbox_requeue_service import (
    TipOutboxRequeueService,
)


class AdminOutboxEventListAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        events = (
            TipOutboxEvent.objects
            .filter(topic__icontains="tip")
            .order_by("-created_at")[:100]
        )

        data = [
            {
                "id": event.pk,
                "topic": event.topic,
                "status": event.status,
                "created_at": event.created_at,
            }
            for event in events
        ]

        return Response(data)


class AdminRequeueOutboxAPIView(APIView):

    permission_classes = [IsAdminUser]

    def post(self, request, pk):

        event = TipOutboxEvent.objects.get(pk=pk)

        TipOutboxRequeueService.requeue(
            outbox_event=event,
            triggered_by=request.user,
        )

        return Response(
            {"detail": "event requeued"}
        )