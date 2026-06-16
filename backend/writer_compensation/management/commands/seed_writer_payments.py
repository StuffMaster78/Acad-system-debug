"""
Seed writer payout records — alias for seed_payment_management.

Delegates to seed_payment_management so both commands stay in sync.
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Seed writer payout records (alias for seed_payment_management)."

    def add_arguments(self, parser):
        parser.add_argument("--website-id", type=int)
        parser.add_argument("--clear", action="store_true")
        parser.add_argument("--count", type=int, default=10)

    def handle(self, *args, **options):
        call_command(
            "seed_payment_management",
            website_id=options.get("website_id"),
            clear=options.get("clear", False),
            count=options.get("count", 10),
        )
