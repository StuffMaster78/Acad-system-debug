import json
import time

from django.http import HttpResponseForbidden, StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views import View

from writer_management.services.dashboard_realtime_service import (
    WriterDashboardRealtimeService,
)


@method_decorator(login_required, name="dispatch")
class WriterDashboardRealtimeStream(View):
    """
    Server-Sent Events stream that pushes real-time widget data to writers.
    """

    stream_interval_seconds = 15

    def get(self, request):
        if getattr(request.user, "role", None) != "writer":
            return HttpResponseForbidden("Writer access only.")

        def event_stream():
            try:
                while True:
                    payload = WriterDashboardRealtimeService.build_payload(request.user)
                    event = "writer_dashboard"
                    yield f"event: {event}\ndata: {json.dumps(payload)}\n\n"
                    time.sleep(self.stream_interval_seconds)
            except GeneratorExit:
                return

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        return response

