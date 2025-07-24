import logging
logger = logging.getLogger(__name__)

def send_sms_notification(user, message, use_async=False, **kwargs):
    from notifications_system.tasks.notifications import (
        async_send_sms_notification
    )
    phone = getattr(user, 'phone_number', None)

    if not phone:
        logger.warning(f"User {user.id} has no phone number")
        return

    if use_async:
        async_send_sms_notification.delay(user.id, message)
        return

    try:
        logger.info(f"Sending SMS to {phone}: {message}")
        # your_sms_provider.send(phone, message)
    except Exception as e:
        logger.exception(f"Failed to send SMS to {phone}: {str(e)}")