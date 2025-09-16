from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

logger = logging.getLogger(__name__)


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


def _validate_json(data: Any, schema_path: Path) -> None:
    """Validate JSON data against a JSON Schema if jsonschema is present.

    Args:
        data: Parsed JSON-compatible object.
        schema_path: Path to the schema file.

    Raises:
        RuntimeError: If validation fails or schema is unreadable.
    """
    try:
        import jsonschema  # type: ignore
    except Exception:
        # Soft dependency: skip validation if library not installed.
        logger.debug("jsonschema not installed; skipping validation.")
        return

    try:
        schema = _read_json(schema_path)
        jsonschema.validate(instance=data, schema=schema)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"JSON schema validation failed: {exc}") from exc


class BroadcastEventRegistry:
    """In-process registry for broadcast event metadata.

    Data source:
        notifications_system/registry/configs/broadcast_events.json

    Schema:
        notifications_system/registry/configs/schemas/
            broadcast_event.schema.json

    The registry is process-local and safe to call repeatedly; loads are
    idempotent.

    Stored per event (keyed by `event_key`):
        {
          "event_key": str,
          "description": str,
          "scope": "systemwide" | "website",
          "default_channels": [str, ...],
          "forced_channels": [str, ...],
          "priority": str | int,
          "force_send": bool,
          "filters": { ... }
        }
    """

    _loaded: bool = False
    _events: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def load(cls) -> int:
        """Load and validate broadcast event configs into the registry.

        Returns:
            Number of events loaded.
        """
        cfg_path = _pkg_path("configs", "broadcast_events.json")
        schema_path = _pkg_path(
            "configs", "schemas", "broadcast_event.schema.json"
        )

        data = _read_json(cfg_path)
        _validate_json(data, schema_path)

        events: Dict[str, Dict[str, Any]] = {}
        for item in data:
            try:
                key = str(item["event_key"])
            except KeyError as exc:
                raise RuntimeError("broadcast item missing event_key") from exc

            events[key] = {
                "event_key": key,
                "description": item.get("description", ""),
                "scope": item.get("scope", "systemwide"),
                "default_channels": list(
                    item.get("default_channels", [])
                ),
                "forced_channels": list(
                    item.get("forced_channels", [])
                ),
                "priority": item.get("priority", "normal"),
                "force_send": bool(item.get("force_send", False)),
                "filters": dict(item.get("filters", {})),
            }

        cls._events = events
        cls._loaded = True
        logger.debug("BroadcastEventRegistry loaded %d events.", len(events))
        return len(events)

    @classmethod
    def ensure_loaded(cls) -> None:
        """Load registry if not already loaded."""
        if not cls._loaded:
            cls.load()

    # ---------- Accessors ----------

    @classmethod
    def all(cls) -> Dict[str, Dict[str, Any]]:
        """Return a copy of the full registry."""
        cls.ensure_loaded()
        return dict(cls._events)

    @classmethod
    def get(cls, event_key: str) -> Optional[Dict[str, Any]]:
        """Return the event dict for an event_key, or None."""
        cls.ensure_loaded()
        return cls._events.get(event_key)

    @classmethod
    def default_channels(cls, event_key: str) -> Iterable[str]:
        """Return default channels for an event."""
        ev = cls.get(event_key) or {}
        return list(ev.get("default_channels", []))

    @classmethod
    def forced_channels(cls, event_key: str) -> Iterable[str]:
        """Return forced channels for an event (may be empty)."""
        ev = cls.get(event_key) or {}
        return list(ev.get("forced_channels", []))

    @classmethod
    def is_force_send(cls, event_key: str) -> bool:
        """Return True if event bypasses preferences."""
        ev = cls.get(event_key) or {}
        return bool(ev.get("force_send", False))

    @classmethod
    def priority(cls, event_key: str) -> Any:
        """Return priority for an event (label or int)."""
        ev = cls.get(event_key) or {}
        return ev.get("priority", "normal")

    @classmethod
    def scope(cls, event_key: str) -> str:
        """Return scope ('systemwide' or 'website')."""
        ev = cls.get(event_key) or {}
        return str(ev.get("scope", "systemwide"))

    @classmethod
    def filters(cls, event_key: str) -> Dict[str, Any]:
        """Return filters dict (e.g., roles) for targeting."""
        ev = cls.get(event_key) or {}
        return dict(ev.get("filters", {}))


def autoload_broadcast_events() -> int:
    """Convenience loader used by AppConfig.ready()."""
    return BroadcastEventRegistry.load()