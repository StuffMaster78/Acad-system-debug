from abc import ABC, abstractmethod

class BaseDeliveryBackend(ABC):
    """
    Abstract base class for all delivery backends.
    """

    def __init__(self, notification, channel_config=None):
        self.notification = notification
        self.channel_config = channel_config or {}

    @abstractmethod
    def send(self):
        """
        Send the notification.
        Should return True on success, False otherwise.
        """
        pass

    def supports_retry(self):
        return False  # Override if the backend supports retry logic