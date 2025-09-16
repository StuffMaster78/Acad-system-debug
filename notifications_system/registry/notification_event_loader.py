from __future__ import annotations

"""
Load and register notification event configs.

Sources:
  1) Central path (file or dir) via settings.NOTIFY_EVENTS_DIR
     (defaults to this package's configs dir).
  2) Per-app JSON files under the subdir specified by
     settings.NOTIFY_APP_EVENTS_SUBDIR (default: 'notification_configs').

Supports JSON shapes:
  - List of dicts: [{ "event_key": "...", ... }, ...]
  - Flat map: { "order.paid": {...}, ... }
  - Nested groups:
      { "order": { "paid": {...}, "assigned": {...} } }
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from django.apps import apps
from django.conf import settings

from .main_registry import NOTIFICATION_REGISTRY
from .validator import validate_event_config

logger = logging.getLogger(__name__)

# --------------------
# Configurable paths
# --------------------

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"
EVENT_CONFIG_PATH = CONFIGS_DIR / "notification_event_config.json"

CENTRAL_EVENTS_DIR = Path(
    getattr(settings, "NOTIFY_EVENTS_DIR", str(CONFIGS_DIR))
)

PER_APP_EVENTS_SUBDIR = getattr(
    settings, "NOTIFY_APP_EVENTS_SUBDIR", "notification_configs"
)


# --------------------
# File discovery
# --------------------

def _json_files_in(path: Path) -> Iterable[Path]:
    """Yield *.json files inside a directory, if it exists."""
    if path.exists() and path.is_dir():
        yield from sorted(path.glob("*.json"))


def _central_sources() -> Iterable[Tuple[str, Path]]:
    """Yield ('central', path) for each central JSON source.

    If CENTRAL_EVENTS_DIR is a file -> just that.
    If it's a dir -> every *.json inside.
    Also includes EVENT_CONFIG_PATH if present (legacy single-file).
    """
    if CENTRAL_EVENTS_DIR.exists():
        if CENTRAL_EVENTS_DIR.is_file() and \
                CENTRAL_EVENTS_DIR.suffix.lower() == ".json":
            yield ("central", CENTRAL_EVENTS_DIR)
        elif CENTRAL_EVENTS_DIR.is_dir():
            for f in _json_files_in(CENTRAL_EVENTS_DIR):
                yield ("central", f)

    if EVENT_CONFIG_PATH.exists() and EVENT_CONFIG_PATH.is_file():
        yield ("central", EVENT_CONFIG_PATH)


def _per_app_sources() -> Iterable[Tuple[str, Path]]:
    """Yield ('<app_label>', path) for JSON files in each app subdir."""
    for app_cfg in apps.get_app_configs():
        cfg_dir = Path(app_cfg.path) / PER_APP_EVENTS_SUBDIR
        for f in _json_files_in(cfg_dir):
            yield (app_cfg.label, f)


def _load_json(file_path: Path) -> Any:
    """Read JSON from a file path."""
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------
# Shape handling
# --------------------

def _flatten_events(obj: Any, prefix: str = "") -> List[Tuple[str, Dict]]:
    """Normalize supported JSON shapes to (event_key, cfg) pairs.

    Supports:
      - list:   [{ "event_key": "...", ... }, ...]
      - map:    { "order.paid": {...}, ... }
      - nested: { "order": { "paid": {...}, ... } }

    Args:
        obj: Parsed JSON object.
        prefix: Prefix for nested keys during recursion.

    Returns:
        List of (event_key, config_without_event_key).
    """
    out: List[Tuple[str, Dict]] = []

    # Case: list of dicts with event_key inside each item
    if isinstance(obj, list):
        for item in obj:
            if not isinstance(item, dict) or "event_key" not in item:
                raise ValueError(
                    "List form requires dict items with 'event_key'."
                )
            ek = item["event_key"]
            cfg = {k: v for k, v in item.items() if k != "event_key"}
            out.append((ek, cfg))
        return out

    # Case: flat map { "ev.key": {...} }
    if isinstance(obj, dict) and any(
        isinstance(v, dict) for v in obj.values()
    ) and any("." in k for k in obj.keys()):
        for ek, cfg in obj.items():
            if not isinstance(cfg, dict):
                raise ValueError(f"Config for '{ek}' must be an object.")
            out.append((ek, cfg))
        return out

    # Case: nested groups { "order": { "paid": {...} } }
    if isinstance(obj, dict):
        for k, v in obj.items():
            new_prefix = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                # Heuristic: terminal config likely has these keys
                if any(x in v for x in (
                    "channels", "roles", "priority", "templates",
                    "enabled", "description",
                )):
                    out.append((new_prefix, v))
                else:
                    out.extend(_flatten_events(v, new_prefix))
        return out

    raise ValueError(
        "Unsupported JSON structure: expected list of event dicts, a "
        "dict map of {event_key: config}, or nested groups."
    )


def _normalize_config(event_key: str, cfg: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize legacy keys and general shape for a single event.

    - default_channels -> channels
    - notify_roles     -> roles
    - priority         -> lowercased if str
    - drop: default_channels, notify_roles, event_key (if present)
    """
    normalized: Dict[str, Any] = dict(cfg)

    if "channels" not in normalized and "default_channels" in normalized:
        normalized["channels"] = normalized.pop("default_channels")

    if "roles" not in normalized and "notify_roles" in normalized:
        normalized["roles"] = normalized.pop("notify_roles")

    pr = normalized.get("priority")
    if isinstance(pr, str):
        normalized["priority"] = pr.lower()

    for legacy in ("default_channels", "notify_roles", "event_key"):
        normalized.pop(legacy, None)

    return normalized


