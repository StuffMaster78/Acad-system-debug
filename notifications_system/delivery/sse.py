from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional, Set

import redis
from django.conf import settings

from notifications_system.delivery.base import (
    BaseDeliveryBackend,
    DeliveryResult,
)
from notifications_system.registry.template_registry import get_template
from notifications_system.models.realtime_channel import RealtimeChannel

logger = logging.getLogger(__name__)


def _redis_client() -> redis.Redis:
    """Create a Redis client from settings.

    Returns:
        Redis client connected via REDIS_URL or a local default.
    """
    url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    return redis.Redis.from_url(url)


class SSEBackend(BaseDeliveryBackend):
    """Server-Sent Events (SSE) delivery backend.

    Publishes rendered notification payloads to active realtime channels
    in Redis. Channels may be linked to users and/or groups.

    Channel config keys:
      * groups: Iterable of group names for additional fan-out.

    Returns:
      DeliveryResult indicating publish outcome.
    """

    channel = "sse"

    def send(self) -> DeliveryResult:
        event = self.notification.event
        payload: Dict[str, Any] = dict(self.notification.payload or {})
        user_id = getattr(self.notification.user, "id", None)
        website_id = getattr(self.notification.website, "id", None)
        cfg_groups = self.channel_config.get("groups")
        pay_groups = payload.get("groups")
        groups = cfg_groups or pay_groups

        tmpl = get_template(event)
        if not tmpl:
            return DeliveryResult(False, f"No class template for '{event}'")

        try:
            title, text, html = tmpl.render(payload)
        except Exception as exc:  # noqa: BLE001
            logger.exception("SSE render failed for '%s': %s", event, exc)
            return DeliveryResult(False, f"render failed: {exc}")

        body: Dict[str, Any] = {
            "event": event,
            "title": title,
            "message": text,
            "html": html,
            "payload": payload,
            "notification_id": getattr(self.notification, "id", None),
            "user_id": user_id,
            "website_id": website_id,
        }

        channels: Set[str] = set()

        if user_id:
            qs = RealtimeChannel.objects.filter(
                user_id=user_id,
                is_active=True,
            )
            if website_id and hasattr(RealtimeChannel, "website_id"):
                qs = qs.filter(website_id=website_id)
            channels.update(qs.values_list("channel_name", flat=True))

        if groups:
            qs = RealtimeChannel.objects.filter(
                group__in=list(groups),
                is_active=True,
            )
            if website_id and hasattr(RealtimeChannel, "website_id"):
                qs = qs.filter(website_id=website_id)
            channels.update(qs.values_list("channel_name", flat=True))

        if not channels:
            return DeliveryResult(True, "no active SSE channels")

        try:
            client = _redis_client()
            data = json.dumps(body, default=str)
            for chan in channels:
                client.publish(chan, data)
            return DeliveryResult(
                True,
                f"published to {len(channels)} channel(s)",
                {"channels": list(channels)},
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("SSE publish failed for '%s': %s", event, exc)
            return DeliveryResult(False, f"redis publish failed: {exc}")

    def supports_retry(self) -> bool:
        """Return True. Publishing is idempotent at-least-once."""
        return True