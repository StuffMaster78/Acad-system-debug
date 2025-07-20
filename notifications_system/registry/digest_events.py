DIGESTABLE_EVENTS = {
    'order.created': {'delay_minutes': 60, 'group_by': 'user.id'},
    'order.completed': {'delay_minutes': 120, 'group_by': 'user.id'},
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