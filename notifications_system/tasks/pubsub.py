import json
import redis
from celery import shared_task
from django.conf import settings

r = redis.StrictRedis.from_url(settings.REDIS_URL)

@shared_task
def publish_notification(event_type, payload):
    """
    Publish notification to Redis channel.
    """
    message = json.dumps({"type": event_type, "payload": payload})
    r.publish("notifications", message)