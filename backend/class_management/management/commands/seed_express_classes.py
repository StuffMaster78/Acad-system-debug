"""
Seed demo class orders (express/online class orders) for each active website.

Creates ClassOrder records with various statuses to populate the admin class
management view with realistic demo data.

Safe to re-run — skips websites that already have class orders.
"""
from datetime import timedelta
from decimal import Decimal
import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from class_management.constants import ClassOrderStatus
from class_management.models import ClassOrder
from websites.models.websites import Website


SUBJECTS = [
    "Introduction to Nursing", "Calculus I", "Business Ethics",
    "Introduction to Psychology", "Data Structures", "Thermodynamics",
    "Cell Biology", "Organic Chemistry", "Shakespeare Studies",
    "World History", "Microeconomics", "Social Theory",
]

INSTITUTIONS = [
    "State University", "City College", "Online Academy",
    "Community College", "Tech Institute", "Liberal Arts College",
]

ACADEMIC_LEVELS = ["Undergraduate", "Graduate", "Doctoral"]

STATUS_DISTRIBUTION = [
    (ClassOrderStatus.SUBMITTED, 0.20),
    (ClassOrderStatus.UNDER_REVIEW, 0.15),
    (ClassOrderStatus.PRICE_PROPOSED, 0.15),
    (ClassOrderStatus.ASSIGNED, 0.20),
    (ClassOrderStatus.IN_PROGRESS, 0.25),
    (ClassOrderStatus.COMPLETED, 0.05),
]


class Command(BaseCommand):
    help = "Seed demo ClassOrder records per active website."

    def add_arguments(self, parser):
        parser.add_argument("--website-id", type=int)
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--count", type=int, default=5, help="Orders per website (default: 5)")

    def handle(self, *args, **options):
        website_id = options.get("website_id")
        clear = options.get("clear", False)
        count = options.get("count", 5)

        websites = (
            Website.objects.filter(id=website_id) if website_id
            else Website.objects.filter(is_active=True)
        )

        from django.contrib.auth import get_user_model
        User = get_user_model()

        clients = list(User.objects.filter(role="client", is_active=True)[:20])
        if not clients:
            self.stdout.write(self.style.WARNING("No client users found — run seed_dev_data first."))
            return

        total_created = 0

        for website in websites:
            if clear:
                ClassOrder.objects.filter(website=website).delete()

            if ClassOrder.objects.filter(website=website).exists():
                self.stdout.write(f"  {website.name}: already has class orders — skipping")
                continue

            for _ in range(count):
                client = random.choice(clients)
                subject = random.choice(SUBJECTS)
                institution = random.choice(INSTITUTIONS)
                level = random.choice(ACADEMIC_LEVELS)

                # Pick status from distribution
                rand = random.random()
                cumulative = 0.0
                status = ClassOrderStatus.SUBMITTED
                for stat, prob in STATUS_DISTRIBUTION:
                    cumulative += prob
                    if rand <= cumulative:
                        status = stat
                        break

                today = timezone.now().date()
                starts_on = today + timedelta(days=random.randint(-30, 30))
                ends_on = starts_on + timedelta(days=random.randint(45, 120))

                base_price = {"Undergraduate": "450.00", "Graduate": "700.00", "Doctoral": "950.00"}[level]
                quoted = Decimal(base_price) + Decimal(str(random.randint(0, 200)))

                order = ClassOrder.objects.create(
                    website=website,
                    client=client,
                    title=f"{subject} — {institution}",
                    institution_name=institution,
                    class_name=subject,
                    class_subject=subject,
                    academic_level=level,
                    starts_on=starts_on,
                    ends_on=ends_on,
                    status=status,
                    quoted_amount=quoted,
                    currency="USD",
                    initial_client_notes=f"Demo class order for {subject}. Standard instructions apply.",
                )
                total_created += 1
                self.stdout.write(f"  {website.name}: #{order.id} {status} — {subject}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. Created {total_created} class orders."))
