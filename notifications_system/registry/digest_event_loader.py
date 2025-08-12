import json
import os
from pathlib import Path

from notifications_system.registry.validator import validate_event_config
from notifications_system.registry.main_registry import NotificationRegistry

# Schema path for digest event configs
SCHEMA_PATH = Path(__file__).parent / "config" / "schemas" / "digest_event.schema.json"

# Config JSON file (holds list of event configs)
CONFIG_FILE = Path(__file__).parent / "config" / "digest_event_config.json"


def load_digest_configs():
    """Load and validate digest event configurations."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Digest config file not found at {CONFIG_FILE}")

    with open(CONFIG_FILE, "r") as f:
        configs = json.load(f)

    if not isinstance(configs, list):
        raise ValueError("digest_event_config.json must contain a list of config objects")

    for config in configs:
        validate_event_config(config, SCHEMA_PATH)
        event_key = config.get("event_key")
        if not event_key:
            raise ValueError(f"Digest config missing 'event_key': {config}")
        NotificationRegistry.register_template(
            event_key, "email", config.get("email_template", "default_digest_email.html")
        )