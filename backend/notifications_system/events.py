from __future__ import annotations

import json
import threading
from typing import Any, Dict, Iterable, Optional, Union

import redis
from django.conf import settings

from notifications_system.tasks.handle_tasks import handle_event

# Redis connection settings
REDIS_HOST = getattr(settings, "REDIS_HOST", "localhost")
REDIS_PORT = int(getattr(settings, "REDIS_PORT", 6379))
REDIS_DB = int(getattr(settings, "REDIS_DB", 0))

USER_CHANNEL = "notifications:user:"
GROUP_CHANNEL = "notifications:group:"
GLOBAL_CHANNEL = "notifications:global"


class NotificationBroadcaster:
    """
    Lightweight pub/sub broadcaster over Redis for in-app realtime.
    """
    _redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    # user_id -> {"event": threading.Event, "queue": list, "lock": threading.Lock}
    _subscribers: Dict[Any, Dict[str, Any]] = {}

    @classmethod
    def _channel_name(cls, kind: str, key: Union[int, str, None] = None) -> str:
        if kind == "user" and key is not None:
            return f"{USER_CHANNEL}{key}"
        if kind == "group" and key is not None:
            return f"{GROUP_CHANNEL}{key}"
        return GLOBAL_CHANNEL

    @classmethod
    def publish(
        cls,
        payload: Dict[str, Any],
        *,
        user_id: Optional[Union[int, str]] = None,
        group: Optional[Union[str, int, Iterable[Union[str, int]]]] = None,
        global_broadcast: bool = False,
        **extra: Any,
    ) -> None:
        """
        Publish a payload to user / group / global channels.
        Accepts extra kwargs (e.g., notification_id) and merges them into the payload.
        """
        if extra:
            payload = {**payload, **extra}

        def _send(channel: str, data: Dict[str, Any]) -> None:
            # Redis wants bytes; json.dumps -> str is fine; client will encode
            cls._redis.publish(channel, json.dumps(data))

        if user_id is not None:
            _send(cls._channel_name("user", user_id), payload)

        if group:
            if isinstance(group, (list, tuple, set)):
                for g in group:
                    _send(cls._channel_name("group", g), payload)
            else:
                _send(cls._channel_name("group", group), payload)

        if global_broadcast:
            _send(GLOBAL_CHANNEL, payload)

    @classmethod
    def subscribe(
        cls,
        user_id: Union[int, str],
        *,
        groups: Optional[Iterable[Union[str, int]]] = None,
        include_global: bool = False,
    ):
        """
        Begin listening for messages for a user (and optional groups/global).
        Returns an internal queue (FIFO) you can poll via get_message(...).
        """
        if user_id in cls._subscribers:
            return cls._subscribers[user_id]["queue"]

        event = threading.Event()
        lock = threading.Lock()
        queue: list = []
        cls._subscribers[user_id] = {"event": event, "queue": queue, "lock": lock}

        def listen():
            pubsub = cls._redis.pubsub()
            channels = [cls._channel_name("user", user_id)]
            if groups:
                channels += [cls._channel_name("group", g) for g in groups]
            if include_global:
                channels.append(GLOBAL_CHANNEL)

            pubsub.subscribe(*channels)
            for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    raw = message.get("data")
                    data = json.loads(raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw)
                except Exception:
                    continue
                with lock:
                    queue.append(data)
                event.set()

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        return queue

    @classmethod
    def get_message(cls, user_id: Union[int, str], timeout: float = 30.0):
        """
        Block up to `timeout` seconds for the next message, then return it or None.
        """
        sub = cls._subscribers.get(user_id)
        if not sub:
            return None

        event: threading.Event = sub["event"]
        lock: threading.Lock = sub["lock"]
        if event.wait(timeout):
            with lock:
                item = sub["queue"].pop(0) if sub["queue"] else None
                # Re-arm only if there are no pending items
                if not sub["queue"]:
                    event.clear()
                return item
        return None

    @classmethod
    def unsubscribe(cls, user_id: Union[int, str]) -> None:
        cls._subscribers.pop(user_id, None)


def emit_event(event_key: str, payload: Dict[str, Any], *, delay: bool = True) -> None:
    """
    Emit an event to the notification pipeline via Celery.
    """
    if delay:
        handle_event.delay(event_key, payload)
    else:
        # Synchronous execution
        try:
            handle_event.run(event_key, payload)  # call the task’s run()
        except AttributeError:
            # Fallback if task doesn’t expose run()
            handle_event.apply(args=[event_key, payload])