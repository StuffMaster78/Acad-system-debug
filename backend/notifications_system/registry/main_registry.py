# notifications_system/registry/main_registry.py
"""
Central Notification Registry.

Holds in-memory config maps and a light helper for per-event template
names and forced channels. Prefer the dedicated registries where
possible:
  - template_registry.py       (class-based + name-based templates)
  - forced_channels.py         (forced channel rules)
  - notification_registry.py   (loads NOTIFICATION_REGISTRY)
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Mapping, Optional, Set


# Flat dict registries populated by loaders
NOTIFICATION_REGISTRY: Dict[str, Dict[str, Any]] = {}
DIGEST_EVENT_REGISTRY: Dict[str, Dict[str, Any]] = {}
BROADCAST_EVENT_REGISTRY: Dict[str, Dict[str, Any]] = {}

# Optional grouping
ALL_EVENT_REGISTRIES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "notification": NOTIFICATION_REGISTRY,
    "digest": DIGEST_EVENT_REGISTRY,
    "broadcast": BROADCAST_EVENT_REGISTRY,
}


class NotificationRegistry:
    """Store per-event template filenames and forced channels.

    This is a thin helper for code that still expects a single object
    to answer both "what file template should I use for channel X?" and
    "which channels are forced for this event?" Prefer the newer
    modules for fresh code.
    """

    def __init__(self) -> None:
        self._templates: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._forced_channels: Dict[str, Set[str]] = defaultdict(set)

    # ----- Templates -----

    def register_template(
        self,
        event_key: str,
        channel: str,
        template_name: str,
    ) -> None:
        """Register a per-channel template filename for an event."""
        self._templates[event_key][channel] = template_name

    def get_template(self, event_key: str, channel: str) -> str:
        """Return the template filename or a default."""
        return self._templates.get(event_key, {}).get(
            channel, "default_template.html"
        )

    # ----- Forced channels -----

    def register_forced_channel(self, event_key: str, channel: str) -> None:
        """Mark a channel as forced for the event."""
        self._forced_channels[event_key].add(channel)

    def get_forced_channels(self, event_key: str) -> Set[str]:
        """Return the set of forced channels for the event."""
        return set(self._forced_channels.get(event_key, set()))

    # ----- Bulk/utility -----

    def register_from_config(
        self, config: Mapping[str, Mapping[str, Any]]
    ) -> int:
        """Populate from a config map {event_key: config}.

        Recognized keys per event:
          - templates: {channel: template_name}
          - forced_channels: [channel, ...]

        Args:
            config: Mapping of event configs.

        Returns:
            int: Number of events processed.
        """
        count = 0
        for event_key, cfg in config.items():
            templates = cfg.get("templates", {}) or {}
            if isinstance(templates, Mapping):
                for ch, name in templates.items():
                    self.register_template(event_key, str(ch), str(name))

            forced = cfg.get("forced_channels", []) or []
            for ch in forced:
                self.register_forced_channel(event_key, str(ch))
            count += 1
        return count

    def refresh_from_notifications(self) -> int:
        """Load from the global NOTIFICATION_REGISTRY."""
        return self.register_from_config(NOTIFICATION_REGISTRY)

    def clear(self) -> None:
        """Reset all stored mappings (tests/dev only)."""
        self._templates.clear()
        self._forced_channels.clear()

    def as_dict(self) -> Dict[str, Any]:
        """Return a serializable snapshot for admin/debug."""
        return {
            "templates": {
                k: dict(v) for k, v in self._templates.items()
            },
            "forced_channels": {
                k: sorted(v) for k, v in self._forced_channels.items()
            },
        }


# Singleton instance for legacy callers
notification_registry = NotificationRegistry()


__all__ = [
    "NOTIFICATION_REGISTRY",
    "DIGEST_EVENT_REGISTRY",
    "BROADCAST_EVENT_REGISTRY",
    "ALL_EVENT_REGISTRIES",
    "NotificationRegistry",
    "notification_registry",
]