# notifications_system/management/commands/seed_events.py
"""
Seed NotificationEvent rows from the NotificationEvent enum.
Run: python manage.py seed_events
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.enums import NotificationEvent, get_event_category
from notifications_system.models.notification_event import (
    NotificationEvent as NotificationEventModel
)


class Command(BaseCommand):
    help = 'Seed NotificationEvent rows from the enum.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing events.',
        )

    def handle(self, *args, **options):
        update = options['update']
        created = updated = skipped = 0

        for event_value, event_label in NotificationEvent.choices:
            category = get_event_category(event_value)

            obj, was_created = NotificationEventModel.objects.get_or_create(
                event_key=event_value,
                defaults={
                    'label': event_label,
                    'category': category,
                    'is_active': True,
                },
            )

            if was_created:
                created += 1
                self.stdout.write(f"  CREATE  {event_value}")
            elif update:
                obj.label = event_label
                obj.category = category
                obj.save(update_fields=['label', 'category'])
                updated += 1
                self.stdout.write(f"  UPDATE  {event_value}")
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created} | Updated: {updated} | Skipped: {skipped}"
            )
        )