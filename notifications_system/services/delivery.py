
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer # type: ignore

from notifications_system.models.notifications import Notification

class NotificationDeliveryService:
    """
    Handles delivery of notifications via multiple channels.
    Extendable to SMS, Push, etc.
    """

    @classmethod
    def deliver(cls, notification: Notification) -> bool:
        """
        Dispatches the notification to the appropriate delivery method based on its channel.
        Returns True if delivery was successful, False otherwise.
        """
        delivery_method = getattr(
            cls,
            f"deliver_via_{notification.channel}",
            None
        )
        if callable(delivery_method):
            return delivery_method(notification)
        return False  # Unknown/unsupported channel

    @classmethod
    def deliver_via_email(cls, notification: Notification) -> bool:
        """Delivers the notification via email."""
        user_email = getattr(notification.user, 'email', None)
        if not user_email:
            return False

        send_mail(
            subject=notification.title or "Notification",
            message=notification.body or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=True
        )
        return True

    @classmethod
    def deliver_via_websocket(cls, notification: Notification) -> bool:
        channel_layer = get_channel_layer()
        group_name = f"user_notifications_{notification.user.id}"

        payload = {
            "type": "notify",
            "data": {
                "id": notification.id,
                "title": notification.title,
                "body": notification.body,
                "timestamp": str(notification.created_at),
                "is_read": notification.is_read,
                "priority": notification.priority,
                "group": notification.group.name if notification.group else None,
            }
        }

        try:
            async_to_sync(channel_layer.group_send)(group_name, payload)
            return True
        except Exception:
            return False