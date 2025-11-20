from __future__ import annotations
import json
from pathlib import Path
from django.core.management.base import BaseCommand

from notifications_system.registry.compat import (
    normalize_broadcast, normalize_digest, normalize_notifications
)

class Command(BaseCommand):
    help = "Normalize event config JSON files (creates .bak backups)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--configs-dir", required=True,
            help="Dir with *_event_config.json files"
        )

    def handle(self, *args, **opts):
        d = Path(opts["configs_dir"])
        files = {
            "broadcast_event_config.json": normalize_broadcast,
            "digest_event_config.json": normalize_digest,
            "notification_event_config.json": normalize_notifications,
        }
        for fname, fn in files.items():
            path = d / fname
            if not path.exists():
                self.stdout.write(self.style.WARNING(f"Missing {path}"))
                continue
            try:
                original = json.loads(path.read_text())
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f"Invalid JSON {path}: {exc}"))
                continue
            normalized = fn(original)
            (d / (fname + ".bak")).write_text(json.dumps(original, indent=2))
            path.write_text(json.dumps(normalized, indent=2))
            self.stdout.write(self.style.SUCCESS(f"Fixed {fname}"))
