# notifications_system/management/commands/validate_templates.py
"""
Validates that all active notification events have templates
for all supported channels.

Run: python manage.py validate_templates
Run: python manage.py validate_templates --fix   (seeds missing ones)
Run: python manage.py validate_templates --channel email
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.enums import NotificationChannel
from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.event_config import NotificationEventConfig
from notifications_system.models.notifications_template import NotificationTemplate


class Command(BaseCommand):
    help = 'Validate template coverage for all active notification events.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--channel',
            type=str,
            default=None,
            help='Check a specific channel only (email or in_app)',
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Auto-seed missing templates with placeholder content.',
        )
        parser.add_argument(
            '--strict',
            action='store_true',
            help='Exit with code 1 if any templates are missing.',
        )

    def handle(self, *args, **options):
        channel_filter = options['channel']
        fix = options['fix']
        strict = options['strict']

        channels = [channel_filter] if channel_filter else [
            NotificationChannel.EMAIL,
            NotificationChannel.IN_APP,
        ]

        events = NotificationEvent.objects.filter(is_active=True)
        missing = []
        ok_count = 0

        self.stdout.write(f"\nChecking {events.count()} active events "
                          f"across {len(channels)} channel(s)...\n")

        for event in events.order_by('category', 'event_key'):
            # Get which channels this event supports
            try:
                config = NotificationEventConfig.objects.get(event=event)
                supported_channels = []
                if config.supports_email and NotificationChannel.EMAIL in channels:
                    supported_channels.append(NotificationChannel.EMAIL)
                if config.supports_in_app and NotificationChannel.IN_APP in channels:
                    supported_channels.append(NotificationChannel.IN_APP)
            except NotificationEventConfig.DoesNotExist:
                supported_channels = channels

            for channel in supported_channels:
                exists = NotificationTemplate.objects.filter(
                    event=event,
                    channel=channel,
                    is_active=True,
                ).exists()

                if exists:
                    ok_count += 1
                else:
                    missing.append((event, channel))
                    self.stdout.write(
                        self.style.WARNING(
                            f"  MISSING  {event.event_key:<45} [{channel}]"
                        )
                    )

                    if fix:
                        self._create_placeholder(event, channel)

        # Summary
        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f"  OK       {ok_count} template(s) found")
        )

        if missing:
            self.stdout.write(
                self.style.ERROR(
                    f"  MISSING  {len(missing)} template(s) not found"
                )
            )
            self.stdout.write(
                '\nRun with --fix to create placeholders, '
                'or run seed_templates to seed defaults.\n'
            )
            if strict:
                raise SystemExit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ All templates are present.\n')
            )

    def _create_placeholder(self, event, channel):
        """Create a placeholder template so the system doesn't crash on delivery."""
        from notifications_system.models.notifications_template import NotificationTemplate

        defaults = {
            'locale': 'en',
            'version': 1,
            'is_active': True,
            'available_variables': [],
        }

        if channel == NotificationChannel.EMAIL:
            defaults.update({
                'subject': f'[{event.label}]',
                'body_text': f'You have a new notification: {event.label}',
                'body_html': (
                    f'<p>You have a new notification: <strong>{event.label}</strong></p>'
                ),
            })
        else:
            defaults.update({
                'title': event.label,
                'message': f'You have a new notification.',
            })

        NotificationTemplate.objects.get_or_create(
            event=event,
            channel=channel,
            website=None,
            locale='en',
            defaults=defaults,
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"    → Created placeholder for {event.event_key} [{channel}]"
            )
        )