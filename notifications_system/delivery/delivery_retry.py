# notifications/deliveretry.py

import json
import redis
from django.conf import settings
from notifications_system.models.realtime_channel import RealtimeChannel
from notifications_system.registry.template_registry import TemplateRegistry

r = redis.Redis.from_url(getattr(settings, "REDIS_URL", "redis://localhost:6379"))


def deliver_sse_event(event_name: str, recipient: dict, context: dict):
    """
    Deliver an SSE event to one or more channels.
    """
    template = TemplateRegistry.get_template(event_name)
    instance = template(context)

    title, message, html_message = instance.render()
    payload = {
        "event": event_name,
        "title": title,
        "message": message,
        "html": html_message,
        "context": context,
    }

    channels = []
    if recipient.get("user_id"):
        channels += list(
            RealtimeChannel.objects.filter(user_id=recipient["user_id"], is_active=True)
            .values_list("channel_name", flat=True)
        )

    if recipient.get("group"):
        channels += list(
            RealtimeChannel.objects.filter(group=recipient["group"], is_active=True)
            .values_list("channel_name", flat=True)
        )

    for chan in set(channels):
        r.publish(chan, json.dumps(payload))
