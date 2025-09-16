"""Notification delivery service with retry backoff.

This module centralizes per-channel delivery and applies retry/backoff
policies using the helpers in
`notifications_system.utils.retry_task`.

Channels can call the shared `_deliver_with_retry` to get exponential
backoff. Defaults are configurable via settings:

- NOTIFY_MAX_RETRIES (int, default=3)
- NOTIFY_BACKOFF_BASE (int, seconds, default=5)
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.mail import send_mail

from notifications_system.models.notifications import Notification
from notifications_system.utils.retry_task import (
    retry_task_with_backoff,
    retry_task_with_backoff_async,
)

logger = logging.getLogger(__name__)


class NotificationDeliveryService:
    """Dispatch notifications over specific channels with retries.

    Methods here should be thin wrappers around the actual per-channel
    clients (email, SSE, push, etc.), but they all go through a common
    retry strategy for resiliency.
    """

    # -------- Public API -------------------------------------------------

    @classmethod
    def deliver(cls, notification: Notification) -> bool:
        """Deliver a notification by its `channel` field.

        Args:
            notification: Notification ORM instance.

        Returns:
            True if delivery succeeded, False otherwise.
        """
        method = getattr(cls, f"deliver_via_{notification.channel}", None)
        if not callable(method):
            logger.warning("Unsupported channel: %s", notification.channel)
            return False
        return bool(method(notification))

    # -------- Channel implementations -----------------------------------

    @classmethod
    def deliver_via_email(cls, notification: Notification) -> bool:
        """Deliver the notification via email with retries.

        Args:
            notification: Notification ORM instance.

        Returns:
            True on success, False otherwise.
        """
        user_email = getattr(notification.user, "email", None)
        if not user_email:
            logger.info("Email skipped (no address) for user=%s",
                        getattr(notification.user, "id", None))
            return False

        def _send() -> bool:
            sent = send_mail(
                subject=notification.title or "Notification",
                message=notification.message or "",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL",
                                   "no-reply@example.com"),
                recipient_list=[user_email],
                fail_silently=False,
                html_message=getattr(notification, "rendered_message_html",
                                     None),
            )
            # Django returns number of successfully delivered messages.
            return bool(sent)

        return cls._deliver_with_retry("email", _send)

    @classmethod
    def deliver_via_sse(cls, notification: Notification) -> bool:
        """Deliver the notification via SSE with retries.

        Args:
            notification: Notification ORM instance.

        Returns:
            True on success, False otherwise.
        """
        try:
            from notifications_system.realtime.sse_publisher import (
                sse_publish_to_user,
            )
        except Exception:  # noqa: BLE001
            logger.exception("SSE publisher import failed.")
            return False

        payload = {
            "title": notification.rendered_title or notification.title,
            "message": notification.rendered_message or notification.message,
            "id": notification.id,
            "event": notification.event,
        }

        def _send() -> bool:
            uid = getattr(notification.user, "id", None)
            if uid is None:
                return False
            sse_publish_to_user(uid, payload)
            return True

        return cls._deliver_with_retry("sse", _send)

    # Example stub: push (kept minimal, but wired for retries)
    @classmethod
    def deliver_via_push(cls, notification: Notification) -> bool:
        """Deliver via push (FCM/OneSignal), using retry wrapper.

        Replace the inner `_send` with your provider integration.
        """
        user = notification.user
        tokens = getattr(user, "device_tokens", []) or []

        def _send() -> bool:
            if not tokens:
                logger.info("Push skipped (no tokens) for user=%s", user.id)
                return False
            # Example only; replace with real push client call.
            logger.info("PUSH to %s: %s", user.id, notification.message)
            return True

        return cls._deliver_with_retry("push", _send)

    # -------- Async companion (optional) --------------------------------

    @classmethod
    async def deliver_async(cls, notification: Notification) -> bool:
        """Async variant for environments using async channels.

        Falls back to sync methods via `async_to_sync` where needed.
        """
        method = getattr(cls, f"deliver_async_via_{notification.channel}",
                         None)
        if callable(method):
            return bool(await method(notification))

        # Fallback: run sync deliver in a thread via async_to_sync.
        return bool(await async_to_sync(cls.deliver)(notification))

    # Example async channel if you add a real async client:
    # async def deliver_async_via_sse(cls, notification: Notification) -> bool:
    #     async def _send():
    #         ...
    #     return await cls._deliver_with_retry_async("sse", _send)

    # -------- Shared retry wrappers -------------------------------------

    @classmethod
    def _deliver_with_retry(
        cls,
        channel: str,
        thunk: Callable[[], bool],
    ) -> bool:
        """Run a synchronous `thunk` with exponential backoff.

        Args:
            channel: Channel label (for logs/metrics).
            thunk: Zero-arg callable that returns True/False.

        Returns:
            True on success, False otherwise.
        """
        max_retries = getattr(settings, "NOTIFY_MAX_RETRIES", 3)
        base = getattr(settings, "NOTIFY_BACKOFF_BASE", 5)

        def _task() -> bool:
            ok = bool(thunk())
            if not ok:
                raise RuntimeError(f"{channel} delivery returned False")
            return ok

        res = retry_task_with_backoff(
            _task,
            max_retries=max_retries,
            base_backoff=base,
            raise_on_fail=False,
        )
        return bool(res)

    @classmethod
    async def _deliver_with_retry_async(
        cls,
        channel: str,
        thunk_async,  # Callable[[], Awaitable[bool]]
    ) -> bool:
        """Run an async `thunk_async` with exponential backoff.

        Args:
            channel: Channel label (for logs/metrics).
            thunk_async: Zero-arg async callable returning True/False.

        Returns:
            True on success, False otherwise.
        """
        max_retries = getattr(settings, "NOTIFY_MAX_RETRIES", 3)
        base = getattr(settings, "NOTIFY_BACKOFF_BASE", 5)

        async def _task():
            ok = bool(await thunk_async())
            if not ok:
                raise RuntimeError(f"{channel} delivery returned False")
            return ok

        res = await retry_task_with_backoff_async(
            _task,
            max_retries=max_retries,
            base_backoff=base,
            raise_on_fail=False,
        )
        return bool(res)