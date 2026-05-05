from __future__ import annotations

from django.http import StreamingHttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from communications.sse.event_bus import CommunicationSSEEventBus
from communications.sse.event_bus import format_sse_event
from communications.sse.event_formatter import (
    CommunicationSSEEventFormatter,
)
from communications.api.throttles import CommunicationSSEThrottle

class CommunicationSSEView(APIView):
    """
    Stream communication events using Server Sent Events.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [CommunicationSSEThrottle]

    def get(self, request):
        """
        Open SSE stream.
        """
        user = request.user

        def event_stream():
            for item in CommunicationSSEEventBus.subscribe():
                event_name = item.get("event", "message")
                data = item.get("data", {})

                if not _user_can_receive_event(user=user, data=data):
                    continue

                rendered = CommunicationSSEEventFormatter.format(
                    event=event_name,
                    data=data,
                )

                yield rendered.encode("utf-8")

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


def _user_can_receive_event(*, user, data: dict) -> bool:
    """
    Return whether the user can receive this SSE event.
    """
    meta = data.get("meta", {})
    recipient_ids = meta.get("recipient_user_ids")

    if recipient_ids is None:
        return False

    return user.id in recipient_ids