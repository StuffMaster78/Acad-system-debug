from __future__ import annotations

import logging
from typing import Any, Iterable, Mapping, Optional

from notifications_system.enums import NotificationType
from notifications_system.services.core import NotificationService

logger = logging.getLogger(__name__)


class SSENotificationDispatcher:
    """Dispatch SSE notifications via the central service.

    This path persists notifications, logs deliveries, handles retries,
    and uses the SSE backend as one of the delivery channels.

    Methods are static to avoid import cycles and state.
    """

    channel = "sse"

    @staticmethod
    def send(
        event: str,
        payload: Mapping[str, Any],
        users: Iterable[Any],
        *,
        website: Optional[Any] = None,
        groups: Optional[Iterable[str]] = None,
    ) -> int:
        """Send SSE notifications for a set of users via the service.

        Args:
            event: Canonical event key (e.g., "order.created").
            payload: Context passed to the template/backends.
            users: Iterable of user objects.
            website: Optional tenant/site object. If not provided,
                falls back to ``getattr(user, "website", None)``.
            groups: Optional group names for fan-out.

        Returns:
            Number of attempted sends.
        """
        attempts = 0
        for user in users:
            try:
                site = website or getattr(user, "website", None)
                NotificationService.send_notification(
                    user=user,
                    event=event,
                    payload=dict(payload),
                    website=site,
                    channels=[NotificationType.SSE],
                    groups=groups,
                )
                attempts += 1
            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "SSE service dispatch failed (user=%s, event=%s): %s",
                    getattr(user, "id", None),
                    event,
                    exc,
                )
        return attempts