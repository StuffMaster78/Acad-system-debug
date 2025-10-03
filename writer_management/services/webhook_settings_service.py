from django.core.exceptions import ValidationError
from django.db import IntegrityError

from writer_management.models.webhook_settings import (
    WebhookSettings, WebhookPlatform
)
from orders.order_enums import WebhookEvent
from writer_management.tasks import deliver_webhook_payload
from orders.serializers import OrderMinimalSerializer 
from django.utils import timezone

class WebhookSettingsService:
    """
    Service to manage writer webhook settings.
    """

    @staticmethod
    def create_or_update(
        user, website, platform,
        webhook_url, events, enabled=True
    ):
        """
        Create or update the webhook settings for a user.
        """
        if not webhook_url.startswith("https://"):
            raise ValidationError("Webhook URL must start with https://")

        try:
            settings_obj, _created = WebhookSettings.objects.update_or_create(
                user=user,
                platform=platform,
                website=website,
                defaults={
                    "webhook_url": webhook_url,
                    "subscribed_events": events,
                    "enabled": enabled,
                    "is_active": True,
                }
            )
            return settings_obj
        except IntegrityError as e:
            raise ValidationError("Could not save webhook settings: " + str(e))

    @staticmethod
    def disable(user, platform, website):
        """
        Disable webhook without deleting it.
        """
        try:
            settings_obj = WebhookSettings.objects.get(
                user=user, platform=platform, website=website
            )
            settings_obj.enabled = False
            settings_obj.save()
            return settings_obj
        except WebhookSettings.DoesNotExist:
            raise ValidationError("Webhook settings not found.")

    @staticmethod
    def get_active_settings_for_event(user, event, website):
        """
        Return webhook settings if the user is subscribed to a specific event.
        """
        return WebhookSettings.objects.filter(
            user=user,
            website=website,
            enabled=True,
            is_active=True,
            subscribed_events__contains=[event]
        ).first()
    @staticmethod
    def send_event_to_subscribers(event_type: str, order, actor=None):
        """
        Send a webhook event to all eligible writer webhook subscribers.

        Args:
            event_type (str): The event key (e.g., ORDER_CREATED).
            order (Order): The order triggering the event.
            actor (User): Optional user who triggered the event.
        """
        settings_qs = WebhookSettings.objects.filter(
            enabled=True,
            is_active=True,
            website=order.website,
            subscribed_events__contains=[event_type]
        ).select_related("user")

        for setting in settings_qs:
            if not setting.webhook_url:
                continue

            payload = {
                "event": event_type,
                "order": OrderMinimalSerializer(order).data,
                "triggered_by": actor.id if actor else None,
                "timestamp": timezone.now().isoformat(),
            }

            deliver_webhook_payload.delay(
                webhook_url=setting.webhook_url,
                payload=payload,
                platform=setting.platform,
                user_id=setting.user_id,
                event_type=event_type,
            )