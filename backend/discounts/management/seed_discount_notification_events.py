from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.enums import NotificationChannel
from notifications_system.enums import NotificationPriority
from notifications_system.enums import TemplateScope
from notifications_system.models.event_config import (
    NotificationEventConfig,
)
from notifications_system.models.notification_event import (
    NotificationEvent,
)
from notifications_system.models.notifications_template import (
    NotificationTemplate,
)


DISCOUNT_EVENTS = [
    {
        "event_key": "discount.applied",
        "label": "Discount Applied",
        "description": "Sent when a client discount is applied.",
        "category": "discount",
        "recipient_roles": ["client"],
        "subject": "Your discount has been applied",
        "title": "Discount applied",
        "message": "Your discount {{ discount_code }} was applied.",
    },
    {
        "event_key": "discount.expiring_soon",
        "label": "Discount Expiring Soon",
        "description": "Sent when a discount is close to expiry.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Discount expiring soon: {{ discount_code }}",
        "title": "Discount expiring soon",
        "message": "{{ discount_code }} expires at {{ ends_at }}.",
    },
    {
        "event_key": "discount.usage_limit_reached",
        "label": "Discount Usage Limit Reached",
        "description": "Sent when a discount reaches its usage limit.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Discount usage limit reached: {{ discount_code }}",
        "title": "Usage limit reached",
        "message": "{{ discount_code }} has reached its usage limit.",
    },
    {
        "event_key": "discount.campaign_activated",
        "label": "Campaign Activated",
        "description": "Sent when a discount campaign is activated.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Campaign activated: {{ campaign_name }}",
        "title": "Campaign activated",
        "message": "{{ campaign_name }} is now active.",
    },
    {
        "event_key": "discount.campaign_deactivated",
        "label": "Campaign Deactivated",
        "description": "Sent when a campaign is deactivated.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Campaign deactivated: {{ campaign_name }}",
        "title": "Campaign deactivated",
        "message": "{{ campaign_name }} has been deactivated.",
    },
    {
        "event_key": "discount.campaign_archived",
        "label": "Campaign Archived",
        "description": "Sent when a campaign is archived.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Campaign archived: {{ campaign_name }}",
        "title": "Campaign archived",
        "message": "{{ campaign_name }} has been archived.",
    },
    {
        "event_key": "discount.campaign_restored",
        "label": "Campaign Restored",
        "description": "Sent when a campaign is restored.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Campaign restored: {{ campaign_name }}",
        "title": "Campaign restored",
        "message": "{{ campaign_name }} has been restored.",
    },
    {
        "event_key": "discount.tier_created",
        "label": "Spend Tier Created",
        "description": "Sent when a spend tier discount is created.",
        "category": "discount",
        "recipient_roles": ["admin", "support"],
        "subject": "Spend tier created: {{ tier_name }}",
        "title": "Spend tier created",
        "message": "{{ tier_name }} has been created.",
    },
    {
        "event_key": "discount.loyalty_created",
        "label": "Loyalty Discount Created",
        "description": "Sent when a loyalty discount is created.",
        "category": "discount",
        "recipient_roles": ["client"],
        "subject": "Your loyalty discount is ready",
        "title": "Loyalty reward ready",
        "message": "Your loyalty discount {{ discount_code }} is ready.",
    },
]


class Command(BaseCommand):
    """
    Seed discount notification events, configs, and default templates.
    """

    help = "Seed discount notification events and templates."

    def handle(self, *args, **options) -> None:
        """
        Create or update discount notification setup.
        """
        created = 0
        updated = 0

        for item in DISCOUNT_EVENTS:
            event, event_created = NotificationEvent.objects.update_or_create(
                event_key=item["event_key"],
                defaults={
                    "label": item["label"],
                    "description": item["description"],
                    "category": item["category"],
                    "scope": NotificationEvent.SCOPE_USER,
                    "is_active": True,
                },
            )

            NotificationEventConfig.objects.update_or_create(
                event_key=item["event_key"],
                defaults={
                    "label": item["label"],
                    "description": item["description"],
                    "supports_email": True,
                    "supports_in_app": True,
                    "default_email_enabled": True,
                    "default_in_app_enabled": True,
                    "priority": NotificationPriority.NORMAL,
                    "recipient_roles": item["recipient_roles"],
                    "is_mandatory": False,
                    "user_can_disable": True,
                    "admin_can_disable": True,
                    "digest_eligible": False,
                    "is_active": True,
                },
            )

            NotificationTemplate.objects.update_or_create(
                event=event,
                website=None,
                channel=NotificationChannel.EMAIL,
                locale="en",
                version=1,
                defaults={
                    "scope": TemplateScope.GLOBAL,
                    "subject": item["subject"],
                    "body_html": (
                        "<p>{{ message }}</p>"
                        "<p>Website: {{ website_name }}</p>"
                    ),
                    "body_text": "{{ message }}",
                    "available_variables": [
                        "discount_code",
                        "discount_amount",
                        "final_amount",
                        "campaign_name",
                        "tier_name",
                        "ends_at",
                        "website_name",
                    ],
                    "is_active": True,
                },
            )

            NotificationTemplate.objects.update_or_create(
                event=event,
                website=None,
                channel=NotificationChannel.IN_APP,
                locale="en",
                version=1,
                defaults={
                    "scope": TemplateScope.GLOBAL,
                    "title": item["title"],
                    "message": item["message"],
                    "available_variables": [
                        "discount_code",
                        "discount_amount",
                        "final_amount",
                        "campaign_name",
                        "tier_name",
                        "ends_at",
                    ],
                    "is_active": True,
                },
            )

            if event_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Discount notification events seeded. "
                f"created={created}, updated={updated}"
            )
        )