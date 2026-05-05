from __future__ import annotations

import json
import queue
import time
from collections.abc import Generator
from typing import Any
from django.conf import settings
from redis import Redis

from communications.sse.event_formatter import (
    CommunicationSSEEventFormatter,
)



class CommunicationSSEEventBus:
    """
    Redis-backed SSE event bus.

    Works across multiple Django/Gunicorn workers.
    """

    @staticmethod
    def _client() -> Redis:
        """
        Return Redis client.
        """
        return Redis.from_url(
            settings.COMMUNICATIONS_REDIS_URL,
            decode_responses=True,
        )

    @staticmethod
    def _channel() -> str:
        """
        Return communication SSE channel.
        """
        return getattr(
            settings,
            "COMMUNICATIONS_SSE_CHANNEL",
            "communications:sse",
        )

    @classmethod
    def publish(cls, *, event: dict[str, Any]) -> None:
        """
        Publish event to Redis channel.
        """
        payload = json.dumps(event)
        cls._client().publish(cls._channel(), payload)

    @classmethod
    def subscribe(cls) -> Generator[dict[str, Any], None, None]:
        """
        Subscribe to Redis event stream.
        """
        client = cls._client()
        pubsub = client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(cls._channel())

        try:
            last_ping_at = time.monotonic()

            while True:
                message = pubsub.get_message(timeout=15)

                if message is not None:
                    raw_data = message.get("data")

                    if not raw_data:
                        continue

                    try:
                        event = json.loads(str(raw_data))
                    except json.JSONDecodeError:
                        continue

                    yield event
                    last_ping_at = time.monotonic()
                    continue

                if time.monotonic() - last_ping_at >= 15:
                    yield {
                        "event": "ping",
                        "data": {
                            "type": "ping",
                            "payload": {},
                            "meta": {
                                "timestamp": time.time(),
                            },
                        },
                    }
                    last_ping_at = time.monotonic()
        finally:
            pubsub.close()


def format_sse_event(*, event: str, data: dict[str, Any]) -> str:
    """
    Format event as SSE payload.
    """
    return CommunicationSSEEventFormatter.format(
        event=event,
        data=data,
    )