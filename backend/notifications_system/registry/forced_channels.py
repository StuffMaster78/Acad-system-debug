"""
Forced Channels Registry for the Notifications System.

Manages registration and retrieval of forced channels for specific
notification events. These override user preferences to ensure
important events are always delivered.
"""

from collections import defaultdict
from typing import Dict, Set, Iterable


class ForcedChannelRegistry:
    """Central registry for forced channels per event_key."""

    def __init__(self) -> None:
        self._forced_channels: Dict[str, Set[str]] = defaultdict(set)

    def register(self, event_key: str, channels: Iterable[str]) -> None:
        """Replace forced channels for an event.

        Args:
            event_key (str): Event identifier.
            channels (Iterable[str]): Channels to enforce.
        """
        self._forced_channels[event_key] = set(channels)

    def add(self, event_key: str, channel: str) -> None:
        """Add a single forced channel without replacing existing ones.

        Args:
            event_key (str): Event identifier.
            channel (str): Channel name.
        """
        self._forced_channels[event_key].add(channel)

    def get(self, event_key: str) -> Set[str]:
        """Retrieve forced channels for an event.

        Args:
            event_key (str): Event identifier.

        Returns:
            Set[str]: Channels that must always be used.
        """
        return self._forced_channels.get(event_key, set())

    def all(self) -> Dict[str, Set[str]]:
        """Retrieve all forced channel mappings.

        Returns:
            Dict[str, Set[str]]: Mapping of event → channels.
        """
        return self._forced_channels


# Singleton instance
forced_channel_registry = ForcedChannelRegistry()


def forced_channel(event_key: str, channels: Iterable[str]):
    """Decorator to register forced channels for an event.

    Args:
        event_key (str): Event identifier.
        channels (Iterable[str]): Channels to enforce.

    Returns:
        Callable: Identity decorator for use on functions/classes.
    """

    def decorator(obj):
        forced_channel_registry.register(event_key, channels)
        return obj

    return decorator