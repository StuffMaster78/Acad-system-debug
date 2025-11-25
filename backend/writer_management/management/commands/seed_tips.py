"""
Management command to seed tips with sample data.
Creates direct tips, order-based tips, and class/task-based tips.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from websites.models import Website
from writer_management.models.tipping import Tip
from writer_management.services.tip_service import TipService
from orders.models import Order
from class_management.models import ClassBundle, ExpressClass
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed tips with sample data (direct, order-based, and class-based tips)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing tips before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of tips to create per website (default: 20)',
        )

    def handle(self, *args, **options):
        website_id = options.get('website_id')
        clear = options.get('clear', False)
        count = options.get('count', 20)

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
                self.stdout.write('Clearing existing tips...')
                Tip.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Get clients and writers
            clients = list(User.objects.filter(role='client', is_active=True)[:30])
            writers = list(User.objects.filter(role='writer', is_active=True)[:15])

            if not clients or not writers:
                self.stdout.write(
                    self.style.WARNING('No active clients or writers found. Skipping tip creation.')
                )
                return

            # Sample tip reasons
            tip_reasons = [
                "Excellent work! Thank you for the quality service.",
                "Great job on the order. Really appreciate your effort.",
                "Outstanding quality and attention to detail.",
                "Very satisfied with the work. Keep it up!",
                "Thank you for meeting the deadline and delivering quality work.",
                "Amazing work! Exceeded my expectations.",
                "Professional service and timely delivery. Highly recommended!",
                "Great communication throughout the process. Thank you!",
                "Excellent writing quality. Will definitely work with you again.",
                "Thank you for your dedication and hard work.",
                "Outstanding performance on this project.",
                "Really appreciate the extra effort you put in.",
                "Great job! The work was exactly what I needed.",
                "Thank you for being so responsive and professional.",
                "Excellent service! Very happy with the results.",
            ]

            # Tip amount ranges (in dollars)
            tip_amounts = [
                Decimal('5.00'), Decimal('10.00'), Decimal('15.00'),
                Decimal('20.00'), Decimal('25.00'), Decimal('30.00'),
                Decimal('50.00'), Decimal('75.00'), Decimal('100.00'),
            ]

            total_direct_tips = 0
            total_order_tips = 0
            total_class_tips = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Get website-specific data
                website_clients = [c for c in clients if c.website_id == website.id]
                website_writers = [w for w in writers if w.website_id == website.id]
                
                if not website_clients or not website_writers:
                    self.stdout.write(
                        f'  ⚠ No clients or writers found for {website.name}. Skipping.'
                    )
                    continue

                # Get completed orders for this website
                completed_orders = Order.objects.filter(
                    website=website,
                    status='completed',
                    is_paid=True,
                    assigned_writer__isnull=False
                )[:count * 2]

                # Get class bundles for this website
                class_bundles = ClassBundle.objects.filter(
                    website=website,
                    status__in=[ClassBundle.IN_PROGRESS, ClassBundle.COMPLETED],
                    assigned_writer__isnull=False
                )[:count]

                # Get express classes for this website
                express_classes = ExpressClass.objects.filter(
                    website=website,
                    status__in=[ExpressClass.IN_PROGRESS, ExpressClass.COMPLETED],
                    assigned_writer__isnull=False
                )[:count]

                # Tip type distribution: 40% direct, 40% order-based, 20% class-based
                tip_type_distribution = [
                    ('direct', 0.40),
                    ('order', 0.40),
                    ('class', 0.20),
                ]

                tips_created = 0
                for i in range(count):
                    # Select tip type
                    rand = random.random()
                    cumulative = 0
                    tip_type = 'direct'
                    for ttype, prob in tip_type_distribution:
                        cumulative += prob
                        if rand <= cumulative:
                            tip_type = ttype
                            break

                    # Select random client and writer
                    client = random.choice(website_clients)
                    writer = random.choice(website_writers)

                    # Select tip amount
                    tip_amount = random.choice(tip_amounts)
                    tip_reason = random.choice(tip_reasons)

                    order = None
                    related_entity_type = None
                    related_entity_id = None

                    try:
                        if tip_type == 'order':
                            if not completed_orders.exists():
                                # Fall back to direct tip if no orders
                                tip_type = 'direct'
                            else:
                                order = random.choice(completed_orders)
                                # Ensure order's writer matches selected writer
                                if order.assigned_writer != writer:
                                    # Try to find an order with this writer
                                    writer_orders = [o for o in completed_orders if o.assigned_writer == writer]
                                    if writer_orders:
                                        order = random.choice(writer_orders)
                                    else:
                                        # Use any order but update writer
                                        writer = order.assigned_writer

                        elif tip_type == 'class':
                            # Choose between class bundle and express class
                            entity_choices = []
                            if class_bundles.exists():
                                for bundle in class_bundles:
                                    if bundle.assigned_writer == writer:
                                        entity_choices.append(('class_bundle', bundle.id))
                            if express_classes.exists():
                                for expr_class in express_classes:
                                    if expr_class.assigned_writer == writer:
                                        entity_choices.append(('express_class', expr_class.id))

                            if not entity_choices:
                                # Fall back to direct tip if no class entities
                                tip_type = 'direct'
                            else:
                                related_entity_type, related_entity_id = random.choice(entity_choices)
                                # Update writer to match entity's writer
                                if related_entity_type == 'class_bundle':
                                    bundle = ClassBundle.objects.get(id=related_entity_id)
                                    writer = bundle.assigned_writer
                                else:
                                    expr_class = ExpressClass.objects.get(id=related_entity_id)
                                    writer = expr_class.assigned_writer

                        # Create tip using TipService
                        tip = TipService.create_tip(
                            client=client,
                            writer=writer,
                            amount=tip_amount,
                            reason=tip_reason,
                            website=website,
                            order=order if tip_type == 'order' else None,
                            related_entity_type=related_entity_type if tip_type == 'class' else None,
                            related_entity_id=related_entity_id if tip_type == 'class' else None,
                            origin='client'
                        )

                        # Set payment status (mix of completed and pending)
                        tip.payment_status = random.choice(['completed', 'completed', 'completed', 'pending', 'processing'])
                        tip.sent_at = timezone.now() - timedelta(days=random.randint(1, 90))
                        tip.save()

                        tips_created += 1
                        if tip_type == 'direct':
                            total_direct_tips += 1
                        elif tip_type == 'order':
                            total_order_tips += 1
                        else:
                            total_class_tips += 1

                        entity_info = ""
                        if tip_type == 'order':
                            entity_info = f" | Order #{order.id}"
                        elif tip_type == 'class':
                            entity_info = f" | {related_entity_type} #{related_entity_id}"

                        self.stdout.write(
                            f'  ✓ Created {tip_type} tip #{tip.id} | '
                            f'{client.email} → {writer.email} | ${tip_amount} | '
                            f'Writer: ${tip.writer_earning} ({tip.writer_percentage}%){entity_info}'
                        )

                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ⚠ Failed to create tip: {str(e)}'
                            )
                        )
                        continue

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created:\n'
                    f'  - {total_direct_tips} direct tips\n'
                    f'  - {total_order_tips} order-based tips\n'
                    f'  - {total_class_tips} class-based tips\n'
                    f'  - Total: {total_direct_tips + total_order_tips + total_class_tips} tips'
                )
            )

