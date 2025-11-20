# notifications_system/services/delivery.py
# -*- coding: utf-8 -*-
"""Compatibility delivery shim.

Prefer NotificationService._deliver and CHANNEL_BACKENDS.

This module exists only for legacy imports that call a single
"deliver(...)" function. It resolves the backend from the channel
and invokes it, returning a bool. New code should not import this.
"""

from __future__ import annotations

from typing import Optional

from django.utils import timezone

from notifications_system.enums import DeliveryStatus
from notifications_system.models.notification_delivery import (
    NotificationDelivery,
)


def deliver(notification, channel: Optional[str] = None, **config) -> bool:
    """Deliver a notification via a specific channel.

    Args:
        notification: Notification ORM instance.
        channel: Channel key (e.g., "email"). Defaults to notification.type.
        **config: Extra channel_config passed to the backend.

    Returns:
        bool: True on success, False otherwise.
    """
    # Lazy import to avoid cycles.
    from notifications_system.delivery import CHANNEL_BACKENDS  # noqa
    from notifications_system.services.core import (  # noqa
        NotificationService,
    )

    ch = channel or getattr(notification, "type", None)
    if not ch:
        return False

    # Reuse the real delivery path so logs/retries stay consistent.
    ok = NotificationService._deliver(  # noqa: SLF001
        notification,
        ch,
        html_message=config.get("html_message"),
        email_override=config.get("email_override"),
        attempt=config.get("attempt", 1),
    )

    # Minimal safety record for legacy callers that expected a write.
    # (Core already writes richer rows; this is harmless duplication.)
    try:
        NotificationDelivery.objects.create(
            notification=notification,
            channel=ch,
            status=DeliveryStatus.SENT if ok else DeliveryStatus.FAILED,
            sent_at=timezone.now(),
            attempts=config.get("attempt", 1),
        )
    except Exception:  # pragma: no cover
        # Never let legacy shim crash delivery flow.
        pass

    return bool(ok)