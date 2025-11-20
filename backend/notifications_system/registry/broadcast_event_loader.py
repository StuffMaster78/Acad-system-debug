# notifications_system/registry/broadcast_event_loader.py
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .compat import normalize_broadcast
from .validator import validate_config_file  # use schema by base name (no .json)

logger = logging.getLogger(__name__)


# ---------- helpers ----------

def _pkg_path(*parts: str) -> Path:
    """Return a path relative to this module file."""
    return Path(__file__).parent.joinpath(*parts).resolve()


def _read_json(path: Path) -> Any:
    """Read JSON from path with a useful error on failure."""
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed reading JSON: {path}: {exc}") from exc


def _map_to_list(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    {"broadcast.system_announcement": {...}}  -->
    [{"event_key": "broadcast.system_announcement", ...}]
    """
    return [{**v, "event_key": k} for k, v in d.items()]


# ---------- loader that accepts list or mapping ----------

def _load_and_normalize(path: Path) -> List[Dict[str, Any]]:
    """
    Load JSON (list or mapping), normalize shapes/legacy keys, and return a list of event dicts.
    """
    raw = _read_json(path)

    # First, validate the *file* against the broadcast schema.
    # IMPORTANT: schema_name has no ".json" suffix.
    res = validate_config_file(path, schema_name="broadcast_event.schema")
    res.raise_if_failed()

    # Accept either list or mapping; normalize to list.
    if isinstance(raw, dict):
        items = _map_to_list(raw)
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError(
            "broadcast_event_config.json must be either a list of objects or a mapping "
            "{event_key: { ... }}."
        )

    # Apply tolerant normalizer (handles default_channels -> channels, etc.)
    try:
        items = normalize_broadcast(items)  # idempotent if already normalized
    except Exception:
        # Be forgiving; continue with items as-is.
        pass

    # Final sanity
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"broadcast_event_config item #{idx} is not an object")
        if not it.get("event_key"):
            raise ValueError(f"broadcast_event_config item #{idx} missing 'event_key'")

    return items


# ---------- in-process registry (keyed by event_key) ----------

class BroadcastEventRegistry:
    """
    In-process registry for broadcast event metadata.

    Source file:
        notifications_system/registry/configs/broadcast_event_config.json

    Schema:
        notifications_system/registry/configs/schemas/broadcast_event.schema.json

    Stored per event (keyed by `event_key`):
        {
          "event_key": str,
          "description": str,
          "scope": "systemwide" | "website",
          "channels": [str, ...],          # normalized from channels/default_channels
          "forced_channels": [str, ...],
          "priority": str | int,
          "force_send": bool,
          "filters": { ... }
        }
    """

    _loaded: bool = False
    _events: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def load(cls, *, path: Optional[Path] = None) -> int:
        """
        Load and validate broadcast event configs into the registry.

        Returns:
            Number of events loaded.
        """
        cfg_path = path or _pkg_path("configs", "broadcast_event_config.json")

        items = _load_and_normalize(cfg_path)

        events_by_key: Dict[str, Dict[str, Any]] = {}

        for item in items:
            key = str(item["event_key"])

            # Normalize channels: accept either "channels" or "default_channels"
            channels = item.get("channels")
            if not isinstance(channels, list):
                channels = item.get("default_channels", [])
            channels = list(channels or [])

            events_by_key[key] = {
                "event_key": key,
                "description": item.get("description", ""),
                "scope": item.get("scope", "systemwide"),
                "channels": channels,
                "forced_channels": list(item.get("forced_channels", []) or []),
                "priority": item.get("priority", "normal"),
                "force_send": bool(item.get("force_send", False)),
                "filters": dict(item.get("filters", {}) or {}),
            }

        cls._events = events_by_key
        cls._loaded = True
        logger.debug("BroadcastEventRegistry loaded %d events.", len(events_by_key))
        return len(events_by_key)

    @classmethod
    def ensure_loaded(cls) -> None:
        if not cls._loaded:
            cls.load()

    # ---------- accessors ----------

    @classmethod
    def all(cls) -> Dict[str, Dict[str, Any]]:
        cls.ensure_loaded()
        return dict(cls._events)

    @classmethod
    def get(cls, event_key: str) -> Optional[Dict[str, Any]]:
        cls.ensure_loaded()
        return cls._events.get(event_key)

    @classmethod
    def channels(cls, event_key: str) -> Iterable[str]:
        ev = cls.get(event_key) or {}
        return list(ev.get("channels", []))

    @classmethod
    def forced_channels(cls, event_key: str) -> Iterable[str]:
        ev = cls.get(event_key) or {}
        return list(ev.get("forced_channels", []))

    @classmethod
    def is_force_send(cls, event_key: str) -> bool:
        ev = cls.get(event_key) or {}
        return bool(ev.get("force_send", False))

    @classmethod
    def priority(cls, event_key: str) -> Any:
        ev = cls.get(event_key) or {}
        return ev.get("priority", "normal")

    @classmethod
    def scope(cls, event_key: str) -> str:
        ev = cls.get(event_key) or {}
        return str(ev.get("scope", "systemwide"))

    @classmethod
    def filters(cls, event_key: str) -> Dict[str, Any]:
        ev = cls.get(event_key) or {}
        return dict(ev.get("filters", {}))


def autoload_broadcast_events() -> int:
    """Convenience loader used by AppConfig.ready()."""
    return BroadcastEventRegistry.load()