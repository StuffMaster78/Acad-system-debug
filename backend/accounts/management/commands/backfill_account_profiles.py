from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import AccountProfile
from accounts.services.account_creation_service import (
    AccountCreationService,
)
from users.models import User
from websites.models.websites import Website


class Command(BaseCommand):
    """Backfill account profiles for existing users."""

    help = "Create missing account profiles for existing users."

    def add_arguments(self, parser):
        """Add optional command arguments."""
        parser.add_argument(
            "--website-id",
            type=int,
            help="Optional website ID to backfill for a single website.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        """Backfill missing account profiles."""
        website_id = options.get("website_id")

        websites = Website.objects.all()
        if website_id:
            websites = websites.filter(id=website_id)

        created_count = 0
        skipped_count = 0

        for website in websites:
            users = User.objects.all()

            for user in users:
                exists = AccountProfile.objects.filter(
                    website=website,
                    user=user,
                ).exists()

                if exists:
                    skipped_count += 1
                    continue

                AccountCreationService.create_account_profile(
                    website=website,
                    user=user,
                    actor=None,
                    is_primary=False,
                    metadata={"source": "backfill_account_profiles"},
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Backfill complete. "
                f"Created: {created_count}, Skipped: {skipped_count}"
            )
        )