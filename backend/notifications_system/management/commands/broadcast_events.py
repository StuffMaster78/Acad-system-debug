from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List

from django.core.management.base import BaseCommand, CommandError

from notifications_system.registry.broadcast_event_loader import (
    BroadcastEventRegistry as BER,
)


def _fmt_list(items: Iterable[str]) -> str:
    """Return a short printable comma list."""
    xs = list(items)
    return ", ".join(xs) if xs else "-"


class Command(BaseCommand):
    """Inspect and validate broadcast event configs.

    Usage:
      python manage.py broadcast_events
      python manage.py broadcast_events --validate
      python manage.py broadcast_events --dump-json
      python manage.py broadcast_events --keys-only

    Flags:
      --validate   Validate JSON against schema (if jsonschema present).
      --dump-json  Print raw loaded JSON.
      --keys-only  Print only event keys (one per line).
    """

    help = "List/validate configured broadcast events."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate JSON against schema (if available).",
        )
        parser.add_argument(
            "--dump-json",
            action="store_true",
            help="Dump loaded JSON for broadcasts.",
        )
        parser.add_argument(
            "--keys-only",
            action="store_true",
            help="Print only event keys (one per line).",
        )

    def handle(self, *args, **opts) -> None:
        try:
            count = BER.load()
        except Exception as exc:
            raise CommandError(f"Load failed: {exc}") from exc

        if opts["validate"]:
            # load() already validates if jsonschema is installed; do it
            # again to show explicit success messaging.
            try:
                BER.load()
                self.stdout.write(self.style.SUCCESS("Validation OK."))
            except Exception as exc:
                raise CommandError(f"Validation failed: {exc}") from exc

        if opts["dump-json"]:
            data = BER.all()
            # BER.all() is dict keyed by event_key; convert to list for
            # a stable json dump (sorted by key).
            items: List[Dict[str, Any]] = [
                data[k] for k in sorted(data.keys())
            ]
            self.stdout.write(json.dumps(items, indent=2, default=str))
            return

        if opts["keys-only"]:
            for key in sorted(BER.all().keys()):
                self.stdout.write(key)
            return

        # Pretty print a tiny table, no third-party libs.
        data = BER.all()
        if not data:
            self.stdout.write(self.style.WARNING("No broadcast events."))
            return

        header = [
            "event_key",
            "scope",
            "priority",
            "forced",
            "defaults",
            "filters",
        ]
        rows: List[List[str]] = []
        for key in sorted(data.keys()):
            ev = data[key]
            rows.append([
                key,
                str(ev.get("scope", "systemwide")),
                str(ev.get("priority", "normal")),
                _fmt_list(ev.get("forced_channels", [])),
                _fmt_list(ev.get("default_channels", [])),
                json.dumps(ev.get("filters", {}), separators=(",", ":")),
            ])

        # compute simple widths
        widths = [len(h) for h in header]
        for row in rows:
            for i, col in enumerate(row):
                widths[i] = max(widths[i], len(col))

        def _line(c: str = "-") -> str:
            return "+".join(c * (w + 2) for w in widths)

        # header
        self.stdout.write(_line("-"))
        self.stdout.write(
            "| " + " | ".join(h.ljust(w) for h, w in zip(header, widths)) + " |"
        )
        self.stdout.write(_line("="))
        # body
        for row in rows:
            self.stdout.write(
                "| " + " | ".join(c.ljust(w) for c, w in zip(row, widths)) + " |"
            )
        self.stdout.write(_line("-"))

        self.stdout.write(
            self.style.SUCCESS(f"{len(rows)} broadcast event(s) loaded.")
        )