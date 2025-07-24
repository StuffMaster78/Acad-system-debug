DIGESTABLE_EVENTS = {
    'order.created': {'delay_minutes': 60, 'group_by': 'user.id'},
    'order.completed': {'delay_minutes': 120, 'group_by': 'user.id'},
    'user.signup': {'delay_minutes': 30, 'group_by': 'user.id'},
    'user.profile_updated': {'delay_minutes': 15, 'group_by': 'user.id'},
    'user.password_reset': {'delay_minutes': 45, 'group_by': 'user.id'},
    'user.login': {'delay_minutes': 10, 'group_by': 'user.id'},
    'user.logout': {'delay_minutes': 10, 'group_by': 'user.id'},
    'comment.replied': {'delay_minutes': 30, 'group_by': 'user.id'},
    'comment.liked': {'delay_minutes': 20, 'group_by': 'user.id'},
    'comment.reported': {'delay_minutes': 60, 'group_by': 'user.id'},
    'post.created': {'delay_minutes': 60, 'group_by': 'user.id'},
    'post.updated': {'delay_minutes': 30, 'group_by': 'user.id'},
    'post.deleted': {'delay_minutes': 120, 'group_by': 'user.id'},
    'notification.received': {'delay_minutes': 15, 'group_by': 'user.id'},
    'notification.read': {'delay_minutes': 10, 'group_by': 'user.id'},
    'notification.acknowledged': {'delay_minutes': 20, 'group_by': 'user.id'},
    'comment.added': {'delay_minutes': 45, 'group_by': 'user.id'},
    'post.published': {'delay_minutes': 90, 'group_by': 'user.id'},
    'notification.sent': {'delay_minutes': 30, 'group_by': 'user.id'},
    'system.alert': {'delay_minutes': 120, 'group_by': 'system.id'},
    'task.completed': {'delay_minutes': 60, 'group_by': 'task.id'},
    'event.reminder': {'delay_minutes': 15, 'group_by': 'event.id'},
    'feedback.received': {'delay_minutes': 30, 'group_by': 'user.id'},
    'subscription.renewed': {'delay_minutes': 60, 'group_by': 'user.id'},
    'payment.failed': {'delay_minutes': 120, 'group_by': 'user.id'},
    'payment.success': {'delay_minutes': 60, 'group_by': 'user.id'},
    'alert.critical': {'delay_minutes': 30, 'group_by': 'alert.id'},
    'notification.digest': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.notification': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.event': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.system': {'delay_minutes': 120, 'group_by': 'system.id'},
    'digest.task': {'delay_minutes': 60, 'group_by': 'task.id'},
    'digest.feedback': {'delay_minutes': 30, 'group_by': 'user.id'},
    'digest.subscription': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.payment': {'delay_minutes': 120, 'group_by': 'user.id'},
    'digest.alert': {'delay_minutes': 30, 'group_by': 'alert.id'},
    'digest.notification_digest': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.notification_event': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.notification_system': {'delay_minutes': 120, 'group_by': 'system.id'},
    'digest.notification_task': {'delay_minutes': 60, 'group_by': 'task.id'},
    'digest.notification_feedback': {'delay_minutes': 30, 'group_by': 'user.id'},
    'digest.notification_subscription': {'delay_minutes': 60, 'group_by': 'user.id'},
    'digest.notification_payment': {'delay_minutes': 120, 'group_by': 'user.id'},
    'digest.notification_alert': {'delay_minutes': 30, 'group_by': 'alert.id'},
    'digest.notification_digest_notification': {'delay_minutes': 60, 'group_by': 'user.id'}
}
def get_digestable_events() -> dict:
    """
    Returns a dictionary of events that are digestable.
    Each event maps to its configuration for digest processing.
    """
    return DIGESTABLE_EVENTS

def is_digestable(event_key: str) -> bool:
    return event_key in DIGESTABLE_EVENTS

def get_digest_config(event_key: str) -> dict:
    return DIGESTABLE_EVENTS.get(event_key, {})

def get_digest_delay(event_key: str) -> int:
    """
    Returns the delay in minutes for digest processing of the given event.
    If the event is not digestable, returns None.
    """
    config = get_digest_config(event_key)
    return config.get('delay_minutes') if config else None

def get_digest_group_by(event_key: str) -> str:
    """
    Returns the group_by field for digest processing of the given event.
    If the event is not digestable, returns None.
    """
    config = get_digest_config(event_key)
    
def list_digestable_event_keys() -> list:
    """
    Returns a list of all digestable event keys.
    """
    return list(DIGESTABLE_EVENTS.keys())

def get_digest_event_config(event_key: str) -> dict:
    """
    Returns the configuration for digest processing of the given event key.
    If the event is not digestable, returns an empty dictionary.
    """
    return DIGESTABLE_EVENTS.get(event_key, {})

def get_digest_event_delay(event_key: str) -> int:
    """
    Returns the delay in minutes for digest processing of the given event key.
    If the event is not digestable, returns None.
    """
    config = get_digest_event_config(event_key)
    return config.get('delay_minutes') if config else None

def get_digest_event_group_by(event_key: str) -> str:
    """
    Returns the group_by field for digest processing of the given event key.
    If the event is not digestable, returns None.
    """
    config = get_digest_event_config(event_key)
    return config.get('group_by') if config else None

def get_digest_event_keys() -> list:
    """
    Returns a list of all digestable event keys.
    """
    return list(DIGESTABLE_EVENTS.keys())