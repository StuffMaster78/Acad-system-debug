from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from websites.models import Website
from notifications_system.services.preferences import assign_default_preferences

User = get_user_model()

class Command(BaseCommand):
    help = "Seed notification preferences for all users"

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        success = 0
        for user in users:
            website = getattr(user, "website", None)
            if not website:
                self.stdout.write(self.style.WARNING(f"Skipping user {user} (no website)"))
                continue
            try:
                assign_default_preferences(user, website)
                success += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {user}: {e}"))
        self.stdout.write(self.style.SUCCESS(f"Seeded {success} users successfully"))