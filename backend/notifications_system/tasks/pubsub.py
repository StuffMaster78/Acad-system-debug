import json
import redis
from celery import shared_task
from django.conf import settings

# r = redis.StrictRedis.from_url(settings.REDIS_URL)
r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    password=settings.REDIS_PASSWORD,  # <-- important
)

@shared_task
def publish_notification(event_type, payload):
    """
    Publish notification to Redis channel.
    """
    message = json.dumps({"type": event_type, "payload": payload})
    r.publish("notifications", message)