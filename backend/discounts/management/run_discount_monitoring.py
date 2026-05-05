from __future__ import annotations

from django.core.management.base import BaseCommand

from discounts.services.discount_monitoring_service import (
    DiscountMonitoringService,
)


class Command(BaseCommand):
    """
    Run discount monitoring notification workflows.
    """

    help = "Notify admins about expiring discounts and usage limits."

    def add_arguments(self, parser) -> None:
        """
        Add command arguments.
        """
        parser.add_argument(
            "--days",
            type=int,
            default=3,
            help="Days before expiry to notify admins.",
        )

    def handle(self, *args, **options) -> None:
        """
        Execute monitoring workflows.
        """
        days = options["days"]

        expiring_result = (
            DiscountMonitoringService.notify_expiring_discounts(
                days=days,
            )
        )
        limit_result = (
            DiscountMonitoringService.notify_usage_limit_reached()
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Discount monitoring completed: "
                f"expiring={expiring_result}, "
                f"limits={limit_result}"
            )
        )