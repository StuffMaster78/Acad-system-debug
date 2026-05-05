from __future__ import annotations

from django.core.management.base import BaseCommand

from discounts.services.campaign_scheduler_service import (
    CampaignSchedulerService,
)


class Command(BaseCommand):
    """
    Run scheduled campaign activation and expiry.
    """

    help = "Activate due campaigns and deactivate expired campaigns."

    def handle(self, *args, **options) -> None:
        """
        Execute campaign scheduler.
        """
        result = CampaignSchedulerService.run()

        self.stdout.write(
            self.style.SUCCESS(
                "Discount campaign scheduler completed: "
                f"{result}"
            )
        )