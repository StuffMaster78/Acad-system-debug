from django.core.management.base import BaseCommand

from accounts.enums import ReservedRoleKey
from accounts.models import RoleDefinition
from websites.models.websites import Website


class Command(BaseCommand):
    """Seed default role definitions for all websites."""

    help = "Seed default role definitions for all websites."

    def handle(self, *args, **options):
        """Create reserved role definitions for each website."""
        reserved_roles = [
            (
                ReservedRoleKey.SUPER_ADMIN,
                "Super Admin",
                "Full platform control for a website.",
            ),
            (
                ReservedRoleKey.ADMIN,
                "Admin",
                "Administrative access for operations and setup.",
            ),
            (
                ReservedRoleKey.EDITOR,
                "Editor",
                "Editorial and review responsibilities.",
            ),
            (
                ReservedRoleKey.SUPPORT,
                "Support",
                "Support and communication responsibilities.",
            ),
            (
                ReservedRoleKey.WRITER,
                "Writer",
                "Writer account with work delivery responsibilities.",
            ),
            (
                ReservedRoleKey.CLIENT,
                "Client",
                "Client account for placing and paying for services.",
            ),
        ]

        created_count = 0

        for website in Website.objects.all():
            for role_key, role_name, description in reserved_roles:
                _, created = RoleDefinition.objects.get_or_create(
                    website=website,
                    key=role_key,
                    defaults={
                        "name": role_name,
                        "description": description,
                        "is_system_role": True,
                        "is_active": True,
                    },
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded role definitions. Created {created_count} rows."
            )
        )