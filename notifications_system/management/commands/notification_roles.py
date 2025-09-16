from __future__ import annotations

import json
from typing import Dict, List

from django.core.management.base import BaseCommand, CommandError

from notifications_system.registry.role_registry import (
    autodiscover_roles,
    list_registered_roles,
)


class Command(BaseCommand):
    """List registered notification roles and their channel bindings.

    Usage:
      python manage.py notification_roles
      python manage.py notification_roles --json
      python manage.py notification_roles --keys-only
    """

    help = "Show notification roles, resolvers, and channel mappings."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--json",
            action="store_true",
            help="Dump roles as JSON.",
        )
        parser.add_argument(
            "--keys-only",
            action="store_true",
            help="Print only role names (one per line).",
        )

    def handle(self, *args, **opts) -> None:
        # Ensure roles are discovered even if AppConfig.ready() didn't run
        # (e.g., in weird CI shells or custom Django setups).
        try:
            autodiscover_roles()
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f"Autodiscover failed: {exc}") from exc

        data = list_registered_roles()
        if not data:
            self.stdout.write(self.style.WARNING("No roles registered."))
            return

        if opts["json"]:
            self.stdout.write(json.dumps(data, indent=2, default=str))
            return

        if opts["keys-only"]:
            for role in sorted(data.keys()):
                self.stdout.write(role)
            return

        # Pretty print a tiny table (no third-party deps).
        header = ["role", "resolver", "event_key", "channels"]
        rows: List[List[str]] = []
        for role in sorted(data.keys()):
            resolver = data[role]["resolver"]
            channels_map: Dict[str, List[str]] = data[role]["channels"]
            if not channels_map:
                rows.append([role, resolver, "-", "-"])
                continue
            for ev in sorted(channels_map.keys()):
                chans = ", ".join(channels_map[ev]) or "-"
                rows.append([role, resolver, ev, chans])

        widths = [len(h) for h in header]
        for row in rows:
            for i, col in enumerate(row):
                widths[i] = max(widths[i], len(col))

        def _line(c: str = "-") -> str:
            return "+".join(c * (w + 2) for w in widths)

        self.stdout.write(_line("-"))
        self.stdout.write(
            "| " + " | ".join(h.ljust(w) for h, w in zip(header, widths)) +
            " |"
        )
        self.stdout.write(_line("="))
        for row in rows:
            self.stdout.write(
                "| " + " | ".join(c.ljust(w) for c, w in zip(row, widths)) +
                " |"
            )
        self.stdout.write(_line("-"))
        self.stdout.write(
            self.style.SUCCESS(f"{len(rows)} row(s), {len(data)} role(s).")
        )