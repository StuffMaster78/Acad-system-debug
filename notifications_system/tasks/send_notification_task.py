def send_notification_task(event_key: str, context: dict):
    """
    Sends a notification by dispatching it to the appropriate channels.
    """
    from notifications_system.services.dispatch import NotificationDispatcher
    NotificationDispatcher.dispatch_notification(
        event_key, context
    )