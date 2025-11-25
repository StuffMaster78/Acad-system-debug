"""
Management command to seed reviews with sample data.
Creates website reviews, writer reviews, and order reviews.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from websites.models import Website
from reviews_system.models.website_review import WebsiteReview
from reviews_system.models.writer_review import WriterReview
from reviews_system.models.order_review import OrderReview
from orders.models import Order
from users.models import User
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed reviews with sample data (website, writer, and order reviews)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--website-id',
            type=int,
            help='Specific website ID to seed (if not provided, seeds all websites)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing reviews before seeding',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Number of reviews to create per type per website (default: 20)',
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
                self.stdout.write('Clearing existing reviews...')
                OrderReview.objects.all().delete()
                WriterReview.objects.all().delete()
                WebsiteReview.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS('Cleared existing data')
                )

            # Get clients and writers
            clients = list(User.objects.filter(role='client', is_active=True)[:20])
            writers = list(User.objects.filter(role='writer', is_active=True)[:10])

            if not clients:
                self.stdout.write(
                    self.style.WARNING('No active clients found. Skipping review creation.')
                )
                return

            # Sample review comments
            positive_comments = [
                "Excellent service! Very satisfied with the quality and timeliness.",
                "Great work, exceeded my expectations. Highly recommend!",
                "Professional and reliable. Will definitely use again.",
                "Outstanding quality and attention to detail. Very pleased.",
                "Fast delivery and excellent communication throughout.",
                "Top-notch service! The writer understood exactly what I needed.",
                "Very professional and delivered exactly as promised.",
                "Excellent quality work. Met all requirements perfectly.",
                "Great experience overall. Would definitely recommend.",
                "High-quality work delivered on time. Very satisfied!",
            ]

            neutral_comments = [
                "Good service overall. Met the basic requirements.",
                "Decent work, but could use some improvements.",
                "Satisfactory service. Nothing exceptional but acceptable.",
                "Average quality. Got the job done.",
                "It was okay. Met expectations but nothing more.",
            ]

            negative_comments = [
                "Not quite what I expected. Some issues with quality.",
                "Had to request revisions. Could have been better.",
                "Service was acceptable but not great.",
                "Some delays and quality concerns.",
                "Could improve communication and delivery time.",
            ]

            total_website_reviews = 0
            total_writer_reviews = 0
            total_order_reviews = 0

            for website in websites:
                self.stdout.write(f'\nProcessing website: {website.name} (ID: {website.id})')

                # Create Website Reviews
                self.stdout.write('  Creating website reviews...')
                website_clients = random.sample(clients, min(count, len(clients)))
                for client in website_clients:
                    # Check if review already exists (unique constraint)
                    if WebsiteReview.objects.filter(reviewer=client, website=website).exists():
                        continue

                    # Rating distribution: mostly positive (4-5 stars), some neutral (3), few negative (1-2)
                    rand = random.random()
                    if rand < 0.70:  # 70% positive
                        rating = random.choice([4, 5])
                        comment = random.choice(positive_comments)
                    elif rand < 0.90:  # 20% neutral
                        rating = 3
                        comment = random.choice(neutral_comments)
                    else:  # 10% negative
                        rating = random.choice([1, 2])
                        comment = random.choice(negative_comments)

                    review = WebsiteReview.objects.create(
                        reviewer=client,
                        website=website,
                        rating=rating,
                        comment=comment,
                        origin='client',
                        is_approved=random.choice([True, True, True, False]),  # 75% approved
                        is_shadowed=random.choice([False, False, False, True]),  # 25% shadowed
                        submitted_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                    )

                    total_website_reviews += 1
                    self.stdout.write(
                        f'    ✓ Created website review #{review.id} | {client.email} | {rating} stars'
                    )

                # Create Writer Reviews
                if writers:
                    self.stdout.write('  Creating writer reviews...')
                    for i in range(min(count, len(writers) * 3)):  # Multiple reviews per writer possible
                        writer = random.choice(writers)
                        client = random.choice(clients)

                        # Rating distribution
                        rand = random.random()
                        if rand < 0.75:  # 75% positive
                            rating = random.choice([4, 5])
                            comment = random.choice(positive_comments)
                        elif rand < 0.90:  # 15% neutral
                            rating = 3
                            comment = random.choice(neutral_comments)
                        else:  # 10% negative
                            rating = random.choice([1, 2])
                            comment = random.choice(negative_comments)

                        review = WriterReview.objects.create(
                            reviewer=client,
                            writer=writer,
                            website=website,
                            rating=rating,
                            comment=comment,
                            origin='client',
                            is_approved=random.choice([True, True, True, False]),  # 75% approved
                            is_shadowed=random.choice([False, False, False, True]),  # 25% shadowed
                            submitted_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                        )

                        total_writer_reviews += 1
                        self.stdout.write(
                            f'    ✓ Created writer review #{review.id} | {client.email} → {writer.email} | {rating} stars'
                        )

                # Create Order Reviews
                self.stdout.write('  Creating order reviews...')
                # Get completed orders for this website
                completed_orders = Order.objects.filter(
                    website=website,
                    status='completed',
                    is_paid=True,
                    assigned_writer__isnull=False
                )[:count * 2]  # Get more orders than needed

                if not completed_orders.exists():
                    self.stdout.write(
                        f'    ⚠ No completed orders found for {website.name}. Skipping order reviews.'
                    )
                    continue

                reviewed_orders = set()
                for order in completed_orders:
                    # Check unique constraint (one review per reviewer per order)
                    if order.client in reviewed_orders:
                        continue
                    if OrderReview.objects.filter(reviewer=order.client, order=order).exists():
                        continue

                    # Rating distribution
                    rand = random.random()
                    if rand < 0.70:  # 70% positive
                        rating = random.choice([4, 5])
                        comment = random.choice(positive_comments)
                    elif rand < 0.85:  # 15% neutral
                        rating = 3
                        comment = random.choice(neutral_comments)
                    else:  # 15% negative
                        rating = random.choice([1, 2])
                        comment = random.choice(negative_comments)

                    review = OrderReview.objects.create(
                        reviewer=order.client,
                        order=order,
                        writer=order.assigned_writer,
                        website=website,
                        rating=rating,
                        comment=comment,
                        origin='client',
                        is_approved=random.choice([True, True, True, False]),  # 75% approved
                        is_shadowed=random.choice([False, False, False, True]),  # 25% shadowed
                        submitted_at=timezone.now() - timedelta(days=random.randint(1, 90)),
                    )

                    reviewed_orders.add(order.client)
                    total_order_reviews += 1
                    self.stdout.write(
                        f'    ✓ Created order review #{review.id} | Order #{order.id} | {rating} stars'
                    )

                    if total_order_reviews >= count:
                        break

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully created:\n'
                    f'  - {total_website_reviews} website reviews\n'
                    f'  - {total_writer_reviews} writer reviews\n'
                    f'  - {total_order_reviews} order reviews'
                )
            )

