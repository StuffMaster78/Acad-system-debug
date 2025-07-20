NOTIFICATION_REGISTRY = {}

def register_notification(event_key, config):
    if event_key in NOTIFICATION_REGISTRY:
        raise ValueError(f"Notification event '{event_key}' already registered.")
    NOTIFICATION_REGISTRY[event_key] = config

def get_notification_config(event_key):
    return NOTIFICATION_REGISTRY.get(event_key)

def get_digest_config(event_key):
    config = NOTIFICATION_REGISTRY.get(event_key)
    if config and config.get("digest"):
        return config["digest"]
    return None

def list_all_event_keys():
    return list(NOTIFICATION_REGISTRY.keys())