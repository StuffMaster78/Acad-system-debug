"""
Management command to seed special order configurations and simulate special orders.
Creates predefined order configs, duration options, estimated settings, and sample orders.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from special_orders.models import (
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    EstimatedSpecialOrderSettings,
    SpecialOrder,
)
from users.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed special order configurations and simulate special orders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--create-orders',
            action='store_true',
            help='Also create sample special orders (requires existing clients)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing configs and settings before seeding',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        create_orders = options.get('create_orders', False)
        clear = options.get('clear', False)

        # Get websites to process
        if website_id:
            websites = Website.objects.filter(id=website_id)
            if not websites.exists():
                self.stdout.write(
                    self.style.ERROR(f'Website with ID {website_id} not found')
                )
                return
        else:
            websites = Website.objects.filter(is_active=True)

        if not websites.exists():
            self.stdout.write(
                self.style.WARNING('No active websites found')
            )
            return

        with transaction.atomic():
            if clear:
                self.stdout.write('Clearing existing special order configs and settings...')
                SpecialOrder.objects.all().delete()
                PredefinedSpecialOrderDuration.objects.all().delete()
                PredefinedSpecialOrderConfig.objects.all().delete()
                EstimatedSpecialOrderSettings.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Predefined order types to create
            predefined_configs = [
                {
                    'name': 'Shadow Health',
                    'description': 'Shadow Health assignments and assessments',
                    'durations': [
                        {'days': 2, 'price': Decimal('250.00')},
                        {'days': 3, 'price': Decimal('350.00')},
                        {'days': 5, 'price': Decimal('500.00')},
                        {'days': 7, 'price': Decimal('650.00')},
                        {'days': 10, 'price': Decimal('850.00')},
                    ]
                },
                {
                    'name': 'ATI Comprehensive',
                    'description': 'ATI Comprehensive assessments and practice tests',
                    'durations': [
                        {'days': 2, 'price': Decimal('200.00')},
                        {'days': 3, 'price': Decimal('280.00')},
                        {'days': 5, 'price': Decimal('400.00')},
                        {'days': 7, 'price': Decimal('520.00')},
                        {'days': 10, 'price': Decimal('680.00')},
                    ]
                },
                {
                    'name': 'HESI Exam Prep',
                    'description': 'HESI exam preparation and practice materials',
                    'durations': [
                        {'days': 3, 'price': Decimal('300.00')},
                        {'days': 5, 'price': Decimal('450.00')},
                        {'days': 7, 'price': Decimal('600.00')},
                        {'days': 10, 'price': Decimal('750.00')},
                    ]
                },
                {
                    'name': 'NCLEX Review',
                    'description': 'NCLEX review sessions and practice questions',
                    'durations': [
                        {'days': 3, 'price': Decimal('320.00')},
                        {'days': 5, 'price': Decimal('480.00')},
                        {'days': 7, 'price': Decimal('640.00')},
                        {'days': 10, 'price': Decimal('800.00')},
                    ]
                },
                {
                    'name': 'Custom Project',
                    'description': 'Custom special order projects',
                    'durations': [
                        {'days': 2, 'price': Decimal('180.00')},
                        {'days': 3, 'price': Decimal('250.00')},
                        {'days': 5, 'price': Decimal('380.00')},
                        {'days': 7, 'price': Decimal('500.00')},
                        {'days': 10, 'price': Decimal('650.00')},
                    ]
                },
            ]

            total_configs = 0
            total_durations = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Create estimated order settings
                settings, created = EstimatedSpecialOrderSettings.objects.get_or_create(
                    website=website,
                    defaults={
                        'default_deposit_percentage': Decimal('50.00'),
                    }
                )
                if created:
                    self.stdout.write(
                        f'  ✓ Created estimated order settings: {settings.default_deposit_percentage}% deposit'
                    )
                else:
                    self.stdout.write(
                        f'  - Estimated order settings already exist: {settings.default_deposit_percentage}% deposit'
                    )

                # Create predefined order configs
                for config_data in predefined_configs:
                    # Create config (name must be unique globally, so we add website prefix)
                    config_name = f"{website.name} - {config_data['name']}"
                    # Check if config exists with this name
                    try:
                        config = PredefinedSpecialOrderConfig.objects.get(name=config_name)
                        config_created = False
                        # Update if exists
                        config.description = config_data['description']
                        config.website = website
                        config.is_active = True
                        config.save()
                    except PredefinedSpecialOrderConfig.DoesNotExist:
                        config = PredefinedSpecialOrderConfig.objects.create(
                            name=config_name,
                            description=config_data['description'],
                            website=website,
                            is_active=True,
                        )
                        config_created = True
                    
                    if config_created:
                        total_configs += 1
                        self.stdout.write(
                            f'  ✓ Created predefined config: {config.name}'
                        )
                    else:
                        # Update if exists
                        config.description = config_data['description']
                        config.website = website
                        config.is_active = True
                        config.save()
                        self.stdout.write(
                            f'  ↻ Updated predefined config: {config.name}'
                        )

                    # Create duration options for this config
                    for duration_data in config_data['durations']:
                        duration, dur_created = PredefinedSpecialOrderDuration.objects.get_or_create(
                            predefined_order=config,
                            duration_days=duration_data['days'],
                            defaults={
                                'website': website,
                                'price': duration_data['price'],
                            }
                        )
                        if dur_created:
                            total_durations += 1
                            self.stdout.write(
                                f'    ✓ Created duration: {duration.duration_days} days @ ${duration.price}'
                            )
                        else:
                            # Update price if exists
                            if duration.price != duration_data['price']:
                                duration.price = duration_data['price']
                                duration.website = website
                                duration.save()
                                self.stdout.write(
                                    f'    ↻ Updated duration: {duration.duration_days} days @ ${duration.price}'
                                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created/updated:\n'
                    f'  - {total_configs} predefined order configs\n'
                    f'  - {total_durations} duration options\n'
                    f'  - Estimated order settings for all websites'
                )
            )

            # Create sample special orders if requested
            if create_orders:
                self.create_sample_orders(websites)

    def create_sample_orders(self, websites):
        """Create sample special orders for testing"""
        self.stdout.write('\nCreating sample special orders...')

        # Get some clients
        clients = User.objects.filter(role='client', is_active=True)[:5]
        if not clients.exists():
            self.stdout.write(
                self.style.WARNING('No active clients found. Skipping order creation.')
            )
            return

        # Get some writers
        writers = User.objects.filter(role='writer', is_active=True)[:3]
        if not writers.exists():
            self.stdout.write(
                self.style.WARNING('No active writers found. Skipping order creation.')
            )
            return

        total_orders = 0

        for website in websites:
            # Get predefined configs for this website
            configs = PredefinedSpecialOrderConfig.objects.filter(
                website=website,
                is_active=True
            )[:3]  # Limit to 3 configs per website

            if not configs.exists():
                continue

            # Create 2-3 predefined orders per website
            for i, config in enumerate(configs[:3]):
                if i >= len(clients):
                    break

                client = clients[i % len(clients)]
                writer = writers[i % len(writers)] if writers.exists() else None

                # Get a duration option
                duration_option = config.durations.first()
                if not duration_option:
                    continue

                order = SpecialOrder.objects.create(
                    client=client,
                    website=website,
                    writer=writer,
                    order_type='predefined',
                    predefined_type=config,
                    inquiry_details=f'Sample inquiry for {config.name} - {duration_option.duration_days} days',
                    duration_days=duration_option.duration_days,
                    total_cost=duration_option.price,
                    deposit_required=duration_option.price,  # Full payment for predefined
                    status='in_progress' if writer else 'awaiting_approval',
                    is_approved=True if writer else False,
                )

                total_orders += 1
                self.stdout.write(
                    f'  ✓ Created predefined order #{order.id} for {client.email} | '
                    f'{config.name} | {duration_option.duration_days} days | ${order.total_cost}'
                )

            # Create 1-2 estimated orders per website
            for i in range(2):
                if (i + 3) >= len(clients):
                    break

                client = clients[(i + 3) % len(clients)]
                writer = writers[i % len(writers)] if writers.exists() else None

                # Get estimated settings
                try:
                    settings = website.estimated_order_settings
                    deposit_percent = settings.default_deposit_percentage
                except EstimatedSpecialOrderSettings.DoesNotExist:
                    deposit_percent = Decimal('50.00')

                duration_days = [3, 5, 7][i % 3]
                price_per_day = Decimal('100.00')
                total_cost = duration_days * price_per_day
                deposit_required = total_cost * (deposit_percent / 100)

                order = SpecialOrder.objects.create(
                    client=client,
                    website=website,
                    writer=writer,
                    order_type='estimated',
                    inquiry_details=f'Sample estimated order inquiry - {duration_days} days project',
                    duration_days=duration_days,
                    price_per_day=price_per_day,
                    total_cost=total_cost,
                    deposit_required=deposit_required,
                    admin_approved_cost=total_cost,
                    status='in_progress' if writer else 'awaiting_approval',
                    is_approved=True if writer else False,
                )

                total_orders += 1
                self.stdout.write(
                    f'  ✓ Created estimated order #{order.id} for {client.email} | '
                    f'{duration_days} days | ${total_cost} total | ${deposit_required} deposit'
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created {total_orders} sample special orders')
        )

