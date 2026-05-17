from __future__ import annotations

from typing import Any

from django.core.management.base import BaseCommand

from writer_compensation.enums.compensation_enums import WindowStatus
from writer_compensation.models.payment_window import PaymentWindow
from writer_compensation.tasks.windows_tasks import (
    check_and_close_windows,
    check_and_open_windows,
)


class Command(BaseCommand):
    """
    Manual override command for admins to control payment windows
    outside the automated scheduling system.

    Use cases:
        - Emergency close of active windows
        - Force opening of pending windows
        - Inspect current window state across sites

    Usage:
        python manage.py manage_windows --action=close
        python manage.py manage_windows --action=open --site=1
        python manage.py manage_windows --action=status
    """

    help = "Manually manage payment windows (open, close, status)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--action",
            choices=["close", "open", "status"],
            required=True,
            help=(
                "close: close active windows | "
                "open: open eligible windows | "
                "status: display window state"
            ),
        )

        parser.add_argument(
            "--site",
            type=int,
            default=None,
            help="Optional website ID filter for status view.",
        )

    def handle(self, *args: Any, **options: Any):
        action: str = options["action"]
        site_id: int | None = options["site"]

        if action == "status":
            self._show_status(site_id)
            return

        if action == "close":
            self.stdout.write("Running window close task...")

            result = check_and_close_windows.delay()  # type: ignore[attr-defined]

            self.stdout.write(
                self.style.SUCCESS(f"Done: {result}")
            )
            return

        if action == "open":
            self.stdout.write("Running window open task...")

            result = check_and_open_windows.delay()  # type: ignore[attr-defined]

            self.stdout.write(
                self.style.SUCCESS(f"Done: {result}")
            )
            return

    def _show_status(self, site_id: int | None = None):
        """
        Display current payment window state across websites.

        Shows:
            - Window status (OPEN, CLOSED, PROCESSING, DONE)
            - Date range
            - Window ID
        """

        qs = (
            PaymentWindow.objects.select_related("website")
            .order_by("website_id", "-start_date")
        )

        if site_id:
            qs = qs.filter(website_id=site_id)

        current_site: int | None = None

        status_style_map: dict[WindowStatus, Any] = {
            WindowStatus.OPEN: self.style.SUCCESS,
            WindowStatus.CLOSED: self.style.WARNING,
            WindowStatus.PROCESSING: self.style.NOTICE,
            WindowStatus.DONE: self.style.HTTP_INFO,
        }

        for window in qs[:50]:
            if window.website.pk != current_site:
                current_site = window.website.pk
                self.stdout.write(f"\nSite {current_site}:")

            status_enum = WindowStatus(window.status)

            style = status_style_map.get(
                status_enum,
                self.style.SUCCESS,
            )

            self.stdout.write(
                f"  [{style(window.status)}] "
                f"{window.start_date} → {window.end_date} "
                f"(id: {window.pk})"
            )