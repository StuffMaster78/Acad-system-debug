# notifications_system/management/commands/seed_profiles.py

from django.core.management.base import BaseCommand
from notifications_system.models.notification_preferences import (
    NotificationPreferenceProfile
)

class Command(BaseCommand):
    help = "Seed default notification preference profiles for the system."

    def handle(self, *args, **kwargs):
        profiles = [
            {
                "name": "Minimal",
                "description": "In-app notifications only. No distractions.",
                "email_enabled": False,
                "sms_enabled": False,
                "push_enabled": False,
                "in_app_enabled": True,
                "dnd_enabled": False,
                "dnd_start_hour": 22,
                "dnd_end_hour": 6,
                "is_default": False,
            },
            {
                "name": "Aggressive",
                "description": "You will know everything the moment it happens — everywhere.",
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True,
                "in_app_enabled": True,
                "dnd_enabled": False,
                "dnd_start_hour": 0,
                "dnd_end_hour": 0,
                "is_default": True,
            },
            {
                "name": "Night Owl",
                "description": "Get everything, just not before 10am.",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "in_app_enabled": True,
                "dnd_enabled": True,
                "dnd_start_hour": 0,
                "dnd_end_hour": 10,
                "is_default": False,
            },
            {
                "name":"Balanced",
                "description": "A balanced approach to notifications.",
                "email_enabled": True,
                "sms_enabled": False,
                "push_enabled": True,
                "in_app_enabled": True,
                "dnd_enabled": True,
                "dnd_start_hour": 22,
                "dnd_end_hour": 6,
                "is_default": False,
            },
            {
                "name": "Custom",
                "description": "Customize your notification preferences.",
                "email_enabled": True,
                "sms_enabled": True,
                "push_enabled": True,
                "in_app_enabled": True,
                "dnd_enabled": False,
                "dnd_start_hour": 0,
                "dnd_end_hour": 0,
                "is_default": False,
            }

        ]

        for data in profiles:
            obj, created = NotificationPreferenceProfile.objects.update_or_create(
                name=data["name"], defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created profile: {obj.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated profile: {obj.name}"))