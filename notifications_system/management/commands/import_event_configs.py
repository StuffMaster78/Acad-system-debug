# notifications_system/management/commands/import_event_configs.py
from __future__ import annotations
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from notifications_system.models import NotificationEvent, NotificationTemplate
from typing import Iterable, Optional
from notifications_system.services.dispatcher import resolve_template


class Command(BaseCommand):
    help = "Import JSON configs into DB (one-off or repeatable)."

    def add_arguments(self, parser):
        parser.add_argument("--events", required=True,
                            help="Path to notification_event_config.json")
        parser.add_argument("--templates", required=False,
                            help="Optional path to templates json")

    def handle(self, *args, **opts):
        events_path = Path(opts["events"])
        data = json.loads(events_path.read_text())

        # Support both dict mapping and array-of-objects
        if isinstance(data, dict):
            items = []
            for k, v in data.items():
                v = dict(v)
                v.setdefault("key", k)
                v.setdefault("event_key", v["key"])
                v.setdefault("label", k.replace(".", " ").title())
                v.setdefault("priority", "medium")
                v.setdefault("enabled", True)
                items.append(v)
        else:
            items = data

        for it in items:
            NotificationEvent.objects.update_or_create(
                key=it["key"],
                defaults=dict(
                    label=it.get("label"),
                    description=it.get("description", ""),
                    scope=it.get("scope", "user"),
                    priority=it.get("priority", "medium"),
                    enabled=bool(it.get("enabled", True)),
                    schema_version=it.get("schema_version", 1),
                    metadata=it.get("metadata", {}),
                ),
            )
        self.stdout.write(self.style.SUCCESS(f"Upserted {len(items)} events"))

        tfile = opts.get("templates")
        if not tfile:
            return

        tdata = json.loads(Path(tfile).read_text())
        if isinstance(tdata, dict):
            titems = []
            for k, v in tdata.items():
                v = dict(v)
                v.setdefault("event_key", k)
                titems.append(v)
        else:
            titems = tdata

        count = 0
        for it in titems:
            ev = NotificationEvent.objects.get(key=it["event_key"])
            NotificationTemplate.objects.update_or_create(
                event=ev,
                website_id=it.get("website_id"),
                channel=it["channel"],
                locale=it.get("locale", "en"),
                version=it.get("version", 1),
                defaults=dict(
                    subject=it.get("subject", ""),
                    body_html=it.get("body_html", ""),
                    body_text=it.get("body_text", ""),
                    provider_overrides=it.get("provider_overrides", {}),
                ),
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Upserted {count} templates"))


def prewarm_templates(event_keys: Iterable[str], channels: Iterable[str],
                      website_ids: Iterable[Optional[int]],
                      locales: Iterable[str] = ("en",)) -> None:
    for ek in event_keys:
        for ch in channels:
            for wid in website_ids:
                for loc in locales:
                    resolve_template(ek, ch, wid, loc, use_cache=True)