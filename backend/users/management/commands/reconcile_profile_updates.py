from __future__ import annotations

from django.core.management.base import BaseCommand

from users.models.profile import (
    ProfileUpdateRequest,
    ProfileUpdateRequestStatus,
)
from users.services.profile_update_service import (
    ProfileUpdateService,
)


class Command(BaseCommand):
    help = "Apply approved profile update requests that were not applied."

    def handle(self, *args, **options):
        qs = ProfileUpdateRequest.objects.filter(
            status=ProfileUpdateRequestStatus.APPROVED
        )

        applied = 0

        for request_obj in qs.iterator():
            try:
                ProfileUpdateService.apply_approved_request(
                    request_obj=request_obj
                )
                applied += 1
            except Exception as exc:
                self.stderr.write(
                    f"Failed to apply request {request_obj.pk}: {exc}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Reconciliation complete. Applied: {applied}"
            )
        )