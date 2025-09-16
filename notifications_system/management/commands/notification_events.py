from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

from django.core.management.base import BaseCommand, CommandError

from notifications_system.registry.notification_event_loader import (
    NotificationEventRegistry as NER,
)


def _fmt_list(items: Iterable[str]) -> str:
    """Return a short printable comma list."""
    xs = list(items)
    return ", ".join(xs) if xs else "-"


class Command(BaseCommand):
    """Inspect and validate notification event configs.

    Usage:
      python manage.py notification_events
      python manage.py notification_events --validate
      python manage.py notification_events --dump-json
      python manage.py notification_events --keys-only

    Flags:
      --validate   Validate JSON against schema (if available).
      --dump-json  Print raw loaded JSON.
      --keys-only  Print only event keys (one per line).
    """

    help = "List/validate configured notification events."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate JSON against schema (if available).",
        )
        parser.add_argument(
            "--dump-json",
            action="store_true",
            help="Dump loaded JSON for notification events.",
        )
        parser.add_argument(
            "--keys-only",
            action="store_true",
            help="Print only event keys (one per line).",
        )

    def handle(self, *args, **opts) -> None:
        try:
            count = NER.load()
        except Exception as exc:
            raise CommandError(f"Load failed: {exc}") from exc

        if opts["validate"]:
            try:
                NER.load()
                self.stdout.write(self.style.SUCCESS("Validation OK."))
            except Exception as exc:
                raise CommandError(f"Validation failed: {exc}") from exc

        if opts["dump-json"]:
            data = NER.all()
            items: List[Dict[str, Any]] = [
                data[k] for k in sorted(data.keys())
            ]
            self.stdout.write(json.dumps(items, indent=2, default=str))
            return

        if opts["keys-only"]:
            for key in sorted(NER.all().keys()):
                self.stdout.write(key)
            return

        # Pretty print a tiny table
        data = NER.all()
        if not data:
            self.stdout.write(self.style.WARNING("No notification events."))
            return

        header = [
            "event_key",
            "category",
            "priority",
            "forced",
            "defaults",
        ]
        rows: List[List[str]] = []
        for key in sorted(data.keys()):
            ev = data[key]
            rows.append([
                key,
                str(ev.get("category", "")),
                str(ev.get("priority", "")),
                _fmt_list(ev.get("forced_channels", [])),
                _fmt_list(ev.get("default_channels", [])),
            ])

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
            self.style.SUCCESS(f"{len(rows)} notification event(s) loaded.")
        )