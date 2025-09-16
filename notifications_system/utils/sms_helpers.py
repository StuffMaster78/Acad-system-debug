import logging
from typing import Optional

logger = logging.getLogger(__name__)


def send_sms_notification(
    user,
    message: str,
    *,
    use_async: bool = False,
    provider: Optional[object] = None,
    **kwargs,
) -> bool:
    """Send an SMS notification to a user.

    Args:
        user: Target user instance (must have `phone_number`).
        message: Message text to send.
        use_async: If True, enqueue async Celery task.
        provider: Optional SMS provider client for sync sending.
        **kwargs: Extra context for provider.

    Returns:
        bool: True if dispatched successfully, False otherwise.
    """
    from notifications_system.tasks.notifications import (
        async_send_sms_notification,
    )

    phone = getattr(user, "phone_number", None)
    if not phone:
        logger.warning("SMS skipped: user=%s has no phone number",
                       getattr(user, "id", None))
        return False

    if use_async:
        async_send_sms_notification.delay(user.id, message, **kwargs)
        return True

    try:
        if provider:
            # Plug in your provider integration here:
            # provider.send_sms(phone, message, **kwargs)
            logger.info("SMS [%s] sent via provider to %s", message, phone)
        else:
            # Fallback stub — replace with real client later
            logger.info("SMS [%s] logged only to %s", message, phone)
        return True
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send SMS to %s: %s", phone, exc)
        return False