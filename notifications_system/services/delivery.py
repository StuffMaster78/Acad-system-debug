# notifications/services/delivery.py
from notifications_system.models.notifications import Notification
from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class NotificationDeliveryService:

    @classmethod
    def deliver(cls, notification: Notification):
        if notification.channel == "email":
            return cls.deliver_via_email(notification)
        elif notification.channel == "web":
            return cls.deliver_via_websocket(notification)
        else:
            # fallback or unsupported
            return False

    @classmethod
    def deliver_via_email(cls, notification: Notification):
        if not notification.user.email:
            return False

        subject = notification.title or "Notification"
        message = notification.body or ""
        recipient_list = [notification.user.email]

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=True
        )
        return True

    @classmethod
    def deliver_via_websocket(cls, notification: Notification):
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

        async_to_sync(channel_layer.group_send)(group_name, payload)
        return True