# notifications_system/management/commands/seed_notification_events.py
"""
Seed NotificationEvent and NotificationEventConfig rows from the
NotificationEvent enum defined in enums.py.

Run once on first deploy and again whenever new events are added to
the enum. Safe to run multiple times — uses get_or_create so existing
rows are never overwritten.

Usage:
    python manage.py seed_notification_events
    python manage.py seed_notification_events --website-id 1
    python manage.py seed_notification_events --dry-run
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.enums import (
    NotificationEvent as NotificationEventEnum,
    NotificationCategory,
    NotificationPriority,
    get_event_category,
)

# Events that must always fire regardless of user preferences.
# Extend this list as needed.
MANDATORY_EVENTS = {
    'account.suspended',
    'account.blacklisted',
    'account.deletion_scheduled',
    'writer.banned',
    'writer.suspended',
}

# Events that should NOT be disableable by users.
USER_CANNOT_DISABLE = {
    'account.suspended',
    'account.blacklisted',
    'account.deletion_scheduled',
    'writer.banned',
}

# Events that are in-app only (no email channel).
EMAIL_NOT_SUPPORTED = {
    'order.cancellation_requested',          # staff broadcast, in-app only
    'order.preferred_writer.fallback_to_pool',
    'order.preferred_writer.staff_visibility_reminder',
}

# Events eligible for digest batching.
DIGEST_ELIGIBLE = {
    'order.deadline_approaching',
    'order.rated',
    'ticket.comment_added',
    'message.new',
    'system.announcement',
}

# Default cooldown in seconds per event key.
# 0 = no cooldown (default).
COOLDOWNS = {
    'order.deadline_approaching': 3600, # 1 hour
    'wallet.balance_low': 86400, # 24 hours
    'message.new': 300, # 5 minutes
}


class Command(BaseCommand):
    help = 'Seed NotificationEvent and NotificationEventConfig rows from enums.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without writing to the DB.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        from notifications_system.models.notification_event import (
            NotificationEvent,
        )
        from notifications_system.models.event_config import (
            NotificationEventConfig,
        )

        created_events = 0
        created_configs = 0
        skipped = 0

        for enum_member in NotificationEventEnum:
            event_key = enum_member.value
            label = enum_member.label
            category = get_event_category(event_key)

            if dry_run:
                self.stdout.write(f' [dry-run] Would seed: {event_key}')
                continue

            # Seed NotificationEvent
            event, event_created = NotificationEvent.objects.get_or_create(
                event_key=event_key,
                defaults={
                    'label': label,
                    'category': category,
                    'is_active': True,
                },
            )

            if event_created:
                created_events += 1
                self.stdout.write(
                    self.style.SUCCESS(f' Created event: {event_key}')
                )
            else:
                skipped += 1

            # Seed NotificationEventConfig
            is_mandatory = event_key in MANDATORY_EVENTS
            user_can_disable = event_key not in USER_CANNOT_DISABLE
            digest_eligible = event_key in DIGEST_ELIGIBLE
            cooldown = COOLDOWNS.get(event_key, 0)

            # Infer priority — account/security events get HIGH
            if category in (NotificationCategory.ACCOUNT,) and is_mandatory:
                priority = NotificationPriority.HIGH
            else:
                priority = NotificationPriority.NORMAL

            email_supported = event_key not in EMAIL_NOT_SUPPORTED
            config, config_created = NotificationEventConfig.objects.get_or_create(
                event_key=event_key,
                defaults={
                    'label': label,
                    'supports_email': email_supported,
                    'supports_in_app': True,
                    'default_email_enabled': email_supported,
                    'default_in_app_enabled': True,
                    'priority': priority,
                    'is_mandatory': is_mandatory,
                    'user_can_disable': user_can_disable,
                    'admin_can_disable': not is_mandatory,
                    'digest_eligible': digest_eligible,
                    'cooldown_seconds': cooldown,
                    'is_active': True,
                },
            )

            if config_created:
                created_configs += 1

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\nDry run complete. '
                    f'{len(NotificationEventEnum)} events would be processed.'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. '
                f'Events: {created_events} created, {skipped} already existed. '
                f'Configs: {created_configs} created.'
            )
        )