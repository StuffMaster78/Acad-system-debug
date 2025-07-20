from django.core.management.base import BaseCommand
from notifications_system.utils.priority_mapper import PRIORITY_LABEL_CHOICES
from notifications_system.utils.priority_mapper import get_priority_from_label, get_label_from_priority 
from notifications_system.enums import NotificationPriority
from notifications_system.models.notification_group import NotificationGroup
from notifications_system.enums import NotificationChannel

DEFAULT_GROUPS = [
    {
        "name": "ORDERS",
        "description": "Notifications related to order creation, updates, and assignments.",
    },
    {
        "name": "WRITER_MANAGEMENT",
        "description": "Notifications for writer applications, approvals, bans, and warnings.",
    },
    {
        "name": "CLIENT_MANAGEMENT",
        "description": "Client onboarding, suspension, feedback, and payment issues.",
    },
    {
        "name": "DISCOUNTS",
        "description": "Discount code creation, expiration, or application alerts.",
    },
    {
        "name": "BADGES",
        "description": "Badge awards, progress updates, or demotions.",
    },
    {
        "name": "SUPERADMIN",
        "description": "Alerts for audits, escalations, impersonations, or system flags.",
    },
    {
        "name": "BROADCAST",
        "description": "Platform-wide announcements and broadcasts.",
    },
    {
        "name": "SPECIAL_CLASSES",
        "description": "Special order class notifications, such as urgent academic sessions.",
    },
]

class Command(BaseCommand):
    help = "Seed default notification groups"

    def handle(self, *args, **options):
        created, skipped = 0, 0
        for group in DEFAULT_GROUPS:
            obj, was_created = NotificationGroup.objects.get_or_create(
                name=group["name"],
                defaults={
                    "description": group["description"],
                    "default_channel": NotificationChannel.IN_APP,
                    "default_priority": NotificationPriority.NORMAL,
                    "is_enabled_by_default": True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Created group: {obj.name}"))
            else:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"- Skipped existing group: {obj.name}"))

        self.stdout.write(self.style.SUCCESS(f"\n✅ Seeding complete — Created: {created}, Skipped: {skipped}"))