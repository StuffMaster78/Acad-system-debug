"""
Management command to seed writer payments with sample data.
Creates payments with various statuses, linked to orders and special orders.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from writer_payments_management.models import WriterPayment
from writer_management.models import WriterProfile
from orders.models import Order
from special_orders.models import SpecialOrder
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed writer payments with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing writer payments before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=25,
            help='Number of payments to create per website (default: 25)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        count = options.get('count', 25)

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
                self.stdout.write('Clearing existing writer payments...')
                WriterPayment.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            total_created = 0
            total_paid = 0
            total_pending = 0
            total_delayed = 0
            total_blocked = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Get writers for this website
                writer_profiles = WriterProfile.objects.filter(
                    website=website,
                    user__is_active=True
                )[:20]

                if not writer_profiles.exists():
                    self.stdout.write(
                        f'  ⚠ No writers found for {website.name}. Skipping.'
                    )
                    continue

                # Get completed orders for this website
                completed_orders = Order.objects.filter(
                    website=website,
                    status='completed',
                    assigned_writer__isnull=False
                ).select_related('assigned_writer')[:count * 2]

                # Get special orders for this website
                special_orders = SpecialOrder.objects.filter(
                    website=website,
                    status__in=['completed', 'in_progress', 'assigned']
                )[:count]

                # Payment amount ranges (base payment)
                base_amount_ranges = [
                    (Decimal('50.00'), Decimal('150.00')),   # Small orders
                    (Decimal('150.00'), Decimal('300.00')), # Medium orders
                    (Decimal('300.00'), Decimal('500.00')),  # Large orders
                    (Decimal('500.00'), Decimal('1000.00')), # Very large orders
                ]

                # Status distribution: 60% Paid, 25% Pending, 10% Delayed, 5% Blocked
                status_distribution = [
                    ('Paid', 0.60),
                    ('Pending', 0.25),
                    ('Delayed', 0.10),
                    ('Blocked', 0.05),
                ]

                payments_created = 0
                for i in range(count):
                    try:
                        # Select random writer profile
                        writer_profile = random.choice(writer_profiles)

                        # Determine if payment is for order or special order
                        order = None
                        special_order = None
                        base_amount = Decimal('0.00')
                        bonuses = Decimal('0.00')
                        fines = Decimal('0.00')
                        tips = Decimal('0.00')

                        rand = random.random()
                        if rand < 0.70 and completed_orders.exists():  # 70% order-based
                            # Find an order assigned to this writer
                            writer_orders = [o for o in completed_orders if o.assigned_writer == writer_profile.user]
                            if writer_orders:
                                order = random.choice(writer_orders)
                            else:
                                # Use any order but update writer
                                order = random.choice(completed_orders)
                                writer_profile = WriterProfile.objects.get(
                                    user=order.assigned_writer,
                                    website=website
                                )

                            # Check if payment already exists for this order
                            if WriterPayment.objects.filter(writer=writer_profile, order=order).exists():
                                continue

                            # Base amount
                            amount_range = random.choice(base_amount_ranges)
                            base_amount = Decimal(str(random.uniform(float(amount_range[0]), float(amount_range[1]))))
                            base_amount = base_amount.quantize(Decimal('0.01'))

                            # Bonuses (20% chance)
                            if random.random() < 0.20:
                                bonuses = Decimal(str(random.uniform(10.00, 50.00))).quantize(Decimal('0.01'))

                            # Fines (10% chance)
                            if random.random() < 0.10:
                                fines = Decimal(str(random.uniform(5.00, 25.00))).quantize(Decimal('0.01'))

                            # Tips (30% chance)
                            if random.random() < 0.30:
                                tips = Decimal(str(random.uniform(5.00, 50.00))).quantize(Decimal('0.01'))

                        elif rand < 0.85 and special_orders.exists():  # 15% special order-based
                            special_order = random.choice(special_orders)
                            if special_order.assigned_writer:
                                writer_profile = WriterProfile.objects.get(
                                    user=special_order.assigned_writer,
                                    website=website
                                )

                            # Base amount for special order
                            base_amount = Decimal(str(random.uniform(200.00, 800.00))).quantize(Decimal('0.01'))

                            # Special orders often have bonuses
                            if random.random() < 0.50:
                                bonuses = Decimal(str(random.uniform(25.00, 100.00))).quantize(Decimal('0.01'))

                        else:  # 15% standalone payments (no order)
                            # Base amount
                            amount_range = random.choice(base_amount_ranges)
                            base_amount = Decimal(str(random.uniform(float(amount_range[0]), float(amount_range[1]))))
                            base_amount = base_amount.quantize(Decimal('0.01'))

                            # Bonuses (30% chance)
                            if random.random() < 0.30:
                                bonuses = Decimal(str(random.uniform(10.00, 50.00))).quantize(Decimal('0.01'))

                            # Tips (40% chance)
                            if random.random() < 0.40:
                                tips = Decimal(str(random.uniform(5.00, 50.00))).quantize(Decimal('0.01'))

                        # Calculate total amount
                        total_amount = base_amount + bonuses + tips - fines
                        total_amount = max(total_amount, Decimal('0.00'))  # Ensure non-negative

                        # Select status
                        rand_status = random.random()
                        cumulative = 0
                        status = 'Pending'
                        for stat, prob in status_distribution:
                            cumulative += prob
                            if rand_status <= cumulative:
                                status = stat
                                break

                        # Create payment
                        payment = WriterPayment.objects.create(
                            website=website,
                            writer=writer_profile,
                            order=order,
                            special_order=special_order,
                            amount=total_amount,
                            bonuses=bonuses,
                            fines=fines,
                            tips=tips,
                            status=status,
                            processed_at=timezone.now() - timedelta(days=random.randint(1, 90)) if status == 'Paid' else None,
                            transaction_reference=f"TXN-{random.randint(100000, 999999)}" if status == 'Paid' else None,
                        )

                        payments_created += 1
                        total_created += 1

                        if status == 'Paid':
                            total_paid += 1
                        elif status == 'Pending':
                            total_pending += 1
                        elif status == 'Delayed':
                            total_delayed += 1
                        else:
                            total_blocked += 1

                        entity_info = ""
                        if order:
                            entity_info = f" | Order #{order.id}"
                        elif special_order:
                            entity_info = f" | Special Order #{special_order.id}"

                        self.stdout.write(
                            f'  ✓ Created payment #{payment.id} | '
                            f'{writer_profile.user.email} | ${total_amount} | '
                            f'{status} | Base: ${base_amount} | '
                            f'Bonuses: ${bonuses} | Tips: ${tips} | Fines: ${fines}{entity_info}'
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Failed to create payment: {str(e)}'
                            )
                        )
                        continue

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created:\n'
                    f'  - {total_created} total payments\n'
                    f'  - {total_paid} paid payments\n'
                    f'  - {total_pending} pending payments\n'
                    f'  - {total_delayed} delayed payments\n'
                    f'  - {total_blocked} blocked payments'
                )
            )

