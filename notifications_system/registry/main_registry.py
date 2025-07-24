"""
Central Notification Registry

Manages event configurations, templates, and forced channels.
"""

from collections import defaultdict
from typing import Dict, Set, Optional

# Flat dict registries for config-loaded events
NOTIFICATION_REGISTRY = {}
DIGEST_EVENT_REGISTRY = {}
BROADCAST_EVENT_REGISTRY = {}

# Optional grouping
ALL_EVENT_REGISTRIES = {
    "notification": NOTIFICATION_REGISTRY,
    "digest": DIGEST_EVENT_REGISTRY,
    "broadcast": BROADCAST_EVENT_REGISTRY,
}


class NotificationRegistry:
    """
    Manages notification templates and forced channels.
    """

    def __init__(self):
        self._templates: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._forced_channels: Dict[str, Set[str]] = defaultdict(set)

    def register_template(
        self, event_key: str, channel: str, template_name: str
    ) -> None:
        self._templates[event_key][channel] = template_name

    def get_template(self, event_key: str, channel: str) -> str:
        return self._templates.get(event_key, {}).get(
            channel, "default_template.html"
        )

    def register_forced_channel(self, event_key: str, channel: str) -> None:
        self._forced_channels[event_key].add(channel)

    def get_forced_channels(self, event_key: str) -> Set[str]:
        return self._forced_channels.get(event_key, set())

    def register_from_config():
        """
        Populate notification_registry with templates and forced channels
        from NOTIFICATION_REGISTRY.
        """
        for event_key, config in NOTIFICATION_REGISTRY.items():
            templates = config.get("templates", {})
            for channel, template in templates.items():
                notification_registry.register_template(
                    event_key, channel, template
                )

            forced_channels = config.get("forced_channels", [])
            for channel in forced_channels:
                notification_registry.register_forced_channel(
                    event_key, channel
                )

# Singleton instance
notification_registry = NotificationRegistry()
