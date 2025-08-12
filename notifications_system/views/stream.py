# notifications/views/stream.py
import json
import time
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from notifications_system.events import NotificationBroadcaster

@method_decorator(login_required, name='dispatch')
def notification_event_stream(request):
    user = request.user

    def event_generator():
        """Generates SSE events for the user's notifications."""
        # Subscribe to user's notification channel
        channel = NotificationBroadcaster.subscribe(user.id)

        try:
            while True:
                data = channel.get(block=True, timeout=30)  # blocks until data or timeout
                if data:
                    yield f"data: {json.dumps(data)}\n\n"
        except GeneratorExit:
            NotificationBroadcaster.unsubscribe(user.id)
        except Exception:
            yield 'event: ping\ndata: {}\n\n'

    response = StreamingHttpResponse(
        event_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response