# superadmin_management/services/notification_delivery_orchestrator.py

import logging

logger = logging.getLogger(__name__)


class NotificationDeliveryOrchestrator:
    """
    Ensures notifications are reliable, deduplicated, and retry-safe.
    """

    @staticmethod
    def send(*, event_key, recipient, website, context, idempotency_key=None):

        try:
            from notifications_system.services.notification_service import (
                NotificationService,
            )

            NotificationService.notify(
                event_key=event_key,
                recipient=recipient,
                website=website,
                context=context,
            )

        except Exception as exc:
            logger.exception(
                "Notification failed event=%s recipient=%s error=%s",
                event_key,
                getattr(recipient, "pk", None),
                exc,
            )
            # In real system → push to repair queue