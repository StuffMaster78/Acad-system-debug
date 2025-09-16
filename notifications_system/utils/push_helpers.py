"""Helpers for sending push notifications (sync or async)."""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def send_push_notification(
    user,
    title: str,
    message: str,
    *,
    use_async: bool = False,
    data: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> None:
    """Send a push notification to all of a user's devices.

    Args:
        user: User instance, expected to have ``device_tokens`` attribute.
        title: Notification title.
        message: Notification body text.
        use_async: If True, enqueue via Celery instead of direct send.
        data: Optional dict of extra key/value payload.
        **kwargs: Extra params passed through (future-proofing).

    Raises:
        Exception: If the push client fails to send (only in sync mode).
    """
    from notifications_system.tasks.notifications import (
        async_send_push_notification,
    )

    tokens: List[str] = getattr(user, "device_tokens", []) or []

    if not tokens:
        logger.debug("No device tokens for user %s — skipping push.", user.id)
        return

    if use_async:
        async_send_push_notification.delay(
            user.id, title, message, data or {}
        )
        return

    # TODO: Replace with real push service integration
    for token in tokens:
        try:
            logger.info(
                "PUSH → [%s] to token=%s | msg=%s",
                title, token, message
            )
            # Example: push_client.send(token, title, message, data=data)
        except Exception as exc:
            logger.exception("Push failed for token=%s: %s", token, exc)