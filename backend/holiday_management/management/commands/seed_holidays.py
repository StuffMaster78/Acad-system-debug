"""
Management command to seed common holidays and special days.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from holiday_management.models import SpecialDay
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed common holidays and special days'

    def handle(self, *args, **options):
        self.stdout.write('Seeding holidays and special days...')
        
        # Get or create a superadmin user for created_by
        admin = User.objects.filter(role='superadmin').first()
        if not admin:
            admin = User.objects.filter(role='admin').first()
        
        # US Holidays
        us_holidays = [
            {
                'name': 'Thanksgiving Day',
                'description': 'Thanksgiving Day in the United States',
                'event_type': 'holiday',
                'date': timezone.datetime(2024, 11, 28).date(),  # 4th Thursday of November
                'is_annual': True,
                'is_international': False,
                'countries': ['US'],
                'priority': 'high',
                'reminder_days_before': 7,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 15.00,
                'discount_code_prefix': 'THANKS',
                'discount_valid_days': 3,
                'broadcast_message_template': 'Happy Thanksgiving! We\'re grateful for your business. Use code {code} for {discount}% off!',
            },
            {
                'name': 'Black Friday',
                'description': 'Black Friday shopping day',
                'event_type': 'special_day',
                'date': timezone.datetime(2024, 11, 29).date(),
                'is_annual': True,
                'is_international': False,
                'countries': ['US'],
                'priority': 'critical',
                'reminder_days_before': 14,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 20.00,
                'discount_code_prefix': 'BLACKFRIDAY',
                'discount_valid_days': 1,
            },
            {
                'name': 'Cyber Monday',
                'description': 'Cyber Monday online shopping day',
                'event_type': 'special_day',
                'date': timezone.datetime(2024, 12, 2).date(),
                'is_annual': True,
                'is_international': False,
                'countries': ['US'],
                'priority': 'critical',
                'reminder_days_before': 14,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 20.00,
                'discount_code_prefix': 'CYBER',
                'discount_valid_days': 1,
            },
            {
                'name': 'Veterans Day',
                'description': 'Veterans Day in the United States',
                'event_type': 'holiday',
                'date': timezone.datetime(2024, 11, 11).date(),
                'is_annual': True,
                'is_international': False,
                'countries': ['US'],
                'priority': 'high',
                'reminder_days_before': 7,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 10.00,
                'discount_code_prefix': 'VETERANS',
                'discount_valid_days': 1,
            },
            {
                'name': 'Christmas Day',
                'description': 'Christmas Day',
                'event_type': 'holiday',
                'date': timezone.datetime(2024, 12, 25).date(),
                'is_annual': True,
                'is_international': True,
                'countries': [],
                'priority': 'critical',
                'reminder_days_before': 14,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 25.00,
                'discount_code_prefix': 'CHRISTMAS',
                'discount_valid_days': 7,
            },
            {
                'name': 'New Year\'s Day',
                'description': 'New Year\'s Day',
                'event_type': 'holiday',
                'date': timezone.datetime(2025, 1, 1).date(),
                'is_annual': True,
                'is_international': True,
                'countries': [],
                'priority': 'high',
                'reminder_days_before': 7,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 15.00,
                'discount_code_prefix': 'NEWYEAR',
                'discount_valid_days': 3,
            },
            {
                'name': 'Valentine\'s Day',
                'description': 'Valentine\'s Day',
                'event_type': 'holiday',
                'date': timezone.datetime(2025, 2, 14).date(),
                'is_annual': True,
                'is_international': True,
                'countries': [],
                'priority': 'high',
                'reminder_days_before': 7,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 15.00,
                'discount_code_prefix': 'VALENTINE',
                'discount_valid_days': 3,
            },
            {
                'name': 'Independence Day',
                'description': 'Independence Day in the United States',
                'event_type': 'holiday',
                'date': timezone.datetime(2025, 7, 4).date(),
                'is_annual': True,
                'is_international': False,
                'countries': ['US'],
                'priority': 'high',
                'reminder_days_before': 7,
                'send_broadcast_reminder': True,
                'auto_generate_discount': True,
                'discount_percentage': 10.00,
                'discount_code_prefix': 'JULY4',
                'discount_valid_days': 3,
            },
        ]
        
        created_count = 0
        for holiday_data in us_holidays:
            countries = holiday_data.pop('countries', [])
            holiday, created = SpecialDay.objects.get_or_create(
                name=holiday_data['name'],
                date=holiday_data['date'],
                defaults={
                    **holiday_data,
                    'created_by': admin,
                    'countries': countries
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {holiday.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Already exists: {holiday.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSeeded {created_count} new holidays!')
        )

