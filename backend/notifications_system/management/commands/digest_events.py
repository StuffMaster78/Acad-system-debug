from __future__ import annotations

import json
from typing import Dict, List, Tuple

from django.core.management.base import BaseCommand, CommandError

from notifications_system.registry.digest_event_loader import (
    autoload_digest_events,
)
from notifications_system.registry.main_registry import (
    DIGEST_EVENT_REGISTRY,
)
from notifications_system.registry.digest_events import (
    validate_digest_config,
)


class Command(BaseCommand):
    """Inspect and validate digest event configs.

    Usage:
      python manage.py digest_events
      python manage.py digest_events --json
      python manage.py digest_events --validate
      python manage.py digest_events --keys-only
    """

    help = "List/validate digest event configs."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--json",
            action="store_true",
            help="Dump registry as JSON.",
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate digest registry and exit non-zero on error.",
        )
        parser.add_argument(
            "--keys-only",
            action="store_true",
            help="Print only event keys (one per line).",
        )

    def handle(self, *args, **opts) -> None:
        # Ensure latest configs are loaded.
        try:
            autoload_digest_events()
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f"Digest autoload failed: {exc}") from exc

        if opts["validate"]:
            errors = validate_digest_config()
            if errors:
                for key, msg in errors:
                    self.stderr.write(f"[ERR] {key}: {msg}")
                raise CommandError(
                    f"{len(errors)} validation error(s) found."
                )
            self.stdout.write(self.style.SUCCESS("OK"))
            return

        if opts["keys-only"]:
            for k in sorted(DIGEST_EVENT_REGISTRY.keys()):
                self.stdout.write(k)
            return

        if opts["json"]:
            self.stdout.write(
                json.dumps(DIGEST_EVENT_REGISTRY, indent=2, default=str)
            )
            return

        # Human-readable table view
        self._print_table(DIGEST_EVENT_REGISTRY)

    # ------------------------
    # Helpers
    # ------------------------

    def _print_table(self, reg: Dict[str, Dict]) -> None:
        """Pretty-print a small table without third-party deps."""
        if not reg:
            self.stdout.write("No digest events registered.")
            return

        rows: List[List[str]] = [["event_key", "delay", "group_by", "src"]]
        for ek in sorted(reg.keys()):
            cfg = reg[ek]
            delay = str(cfg.get("delay_minutes", ""))
            gb = str(cfg.get("group_by", ""))
            src = str(cfg.get("__source__", ""))
            rows.append([ek, delay, gb, src])

        widths = [0] * len(rows[0])
        for row in rows:
            for i, col in enumerate(row):
                widths[i] = max(widths[i], len(col))

        def line(ch: str = "-") -> str:
            return "+".join(ch * (w + 2) for w in widths)

        self.stdout.write(line("-"))
        self.stdout.write(
            "| " + " | ".join(
                rows[0][i].ljust(widths[i]) for i in range(len(widths))
            ) + " |"
        )
        self.stdout.write(line("="))
        for row in rows[1:]:
            self.stdout.write(
                "| " + " | ".join(
                    row[i].ljust(widths[i]) for i in range(len(widths))
                ) + " |"
            )
        self.stdout.write(line("-"))
        self.stdout.write(
            self.style.SUCCESS(f"{len(rows) - 1} event(s).")
        )