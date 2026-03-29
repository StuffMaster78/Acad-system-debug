from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.enums import ReservedRoleKey
from accounts.models import AccountProfile, RoleDefinition
from accounts.services.account_role_service import AccountRoleService


class Command(BaseCommand):
    """Backfill account roles for existing account profiles."""

    help = "Assign default roles to existing account profiles."

    @transaction.atomic
    def handle(self, *args, **options):
        """Backfill roles for account profiles."""
        assigned_count = 0
        skipped_count = 0

        profiles = AccountProfile.objects.select_related(
            "website",
            "user",
        )

        for profile in profiles:
            role_keys = self._infer_role_keys(profile)

            for role_key in role_keys:
                role = RoleDefinition.objects.filter(
                    website=profile.website,
                    key=role_key,
                    is_active=True,
                ).first()

                if role is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Missing role '{role_key}' for website "
                            f"{profile.website_id}"
                        )
                    )
                    continue

                try:
                    AccountRoleService.assign_role(
                        account_profile=profile,
                        role=role,
                        actor=None,
                        metadata={"source": "backfill_account_roles"},
                    )
                    assigned_count += 1
                except Exception:
                    skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Role backfill complete. "
                f"Assigned: {assigned_count}, Skipped: {skipped_count}"
            )
        )

    def _infer_role_keys(self, profile) -> list[str]:
        """Infer role keys from legacy user flags or app state."""
        user = profile.user
        role_keys: list[str] = []

        if getattr(user, "is_superuser", False):
            role_keys.append(ReservedRoleKey.SUPER_ADMIN)

        if getattr(user, "is_staff", False):
            role_keys.append(ReservedRoleKey.ADMIN)

        if not role_keys:
            role_keys.append(ReservedRoleKey.CLIENT)

        return role_keys