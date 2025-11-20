from abc import ABC, abstractmethod


class BaseAction(ABC):
    """Abstract base class for all domain actions."""

    def __init__(self, actor, **kwargs):
        self.actor = actor
        self.context = kwargs

    def validate(self):
        """Override for pre-checks. Optional."""
        pass

    @abstractmethod
    def perform(self, **kwargs):
        """Perform the action and return result."""
        pass

class PermissionDenied(Exception):
    """Custom exception when permission check fails."""
    pass