def send_notification_task(event_key: str, context: dict):
    """
    Sends a notification by dispatching it to the appropriate channels.
    """
    from notifications_system.services.dispatch import send
    send(
        event_key=event_key,
        context=context,
        channels=["email", "in_app", "sse"],
        user=context.get("user"),
        website=context.get("website"),
    )