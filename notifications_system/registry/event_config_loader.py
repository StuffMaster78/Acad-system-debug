"""
Module to load and merge notification event configurations from JSON and DB.
Supports schema validation, caching, and DB override logic.

Configuration structure includes:
- event_key: Unique key for the event (e.g., ORDER_ASSIGNED)
- description: Human-readable description
- priority: low, medium, high, critical
- default_channels: Email, SMS, Push, Slack, etc.
- forced_channels: Channels that must always be used
- notify_roles: List of roles to notify (e.g., admin, writer)

JSON config lives in: registry/config/notification_event_config.json
Schema files live in: registry/config/schemas/
Overrides live in: NotificationEventOverride model.
"""
import os
import json
import logging
import os
from pathlib import Path

from django.conf import settings
from django.core.cache import cache

from notifications_system.models.notification_event_override import (
    NotificationEventOverride
)

from notifications_system.registry.validator import validate_event_config
from notifications_system.registry.main_registry import NOTIFICATION_REGISTRY
from notifications_system.registry.digest_event_loader import load_digest_configs

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve(strict=True).parent
CONFIG_DIR = BASE_DIR / "configs"
SCHEMA_DIR = CONFIG_DIR / "schema"

NOTIFICATION_CONFIG_PATH = CONFIG_DIR / "notification_event_config.json"
BROADCAST_EVENT_CONFIG_PATH = CONFIG_DIR / "broadcast_event_config.json"
BROADCAST_EVENT_SCHEMA_PATH = SCHEMA_DIR / "broadcast_event.schema.json"

CONFIG_CACHE_KEY = "notification_event_configs"

CONFIG_FILE_PATH = os.path.join(
    settings.BASE_DIR,
    "notifications_system",
    "registry",
    "config",
    "notification_event_config.json"
)
CACHE_TIMEOUT = 60 * 10  # 10 minutes


def _load_json_config(path: Path) -> dict:
    """Load static event config from JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Failed to load event config JSON from {path}")
        raise RuntimeError(f"Could not load event config from {path}") from e


def _load_db_overrides() -> dict:
    """
    Fetch all NotificationEventOverride records
    and build a dict of overrides.
    
    Returns:
        dict: event_key → override config
    """
    overrides = {}
    for obj in NotificationEventOverride.objects.all():
        try:
            overrides[obj.event_key] = obj.config
        except Exception as e:
            logger.warning(f"Invalid override for {obj.event_key}: {e}")
    return overrides


def _merge_configs(file_config: dict, db_overrides: dict) -> dict:
    """
    Merge database overrides into the base file config.
    DB values take precedence.

    Args:
        file_config (dict): Static config
        db_overrides (dict): DB override config

    Returns:
        dict: Merged result
    """
    merged = file_config.copy()
    merged.update(db_overrides)
    return merged


def get_event_config(force_reload: bool = False) -> dict:
    """
    Load, merge, validate and cache the full event config.

    Args:
        force_reload (bool): If True, ignore cache and
        reload from source.

    Returns:
        dict: Final validated config
    """
    if not force_reload:
        cached = cache.get(CONFIG_CACHE_KEY)
        if cached:
            return cached

    file_config = _load_json_config(NOTIFICATION_CONFIG_PATH)
    db_overrides = _load_db_overrides()
    full_config = _merge_configs(file_config, db_overrides)

    # Validate merged config
    try:
        validate_event_config(full_config)
    except Exception as e:
        logger.error("Validation failed for notification config")
        raise

    # Cache it
    cache.set(CONFIG_CACHE_KEY, full_config, timeout=CACHE_TIMEOUT)
    logger.info("Event config loaded and cached")

    return full_config

def load_broadcast_configs():
    """
    Load and validate broadcast-level notification events.
    These apply system-wide and are not tied to user-triggered flows.
    """
    broadcast_configs = _load_json_config(BROADCAST_EVENT_CONFIG_PATH)

    for config in broadcast_configs:
        validate_event_config(
            config,
            schema_path=BROADCAST_EVENT_SCHEMA_PATH
        )
        event_key = config["event_key"]
        if event_key in NOTIFICATION_REGISTRY:
            raise ValueError(f"Duplicate event_key '{event_key}' in broadcast config.")
        NOTIFICATION_REGISTRY[event_key] = config


def load_all_configs():
    """
    Load all notification and broadcast configs.
    This will populate the NOTIFICATION_REGISTRY.
    Includes: notification events, digest events, broadcast events.
    """
    from notifications_system.registry.notification_event_loader import (
        load_event_configs
    )

    # Load notification event configs
    load_event_configs()

    # Load digest event configs
    load_digest_configs()

    # Load broadcast event configs
    load_broadcast_configs()

    logger.info("All notification and broadcast configs loaded successfully.")