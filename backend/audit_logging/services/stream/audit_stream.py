import json
import redis

from django.conf import settings


class AuditStream:

    client = redis.Redis.from_url(settings.REDIS_URL)

    CHANNEL = "audit.events"

    @classmethod
    def publish(cls, event):

        payload = {
            "id": str(event.id),
            "action": event.action,
            "website_id": str(event.website_id),
            "actor_id": event.actor_id,
            "occurred_at": str(event.occurred_at),
        }

        cls.client.publish(cls.CHANNEL, json.dumps(payload))