from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Optional

import redis
from django.conf import settings

logger = logging.getLogger(__name__)


def _client() -> redis.Redis:
    """Return a Redis client using settings.REDIS_URL or a local default.

    Returns:
        Redis: Connected Redis client instance.
    """
    url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url)


def _publish(channel: str, payload: Dict[str, Any]) -> int:
    """Publish a payload to a Redis pub/sub channel.

    Args:
        channel: Pub/sub channel name.
        payload: JSON-serializable dict to publish.

    Returns:
        The number of clients that received the message.

    Raises:
        Exception: If serialization or publish fails.
    """
    message = {"type": "sse_event", "payload": payload}
    data = json.dumps(message, default=str)
    try:
        rc = _client().publish(channel, data)
        logger.debug("SSE published to %s (receivers=%s)", channel, rc)
        return int(rc)
    except Exception as exc:  # noqa: BLE001
        logger.error("SSE publish failed to %s: %s", channel, exc, exc_info=True)
        raise


def publish_to_user(user_id: int, payload: Dict[str, Any]) -> int:
    """Publish to a user-specific SSE channel.

    Args:
        user_id: Target user ID.
        payload: JSON-serializable dict payload.

    Returns:
        Number of receivers that handled the message.
    """
    channel = f"sse:user:{user_id}"
    return _publish(channel, payload)


def publish_to_group(group: str, payload: Dict[str, Any]) -> int:
    """Publish to a group SSE channel.

    Args:
        group: Group name (e.g., "writers", "admins").
        payload: JSON-serializable dict payload.

    Returns:
        Number of receivers that handled the message.
    """
    channel = f"sse:group:{group}"
    return _publish(channel, payload)


def publish_bulk(
    *,
    users: Optional[Iterable[int]] = None,
    groups: Optional[Iterable[str]] = None,
    payload: Dict[str, Any],
) -> int:
    """Publish the same payload to many user/group channels.

    Args:
        users: Iterable of user IDs. If None, no user channels are sent.
        groups: Iterable of group names. If None, no group channels.
        payload: JSON-serializable dict payload.

    Returns:
        Total number of receivers across all channels.
    """
    total = 0
    users = users or []
    groups = groups or []

    for uid in users:
        try:
            total += publish_to_user(uid, payload)
        except Exception:  # noqa: BLE001
            # Already logged in publish; continue other targets.
            continue

    for grp in groups:
        try:
            total += publish_to_group(grp, payload)
        except Exception:  # noqa: BLE001
            continue

    return total