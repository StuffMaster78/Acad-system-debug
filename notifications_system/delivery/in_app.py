from .base import BaseDeliveryBackend

class InAppBackend(BaseDeliveryBackend):
    """
    Marks the notification as deliverable via in-app UI.
    """

    def send(self):
        self.notification.status = "sent"
        self.notification.save(update_fields=["status"])
        return True