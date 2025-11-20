# notifications_system/registry/loader.py
from __future__ import annotations
import json
import logging
import os
from pathlib import Path
from django.db import transaction
from django.conf import settings

from notifications_system.models.event_config import NotificationEvent
from notifications_system.models.notifications_template import NotificationTemplate
from notifications_system.registry.compat import (
    normalize_broadcast, normalize_digest, normalize_notifications
)

log = logging.getLogger(__name__)

CONFIG_DIR = Path(
    os.getenv("NOTIF_CONFIG_DIR",
              "/app/notifications_system/registry/configs")
)

def _read_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception as exc:
        log.warning("Invalid JSON at %s: %s", path, exc)
        return None

def load_effective_events() -> list[dict]:
    """Return normalized notification events (DB-first, files fallback)."""
    if settings.NOTIFICATIONS_SOURCE in ("db_first", "db_only"):
        if NotificationEvent.objects.exists():
            return [
                dict(
                    key=e.key, label=e.label, priority=e.priority,
                    enabled=e.enabled, scope=e.scope, description=e.description,
                    schema_version=e.schema_version,
                )
                for e in NotificationEvent.objects.all()
            ]
        if settings.NOTIFICATIONS_SOURCE == "db_only":
            return []

    p = CONFIG_DIR / "notification_event_config.json"
    raw = _read_json(p) or []
    norm = normalize_notifications(raw)

    # Optional: seed DB if empty
    if settings.NOTIFICATIONS_SOURCE in ("db_first",) and norm:
        _seed_events_into_db(norm)

    return norm

def _seed_events_into_db(items: list[dict]) -> None:
    try:
        with transaction.atomic():
            for it in items:
                NotificationEvent.objects.update_or_create(
                    key=it["key"],
                    defaults=dict(
                        label=it.get("label") or it["key"].title(),
                        description=it.get("description", ""),
                        scope=it.get("scope", "user"),
                        priority=it.get("priority", "medium"),
                        enabled=bool(it.get("enabled", True)),
                        schema_version=it.get("schema_version", 1),
                        metadata=it.get("metadata", {}),
                    ),
                )
    except Exception as exc:
        log.warning("Seeding events failed (non-fatal): %s", exc)

def load_templates_for(event_key: str) -> list[dict]:
    """Return templates for an event (DB-first, files fallback)."""
    data = []
    if settings.NOTIFICATIONS_SOURCE in ("db_first", "db_only"):
        ev = NotificationEvent.objects.filter(key=event_key).first()
        if ev:
            for t in ev.templates.all():
                data.append(dict(
                    channel=t.channel, locale=t.locale, version=t.version,
                    subject=t.subject, body_html=t.body_html,
                    body_text=t.body_text, website_id=t.website_id,
                    provider_overrides=t.provider_overrides,
                ))
            if data or settings.NOTIFICATIONS_SOURCE == "db_only":
                return data

    # Fallback: optional per-event template files, or a single templates.json
    # (Implement to match your current file layout if you have one.)
    return data

def load_broadcast_defs() -> list[dict]:
    p = CONFIG_DIR / "broadcast_event_config.json"
    raw = _read_json(p) or []
    return normalize_broadcast(raw)

def load_digest_defs() -> list[dict]:
    p = CONFIG_DIR / "digest_event_config.json"
    raw = _read_json(p) or []
    return normalize_digest(raw)