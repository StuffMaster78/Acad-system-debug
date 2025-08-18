# notifications_system/views/streams.py
import time
import json
from django.http import StreamingHttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from notifications_system.events import NotificationBroadcaster


@method_decorator(login_required, name='dispatch')
def notification_event_stream(request):
    user = request.user

    def event_generator():
        """Generates SSE events for the user's notifications."""
        NotificationBroadcaster.subscribe(user.id)

        try:
            while True:
                message = NotificationBroadcaster.get_message(user.id, timeout=30)
                if message:
                    yield f"data: {json.dumps(message)}\n\n"
                else:
                    # heartbeat so browser doesn’t close connection
                    yield "event: ping\ndata: {}\n\n"
        except GeneratorExit:
            NotificationBroadcaster.unsubscribe(user.id)

    response = StreamingHttpResponse(
        event_generator(),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"  # useful with Nginx
    return response


# @login_required
# def sse_notifications(request):
#     """
#     SSE endpoint that streams notifications for logged-in user.
#     """
#     def event_stream():
#         # In real world, you'd pull from Redis, DB, or message queue
#         # Here, a dummy loop (send every 5 seconds)
#         for i in range(100):
#             time.sleep(5)
#             yield f"data: Notification {i} for {request.user.username}\n\n"

#     response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
#     response['Cache-Control'] = 'no-cache'
#     return response


# @login_required
# def poll_notifications(request):
#     """
#     Polling endpoint: returns latest notifications as JSON.
#     """
#     # Example: fetch last 5 from DB (replace with real model)
#     # notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
#     # For demo, fake response:
#     data = [
#         {"message": "You have a new task!", "id": 1},
#         {"message": "Order #42 updated!", "id": 2},
#     ]
#     return JsonResponse({"notifications": data})