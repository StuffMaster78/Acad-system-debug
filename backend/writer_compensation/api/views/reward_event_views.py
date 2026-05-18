from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from event_system.models.event_outbox import (
    EventOutbox,
)


class RewardEventOutboxView(
    APIView,
):
    """
    Reward-related outbox events.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        *args,
        **kwargs,
    ) -> Response:
        """
        Return reward outbox events.
        """

        events = (
            EventOutbox.objects
            .filter(
                event_type__startswith="reward.",
            )
            .order_by(
                "-created_at",
            )[:100]
        )

        payload = [
            {
                "id": event.pk,
                "event_type": (
                    event.event_type
                ),
                "aggregate_id": (
                    event.aggregate_id
                ),
                "payload": event.payload,
                "created_at": (
                    event.created_at
                ),
            }
            for event in events
        ]

        return Response(
            payload,
        )