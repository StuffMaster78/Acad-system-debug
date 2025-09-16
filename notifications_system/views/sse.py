# notifications_system/views/sse.py
import redis
import json
import time
from django.http import StreamingHttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def event_stream(request):
    user_id = request.user.id if request.user.is_authenticated else None
    r = redis.StrictRedis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    pubsub.subscribe(f"sse:user:{user_id}")

    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            yield f"event: {data['type']}\ndata: {json.dumps(data['payload'])}\n\n"
        time.sleep(0.05)

    return StreamingHttpResponse(
        event_stream(request),
        content_type="text/event-stream"
    )

@login_required
def sse_notifications(request):
    response = StreamingHttpResponse(
        event_stream(request),
        content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    return response