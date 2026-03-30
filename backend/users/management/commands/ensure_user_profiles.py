from __future__ import annotations

from django.core.management.base import BaseCommand

from users.models.profile import UserProfile
from users.models.user import User


class Command(BaseCommand):
    help = "Ensure all users have profiles."

    def handle(self, *args, **options):
        created = 0

        for user in User.objects.all().iterator():
            profile, was_created = UserProfile.objects.get_or_create(
                user=user
            )
            if was_created:
                created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Profiles ensured. Created: {created}"
            )
        )