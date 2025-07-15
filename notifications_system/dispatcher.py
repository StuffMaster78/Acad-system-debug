# notifications_system/services/dispatcher.py

import logging
from notifications_system.utils.ws_broadcast import push_ws_notification
from notifications_system.services.core import NotificationService
from notifications_system.notification_enums import NotificationType
from notifications_system.tasks import async_send_notification

logger = logging.getLogger(__name__)

class NotificationDispatcher:
    """
    Sends notifications
    """
    @staticmethod
    def dispatch(
        user,
        *,
        website=None,
        actor=None,
        event="generic",
        payload=None,
        category="info",
        priority=5,
        is_critical=False,
        is_digest=False,
        digest_group=None,
        is_silent=False,
        channels=None,
        template_name=None,
    ):
        """
        Unified channel-aware notification dispatcher.

        Tries to send over WebSocket first. Falls back to email if critical or enabled.
        Logs to DB (in-app) always.
        """
        payload = payload or {}

        # Send to WebSocket
        if not is_silent and NotificationType.WEBSOCKET in (channels or []):
            try:
                push_ws_notification(user.id, payload)
                logger.debug(f"WS push to user {user.id} → OK")
            except Exception as e:
                logger.warning(f"WS push failed for user {user.id}: {e}")

        # Always log to in-app
        NotificationService.send(
            user=user,
            website=website,
            actor=actor,
            event=event,
            payload=payload,
            category=category,
            priority=priority,
            is_critical=is_critical,
            is_digest=is_digest,
            digest_group=digest_group,
            is_silent=is_silent,
            channels=[NotificationType.IN_APP],
            template_name=template_name
        )

        # Optionally fallback to email if critical or requested
        if not is_silent and (
            NotificationType.EMAIL in (channels or []) or is_critical
        ):
            NotificationService.send(
                user=user,
                website=website,
                actor=actor,
                event=event,
                payload=payload,
                category=category,
                priority=priority,
                is_critical=is_critical,
                is_digest=is_digest,
                digest_group=digest_group,
                is_silent=is_silent,
                channels=[NotificationType.EMAIL],
                template_name=template_name
            )

        # Extendable: Add SMS, Push, etc. here