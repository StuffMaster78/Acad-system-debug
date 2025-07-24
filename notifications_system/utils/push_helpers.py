import logging
logger = logging.getLogger(__name__)

def send_push_notification(user, title, message, use_async=False, **kwargs):
    from notifications_system.tasks.notifications import async_send_push_notification
    tokens = getattr(user, 'device_tokens', [])

    if use_async:
        async_send_push_notification.delay(user.id, title, message)
        return

    for token in tokens:
        try:
            logger.info(f"PUSH [{title}] to {token}: {message}")
            # push_client.send(token, title, message)
        except Exception as e:
            logger.exception(f"Push failed for token {token}: {str(e)}")