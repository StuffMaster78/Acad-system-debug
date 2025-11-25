"""
Management command to seed class bundle configurations and simulate classes.
Creates duration options and bundle configs for all websites.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from class_management.models import ClassDurationOption, ClassBundleConfig, ClassBundle
from users.models import User
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed class bundle configurations and simulate class bundles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--create-bundles',
            action='store_true',
            help='Also create sample class bundles (requires existing clients)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing configs and duration options before seeding',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        create_bundles = options.get('create_bundles', False)
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
                self.stdout.write('Clearing existing class configs and duration options...')
                ClassBundleConfig.objects.all().delete()
                ClassDurationOption.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Duration options to create
            duration_configs = [
                {'class_code': '8-10', 'label': '8–10 weeks'},
                {'class_code': '12-14', 'label': '12–14 weeks'},
                {'class_code': '15-16', 'label': '15–16 weeks'},
                {'class_code': '16-18', 'label': '16–18 weeks'},
            ]

            # Bundle configs to create
            # Format: (level, bundle_size, price_per_class)
            bundle_configs = [
                # Undergraduate configs
                ('undergrad', 1, Decimal('150.00')),
                ('undergrad', 2, Decimal('145.00')),
                ('undergrad', 3, Decimal('140.00')),
                ('undergrad', 4, Decimal('135.00')),
                ('undergrad', 5, Decimal('130.00')),
                ('undergrad', 6, Decimal('125.00')),
                ('undergrad', 8, Decimal('120.00')),
                ('undergrad', 10, Decimal('115.00')),
                # Graduate configs
                ('grad', 1, Decimal('200.00')),
                ('grad', 2, Decimal('195.00')),
                ('grad', 3, Decimal('190.00')),
                ('grad', 4, Decimal('185.00')),
                ('grad', 5, Decimal('180.00')),
                ('grad', 6, Decimal('175.00')),
                ('grad', 8, Decimal('170.00')),
                ('grad', 10, Decimal('165.00')),
            ]

            total_durations = 0
            total_configs = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Create duration options
                for dur_config in duration_configs:
                    duration, created = ClassDurationOption.objects.get_or_create(
                        website=website,
                        class_code=dur_config['class_code'],
                        defaults={
                            'label': dur_config['label'],
                            'is_active': True,
                        }
                    )
                    if created:
                        total_durations += 1
                        self.stdout.write(
                            f'  ✓ Created duration option: {duration.label}'
                        )
                    else:
                        self.stdout.write(
                            f'  - Duration option already exists: {duration.label}'
                        )

                # Get all duration options for this website
                duration_options = ClassDurationOption.objects.filter(
                    website=website,
                    is_active=True
                )

                # Create bundle configs for each duration
                for duration_option in duration_options:
                    for level, bundle_size, price_per_class in bundle_configs:
                        config, created = ClassBundleConfig.objects.get_or_create(
                            website=website,
                            duration=duration_option,
                            level=level,
                            bundle_size=bundle_size,
                            defaults={
                                'price_per_class': price_per_class,
                                'is_active': True,
                            }
                        )
                        if created:
                            total_configs += 1
                            self.stdout.write(
                                f'  ✓ Created config: {config.get_level_display()} | '
                                f'{duration_option.label} | {bundle_size} classes @ ${price_per_class}/class'
                            )
                        else:
                            # Update price if config exists
                            if config.price_per_class != price_per_class:
                                config.price_per_class = price_per_class
                                config.save()
                                self.stdout.write(
                                    f'  ↻ Updated config: {config.get_level_display()} | '
                                    f'{duration_option.label} | {bundle_size} classes @ ${price_per_class}/class'
                                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created/updated:\n'
                    f'  - {total_durations} duration options\n'
                    f'  - {total_configs} bundle configurations'
                )
            )

            # Create sample class bundles if requested
            if create_bundles:
                self.create_sample_bundles(websites)

    def create_sample_bundles(self, websites):
        """Create sample class bundles for testing"""
        self.stdout.write('\nCreating sample class bundles...')

        # Get some clients
        clients = User.objects.filter(role='client', is_active=True)[:5]
        if not clients.exists():
            self.stdout.write(
                self.style.WARNING('No active clients found. Skipping bundle creation.')
            )
            return

        # Get some writers
        writers = User.objects.filter(role='writer', is_active=True)[:3]
        if not writers.exists():
            self.stdout.write(
                self.style.WARNING('No active writers found. Skipping bundle creation.')
            )
            return

        total_bundles = 0

        for website in websites:
            # Get active configs for this website
            configs = ClassBundleConfig.objects.filter(
                website=website,
                is_active=True
            )[:10]  # Limit to 10 configs per website

            if not configs.exists():
                continue

            # Create 2-3 bundles per website
            for i, config in enumerate(configs[:3]):
                if i >= len(clients):
                    break

                client = clients[i % len(clients)]
                writer = writers[i % len(writers)] if writers.exists() else None

                # Calculate dates
                start_date = timezone.now().date() + timedelta(days=i * 7)
                end_date = start_date + timedelta(weeks=16)

                bundle = ClassBundle.objects.create(
                    client=client,
                    website=website,
                    assigned_writer=writer,
                    config=config,
                    pricing_source='config',
                    duration=config.duration.class_code,
                    level=config.level,
                    bundle_size=config.bundle_size,
                    price_per_class=config.price_per_class,
                    number_of_classes=config.bundle_size,
                    start_date=start_date,
                    end_date=end_date,
                    total_price=config.total_price,
                    status=ClassBundle.IN_PROGRESS,
                )

                total_bundles += 1
                self.stdout.write(
                    f'  ✓ Created bundle #{bundle.id} for {client.email} | '
                    f'{config.get_level_display()} | {config.bundle_size} classes | ${bundle.total_price}'
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Created {total_bundles} sample class bundles')
        )

