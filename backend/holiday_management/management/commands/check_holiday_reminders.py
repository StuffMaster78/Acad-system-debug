"""
Management command to check for holiday reminders and create them.
Should be run daily via cron or Celery Beat.
"""
from django.core.management.base import BaseCommand
from holiday_management.services import (
    HolidayReminderService,
    HolidayDiscountService,
    HolidayNotificationService
)


class Command(BaseCommand):
    help = 'Check for upcoming special days and create reminders, generate discounts, and notify admins'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-generate-discounts',
            action='store_true',
            help='Auto-generate discount codes for upcoming special days',
        )
        parser.add_argument(
            '--notify-admins',
            action='store_true',
            help='Send notifications to admins about pending reminders',
        )

    def handle(self, *args, **options):
        self.stdout.write('Checking for holiday reminders...')
        
        # Check and create reminders
        reminders = HolidayReminderService.check_and_create_reminders()
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(reminders)} new reminders')
        )
        
        # Auto-generate discounts if requested
        if options['auto_generate_discounts']:
            discounts = HolidayDiscountService.auto_generate_discounts_for_upcoming()
            self.stdout.write(
                self.style.SUCCESS(f'Generated {len(discounts)} discount codes')
            )
        
        # Notify admins if requested
        if options['notify_admins']:
            HolidayNotificationService.notify_admins_of_upcoming_holidays()
            self.stdout.write(
                self.style.SUCCESS('Notifications sent to admins')
            )
        
        self.stdout.write(self.style.SUCCESS('Holiday reminder check completed!'))

