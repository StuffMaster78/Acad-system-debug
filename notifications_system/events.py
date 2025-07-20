from notifications_system.tasks import handle_event

def emit_event(event_key: str, payload: dict, delay: bool = True):
    """
    Emit an event to the notification system.
    This function is a wrapper around the handle_event task.
    """
    if delay:
        handle_event.delay(event_key, payload)
    else:
        handle_event.apply(event_key, payload)