# --------------------
# Main entry
# --------------------

def load_event_configs() -> None:
    """Load, validate, and register event configs into the global registry.

    Reads central + per-app sources, flattens to pairs, normalizes
    legacy keys, validates the *inner* config (no event_key), and fills
    NOTIFICATION_REGISTRY with a per-event dict. For each item, attaches
    a '__source__' field for traceability (origin:file).
    """
    sources = list(_central_sources()) + list(_per_app_sources())
    if not sources:
        logger.warning(
            "No notification config sources found. Checked central=%s, "
            "per-app subdir=%s",
            CENTRAL_EVENTS_DIR,
            PER_APP_EVENTS_SUBDIR,
        )
        NOTIFICATION_REGISTRY.clear()
        return

    new_registry: Dict[str, Dict] = {}

    for origin, path in sources:
        try:
            data = _load_json(path)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                f"Failed to load JSON from {path}: {exc}"
            ) from exc

        pairs = _flatten_events(data)

        for ek, raw_cfg in pairs:
            cfg = _normalize_config(ek, raw_cfg)

            # Validate inner config against schema (no 'event_key').
            res = validate_event_config(cfg, schema_name="event_config_schema")
            res.raise_if_failed()

            if ek in new_registry:
                prev = new_registry[ek].get("__source__", "<unknown>")
                raise ValueError(
                    f"Duplicate event_key '{ek}' from {path} ({origin}); "
                    f"already provided by {prev}"
                )

            cfg["__source__"] = f"{origin}:{path.name}"
            new_registry[ek] = cfg
            logger.debug(
                "Registered event '%s' from %s (%s)", ek, path.name, origin
            )

    NOTIFICATION_REGISTRY.clear()
    NOTIFICATION_REGISTRY.update(new_registry)
    logger.info(
        "Loaded %d notification events from %d sources",
        len(new_registry),
        len(sources),
    )


# --------------------
# Test/dev helpers
# --------------------

def reload_event_configs() -> int:
    """Force reload configs and return count of events loaded."""
    load_event_configs()
    return len(NOTIFICATION_REGISTRY)


__all__ = ["load_event_configs", "reload_event_configs"]