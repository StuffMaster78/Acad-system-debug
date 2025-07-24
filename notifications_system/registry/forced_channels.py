"""
Forced Channels Registry for Notifications System

Manages registration and retrieval of forced channels for specific
notification events. These channels override user preferences to ensure
important events are always sent through specified mediums.
"""

from collections import defaultdict
from typing import Dict, Set, List


class ForcedChannelRegistry:
    """
    Central registry for forced channels per event_key.
    """

    def __init__(self) -> None:
        self._forced_channels: Dict[str, Set[str]] = defaultdict(set)

    def register(self, event_key: str, channels: List[str]) -> None:
        """
        Registers one or more channels that are always used for a
        specific event. Replaces existing forced channels.
        """
        self._forced_channels[event_key] = set(channels)

    def add(self, event_key: str, channel: str) -> None:
        """
        Adds a single forced channel without replacing existing ones.
        """
        self._forced_channels[event_key].add(channel)

    def get(self, event_key: str) -> Set[str]:
        """
        Returns a set of forced channels for a specific event.
        """
        return self._forced_channels.get(event_key, set())

    def all(self) -> Dict[str, Set[str]]:
        """
        Returns the entire forced channel mapping.
        """
        return self._forced_channels


# Shared singleton instance
forced_channel_registry = ForcedChannelRegistry()


# Decorator for convenience
def forced_channel(event_key: str, channels: List[str]):
    """
    Decorator to register forced channels for an event.
    """

    def decorator(func):
        forced_channel_registry.register(event_key, channels)
        return func

    return decorator