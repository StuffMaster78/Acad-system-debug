"""
A service for managing and delivering broadcast notifications to users.
Allows Admin users to create, update, and delete broadcast notifications.
This service handles the creation, delivery, and management of broadcast notifications.
It integrates with user notification preferences and ensures compliance with user settings.
It also supports caching of preferences for performance optimization.   
"""
# notifications/services/broadcast.py

from django.contrib.auth import get_user_model
from notifications_system.models.broadcast_notification import BroadcastNotification
from notifications_system.models.notification_delivery import NotificationDelivery
from notifications_system.services.delivery import NotificationDeliveryService
from notifications_system.template_engine import render_template
from notifications_system.utils.fallbacks import should_fallback_to_email
from notifications_system.utils.ws_broadcast import broadcast_ws_message
from notifications_system.utils.resolver import resolve_profile_settings

User = get_user_model()


class BroadcastNotificationService:

    @classmethod
    def send_broadcast(
        cls, title, body, *, group=None,
        metadata=None, channel='websocket', 
        fallback=True, test_mode=False
    ):
        """
        Send a broadcast notification to all users or users filtered by group.
        """
        users = User.objects.filter(is_active=True)
        if group:
            users = users.filter(groups=group)

        notification = BroadcastNotification.objects.create(
            title=title,
            body=body,
            metadata=metadata or {},
            channel=channel,
            group=group,
            is_test=test_mode,
        )

        for user in users.iterator():
            cls._send_to_user(user, notification, fallback=fallback, test_mode=test_mode)

        return notification

    @classmethod
    def _send_to_user(
        cls, user, notification, *,
        fallback=True, test_mode=False
    ):
        preferences = resolve_profile_settings(user)

        delivery_record = NotificationDelivery.objects.create(
            user=user,
            broadcast=notification,
            channel=notification.channel,
            status='pending'
        )

        try:
            if notification.channel == 'websocket':
                success = broadcast_ws_message(user, {
                    "title": notification.title,
                    "body": notification.body,
                    "meta": notification.metadata,
                })
                delivery_record.status = 'delivered' if success else 'failed'

                if fallback and not success and should_fallback_to_email(user):
                    cls._fallback_to_email(user, notification, test_mode)
                    delivery_record.status = 'fallback'

            elif notification.channel == 'email':
                cls._send_email(user, notification, test_mode)
                delivery_record.status = 'delivered'

            elif notification.channel == 'sms':
                NotificationDeliveryService.send_sms(user.phone, notification.body)
                delivery_record.status = 'delivered'

            else:
                delivery_record.status = 'unsupported'

        except Exception as e:
            delivery_record.status = 'error'
            delivery_record.error_message = str(e)

        delivery_record.save()

    @classmethod
    def _fallback_to_email(cls, user, notification, test_mode):
        subject = f"[Broadcast] {notification.title}"
        context = {"title": notification.title, "body": notification.body, "user": user}

        body_html = render_template("notifications/emails/normal.html", context)
        NotificationDeliveryService.send_email(
            user=user,
            subject=subject,
            body_html=body_html,
            template_name="broadcast_fallback",
            test_mode=test_mode
        )

    @classmethod
    def preview(cls, title, body, user):
        """
        Preview a broadcast notification to a specific user only.
        """
        fake_notification = BroadcastNotification(
            title=title,
            body=body,
            metadata={"preview": True},
            channel='websocket',
            is_test=True
        )
        cls._send_to_user(user, fake_notification, fallback=False, test_mode=True)