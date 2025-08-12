from notifications_system.tasks import handle_event
import json
import threading
import redis
from django.conf import settings

# You can put this in settings
REDIS_HOST = getattr(settings, "REDIS_HOST", "localhost")
REDIS_PORT = getattr(settings, "REDIS_PORT", 6379)
REDIS_DB = getattr(settings, "REDIS_DB", 0)
NOTIFICATION_CHANNEL_PREFIX = "notifications:user:"

class NotificationBroadcaster:
    """
    Handles broadcasting notifications to users via Redis.
    """
    _redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    _subscribers = {}  # user_id -> threading.Event + buffer

    @classmethod
    def _channel_name(cls, user_id):
        return f"{NOTIFICATION_CHANNEL_PREFIX}{user_id}"

    @classmethod
    def publish(cls, user_id, payload: dict):
        cls._redis.publish(cls._channel_name(user_id), json.dumps(payload))

    @classmethod
    def subscribe(cls, user_id):
        if user_id in cls._subscribers:
            return cls._subscribers[user_id]['queue']

        event = threading.Event()
        queue = []
        cls._subscribers[user_id] = {'event': event, 'queue': queue}

        def listen():
            pubsub = cls._redis.pubsub()
            pubsub.subscribe(cls._channel_name(user_id))
            for message in pubsub.listen():
                if message['type'] != 'message':
                    continue
                try:
                    data = json.loads(message['data'])
                    queue.append(data)
                    event.set()
                except Exception:
                    continue

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        return queue

    @classmethod
    def get_message(cls, user_id, timeout=30):
        subscriber = cls._subscribers.get(user_id)
        if not subscriber:
            return None

        event = subscriber['event']
        if event.wait(timeout):
            event.clear()
            return subscriber['queue'].pop(0) if subscriber['queue'] else None
        return None

    @classmethod
    def unsubscribe(cls, user_id):
        cls._subscribers.pop(user_id, None)

def emit_event(event_key: str, payload: dict, delay: bool = True):
    """
    Emit an event to the notification system.
    This function is a wrapper around the handle_event task.
    """
    if delay:
        handle_event.delay(event_key, payload)
    else:
        handle_event.apply(event_key, payload)