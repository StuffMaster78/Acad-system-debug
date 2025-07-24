import json
from pathlib import Path
from typing import List, Dict

from notifications_system.registry.validator import validate_event_config
from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"
EVENT_CONFIG_PATH = CONFIGS_DIR / "notification_event_config.json"
EVENT_SCHEMA_PATH = CONFIGS_DIR / "schema" / "notification_event.schema.json"


def load_event_configs() -> None:
    """
    Load and validate event configurations from JSON file.
    Registers them into NOTIFICATION_REGISTRY.
    """
    with open(EVENT_CONFIG_PATH) as f:
        event_configs = json.load(f)

    for config in event_configs:
        validate_event_config(config, EVENT_SCHEMA_PATH)
        event_key = config["event_key"]
        if event_key in NOTIFICATION_REGISTRY:
            raise ValueError(
                f"Duplicate event_key '{event_key}' in notification config."
            )
        NOTIFICATION_REGISTRY[event_key] = config


def get_notification_config(event_key: str) -> Dict:
    """
    Retrieve the notification config for a given event key.

    Args:
        event_key (str): Event identifier (e.g., 'order.created').

    Returns:
        dict: Notification config for the event.
    """
    if event_key not in NOTIFICATION_REGISTRY:
        raise KeyError(
            f"Notification config for '{event_key}' not found."
        )
    return NOTIFICATION_REGISTRY[event_key]


def get_channels_for_role(event_config: Dict, role: str) -> List[str]:
    """
    Resolve channels for a given role based on an event config.

    Args:
        event_config (dict): The config for a specific event.
        role (str): Role to retrieve channels for (e.g., 'writer').

    Returns:
        list[str]: List of channels like ['email', 'dashboard'].
    """
    if role not in event_config.get("roles", []):
        return []
    return event_config.get("channels", [])


def get_all_event_keys() -> List[str]:
    """
    Returns a list of all registered notification event keys.

    Returns:
        list[str]: All event keys loaded into the registry.
    """
    return list(NOTIFICATION_REGISTRY.keys())

def clear_notification_registry() -> None:
    """
    Clear the notification registry.
    Useful for testing or reloading configurations.
    """
    NOTIFICATION_REGISTRY.clear()
    print("Notification registry cleared.")