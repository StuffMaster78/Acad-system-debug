# notifications_system/management/commands/seed_event_configs.py
"""
Seed NotificationEventConfig rows for all active events.
Run after seed_events: python manage.py seed_event_configs
"""
from __future__ import annotations

from django.core.management.base import BaseCommand

from notifications_system.models.notification_event import NotificationEvent
from notifications_system.models.event_config import NotificationEventConfig
from notifications_system.enums import NotificationPriority


# Default config per event key
# Override any of these per event as needed
EVENT_CONFIG_DEFAULTS = {
    # Mandatory events — always send regardless of preferences
    'account.suspended': {
        'is_mandatory': True,
        'user_can_disable': False,
        'priority': NotificationPriority.CRITICAL,
    },
    'account.blacklisted': {
        'is_mandatory': True,
        'user_can_disable': False,
        'priority': NotificationPriority.CRITICAL,
    },
    'account.deletion_scheduled': {
        'is_mandatory': True,
        'user_can_disable': False,
        'priority': NotificationPriority.CRITICAL,
    },
    'account.login_new_device': {
        'is_mandatory': True,
        'user_can_disable': False,
        'priority': NotificationPriority.HIGH,
    },
    'account.password_changed': {
        'is_mandatory': True,
        'user_can_disable': False,
        'priority': NotificationPriority.HIGH,
    },

    # High priority
    'order.disputed': {
        'priority': NotificationPriority.HIGH,
        'recipient_roles': ['client', 'writer', 'support'],
    },
    'order.deadline_approaching': {
        'priority': NotificationPriority.HIGH,
        'recipient_roles': ['writer'],
        'cooldown_seconds': 3600,
    },
    'payout.failed': {
        'priority': NotificationPriority.HIGH,
        'recipient_roles': ['writer'],
    },
    'wallet.balance_low': {
        'priority': NotificationPriority.HIGH,
        'cooldown_seconds': 86400,  # once per day max
    },

    # Digest eligible — group into daily summary
    'order.rated': {
        'digest_eligible': True,
        'digest_group': 'daily_summary',
        'recipient_roles': ['writer'],
    },
    'writer.badge_earned': {
        'digest_eligible': True,
        'digest_group': 'daily_summary',
        'recipient_roles': ['writer'],
    },
    'ticket.comment_added': {
        'digest_eligible': True,
        'digest_group': 'daily_summary',
        'cooldown_seconds': 300,  # 5 min cooldown per ticket
    },

    # Role-specific recipients
    'order.created': {
        'recipient_roles': ['client'],
    },
    'order.assigned': {
        'recipient_roles': ['writer', 'client'],
    },
    'order.completed': {
        'recipient_roles': ['client', 'writer'],
    },
    'order.cancelled': {
        'recipient_roles': ['client', 'writer'],
    },
    'order.revision_requested': {
        'recipient_roles': ['writer'],
    },
    'payout.requested': {
        'recipient_roles': ['support', 'admin'],
    },
    'payout.completed': {
        'recipient_roles': ['writer'],
    },
    'ticket.created': {
        'recipient_roles': ['support'],
    },
    'ticket.assigned': {
        'recipient_roles': ['support'],
    },
    'ticket.resolved': {
        'recipient_roles': ['client'],
    },
    'writer.approved': {
        'recipient_roles': ['writer'],
    },
    'writer.rejected': {
        'recipient_roles': ['writer'],
    },
    'writer.warning': {
        'recipient_roles': ['writer'],
        'priority': NotificationPriority.HIGH,
    },
}

# Default config applied to all events not in EVENT_CONFIG_DEFAULTS
GLOBAL_DEFAULTS = {
    'supports_email': True,
    'supports_in_app': True,
    'default_email_enabled': True,
    'default_in_app_enabled': True,
    'priority': NotificationPriority.NORMAL,
    'is_mandatory': False,
    'user_can_disable': True,
    'admin_can_disable': True,
    'digest_eligible': False,
    'is_overridable_per_website': True,
    'cooldown_seconds': 0,
    'recipient_roles': [],
}


class Command(BaseCommand):
    help = 'Seed NotificationEventConfig rows for all active events.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='Update existing configs.',
        )

    def handle(self, *args, **options):
        update = options['update']
        created = updated = skipped = 0

        events = NotificationEvent.objects.filter(is_active=True)

        for event in events:
            overrides = EVENT_CONFIG_DEFAULTS.get(event.event_key, {})
            config_data = {**GLOBAL_DEFAULTS, **overrides}
            config_data['label'] = event.label
            config_data['description'] = f"Notifications for {event.label}"

            obj, was_created = NotificationEventConfig.objects.get_or_create(
                event=event,
                defaults=config_data,
            )

            if was_created:
                created += 1
                self.stdout.write(f"  CREATE  {event.event_key}")
            elif update:
                for field, value in config_data.items():
                    setattr(obj, field, value)
                obj.save()
                updated += 1
                self.stdout.write(f"  UPDATE  {event.event_key}")
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created} | Updated: {updated} | Skipped: {skipped}"
            )
        )