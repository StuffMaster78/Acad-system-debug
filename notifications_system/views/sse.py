# notifications_system/views/sse.py
import redis
import json
from django.http import StreamingHttpResponse
from django.conf import settings

def event_stream():
    r = redis.StrictRedis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    pubsub.subscribe("notifications")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            yield f"event: {data['type']}\ndata: {json.dumps(data['payload'])}\n\n"

def sse_notifications(request):
    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    return response