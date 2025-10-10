# notifications_system/registry/notification_event_loader.py
from __future__ import annotations
"""
Load and register notification event configs.

Sources:
  1) Central path (file or dir) via settings.NOTIFY_EVENTS_DIR
     (defaults to this package's configs dir).
  2) Legacy single file at configs/notification_event_config.json.
  3) Per-app JSON files under settings.NOTIFY_APP_EVENTS_SUBDIR
     (default: 'notification_configs') inside each installed app.

Supported root shapes per file:
  - List of dicts:                [{"key": "...", "templates": {...}, ...}, ...]
  - List with 'event_key' only:   [{"event_key": "..." , ...}, ...]  (we fill 'key')
  - Flat map:                     {"order.paid": {...}, "order.assigned": {...}}
  - Wrapped object:               {"events": [ ... ]}
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from django.apps import apps
from django.conf import settings

from .main_registry import NOTIFICATION_REGISTRY
from .compat import normalize_notifications
from .validator import validate_notification_events

logger = logging.getLogger(__name__)

# --------------------
# Configurable paths
# --------------------

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"
LEGACY_SINGLE_FILE = CONFIGS_DIR / "notification_event_config.json"

CENTRAL_EVENTS_DIR = Path(getattr(settings, "NOTIFY_EVENTS_DIR", str(CONFIGS_DIR)))
PER_APP_EVENTS_SUBDIR = getattr(settings, "NOTIFY_APP_EVENTS_SUBDIR", "notification_configs")


# --------------------
# File discovery
# --------------------

def _json_files_in(path: Path) -> Iterable[Path]:
    """Yield *.json files inside a directory, if it exists."""
    if path.exists() and path.is_dir():
        yield from sorted(path.glob("*.json"))


# def _central_sources() -> Iterable[Tuple[str, Path]]:
#     """
#     Yield ('central', path) for JSON sources:
#       * NOTIFY_EVENTS_DIR (file -> itself; dir -> each *.json inside)
#       * legacy single file notification_event_config.json
#     """
#     if CENTRAL_EVENTS_DIR.exists():
#         if CENTRAL_EVENTS_DIR.is_file() and CENTRAL_EVENTS_DIR.suffix.lower() == ".json":
#             yield ("central", CENTRAL_EVENTS_DIR)
#         elif CENTRAL_EVENTS_DIR.is_dir():
#             for f in _json_files_in(CENTRAL_EVENTS_DIR):
#                 yield ("central", f)

#     if LEGACY_SINGLE_FILE.exists() and LEGACY_SINGLE_FILE.is_file():
#         yield ("central", LEGACY_SINGLE_FILE)

def _central_sources() -> Iterable[Tuple[str, Path]]:
    skip_names = {"digest_event_config.json", "broadcast_event_config.json"}
    seen: set[Path] = set()

    def _yield_once(origin: str, p: Path):
        rp = p.resolve()
        if rp in seen:
            return
        seen.add(rp)
        yield (origin, rp)

    if CENTRAL_EVENTS_DIR.exists():
        if CENTRAL_EVENTS_DIR.is_file() and CENTRAL_EVENTS_DIR.suffix.lower() == ".json":
            if CENTRAL_EVENTS_DIR.name not in skip_names:
                yield from _yield_once("central", CENTRAL_EVENTS_DIR)
        elif CENTRAL_EVENTS_DIR.is_dir():
            for f in _json_files_in(CENTRAL_EVENTS_DIR):
                if f.name not in skip_names:
                    yield from _yield_once("central", f)

    if LEGACY_SINGLE_FILE.exists() and LEGACY_SINGLE_FILE.is_file():
        # only if not already yielded by the directory case
        yield from _yield_once("central", LEGACY_SINGLE_FILE)




def _per_app_sources() -> Iterable[Tuple[str, Path]]:
    """Yield ('<app_label>', path) for JSON files in each app's subdir."""
    for app_cfg in apps.get_app_configs():
        cfg_dir = Path(app_cfg.path) / PER_APP_EVENTS_SUBDIR
        for f in _json_files_in(cfg_dir):
            yield (app_cfg.label, f)


# --------------------
# Low-level helpers
# --------------------

def _read_json(file_path: Path) -> Any:
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def _to_list_from_mapping(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    {"order.paid": {...}} -> [{"key": "order.paid", "event_key": "order.paid", ...}]
    """
    lst: List[Dict[str, Any]] = []
    for k, v in d.items():
        if not isinstance(v, dict):
            raise ValueError(f"Config for '{k}' must be an object.")
        item = dict(v)
        item.setdefault("key", k)
        item.setdefault("event_key", k)
        lst.append(item)
    return lst

def _wrap_in_object(a: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Some schemas want an object at root; common wrapper is {'events': [...]}."""
    return {"events": a}




# --------------------
# Schema shape negotiation (per file)
# --------------------

def _to_list_from_events_wrapper(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Accept {"events": <list|map>} and normalize to a list of dicts with keys.
    """
    ev = d.get("events")
    if isinstance(ev, list):
        # Ensure key/event_key on each item
        patched: List[Dict[str, Any]] = []
        for it in ev:
            if not isinstance(it, dict):
                raise ValueError("List items must be objects.")
            k = it.get("key") or it.get("event_key")
            if not k:
                raise ValueError(
                    "Each event item must include 'key' or 'event_key'."
                )
            item = dict(it)
            item.setdefault("key", k)
            item.setdefault("event_key", k)
            patched.append(item)
        return patched
    if isinstance(ev, dict):
        # Map form -> list
        return _to_list_from_mapping(ev)
    raise ValueError("'events' must be a list or an object.")


def load_notification_events(path: Optional[Path] = None) -> Any:
    """Load, normalize, and validate one events JSON file.

    Tries plausible root shapes until the schema accepts one.
    Returns the accepted structure (list or wrapped object).
    """
    cfg_path = path or LEGACY_SINGLE_FILE
    raw = _read_json(cfg_path)

    candidates: List[Any] = [raw]

    # 1) tolerant normalizer
    try:
        norm = normalize_notifications(raw)
        if norm != raw:
            candidates.append(norm)
    except Exception:
        pass

    # 2) mapping/list/wrapped variants
    if isinstance(raw, dict):
        if "events" in raw:
            try:
                lst = _to_list_from_events_wrapper(raw)
                candidates.append(lst)              # plain list
                candidates.append(_wrap_in_object(lst))  # wrapped list
            except Exception:
                # Fallback: treat whole dict as mapping of events.
                lst = _to_list_from_mapping(raw)
                candidates.append(lst)
                candidates.append(_wrap_in_object(lst))
        else:
            lst = _to_list_from_mapping(raw)
            candidates.append(lst)
            candidates.append(_wrap_in_object(lst))
    elif isinstance(raw, list):
        patched: List[Dict[str, Any]] = []
        for it in raw:
            if not isinstance(it, dict):
                raise ValueError("List items must be objects.")
            k = it.get("key") or it.get("event_key")
            if not k:
                raise ValueError(
                    "Each event item must include 'key' or 'event_key'."
                )
            item = dict(it)
            item.setdefault("key", k)
            item.setdefault("event_key", k)
            patched.append(item)
        candidates.append(_wrap_in_object(patched))

    # 3) validate candidates
    errors: List[str] = []
    for data in candidates:
        try:
            validate_notification_events(data)
            logger.debug(
                "notification_event_config validated with shape: %s (%s)",
                type(data).__name__,
                cfg_path.name,
            )
            return data
        except Exception as e:
            errors.append(f"{cfg_path.name}: {e!r}")

    raise ValueError(
        "notification_event_config: no acceptable root shape. Tried "
        "variants:\n" + "\n".join(f"- {e}" for e in errors[:8])
    )


# --------------------
# Registry population
# --------------------

def _iter_items(validated: Any) -> List[Dict[str, Any]]:
    """
    Return a list of event dicts regardless of accepted root shape.
    Supports:
      - list of items
      - {"events": [ ... ]}
      - {"events": { "event.key": {...}, ... }}
      - flat map: { "event.key": {...}, ... }
    """
    # Case 1: already a list
    if isinstance(validated, list):
        return validated

    # Case 2: wrapped
    if isinstance(validated, dict):
        ev = validated["events"]
        if isinstance(ev, list):
            return ev
        if isinstance(ev, dict):
            return _to_list_from_mapping(ev)

    raise RuntimeError(
        "Validated notification config not in a recognized iterable shape."
    )

def _canonical_key(item: Dict[str, Any]) -> str:
    k = (item.get("key") or item.get("event_key") or "").strip()
    if not k:
        raise ValueError("Notification item missing 'key'/'event_key'.")
    return k

def load_event_configs() -> None:
    """
    Load, validate, and register all notification event configs into the global registry.

    Reads central + per-app sources, validates each file by schema (with
    root-shape negotiation), then merges items into NOTIFICATION_REGISTRY,
    keyed by canonical event key. Keeps all original fields and attaches
    '__source__' for traceability.
    """
    sources = list(_central_sources()) + list(_per_app_sources())
    if not sources:
        logger.warning(
            "No notification config sources found. Checked central=%s, per-app subdir=%s",
            CENTRAL_EVENTS_DIR, PER_APP_EVENTS_SUBDIR
        )
        NOTIFICATION_REGISTRY.clear()
        return

    new_registry: Dict[str, Dict[str, Any]] = {}

    for origin, path in sources:
        try:
            validated = load_notification_events(path)
        except Exception as exc:  # noqa: BLE001
            raise ValueError(f"Failed to load/validate {path}: {exc}") from exc

        for item in _iter_items(validated):
            if not isinstance(item, dict):
                raise ValueError(f"{path}: event item must be an object.")
            # Ensure canonical keys exist
            key = _canonical_key(item)
            # Prefer 'key' as canonical, but keep both in stored record
            cfg = dict(item)
            cfg["key"] = key
            cfg.setdefault("event_key", key)
            cfg["__source__"] = f"{origin}:{path.name}"

            if key in new_registry:
                prev = new_registry[key].get("__source__", "<unknown>")
                raise ValueError(
                    f"Duplicate event key '{key}' from {path} ({origin}); already provided by {prev}"
                )

            new_registry[key] = cfg
            logger.debug("Registered event '%s' from %s (%s)", key, path.name, origin)

    NOTIFICATION_REGISTRY.clear()
    NOTIFICATION_REGISTRY.update(new_registry)
    logger.info(
        "Loaded %d notification events from %d sources",
        len(new_registry), len(sources)
    )

def reload_event_configs() -> int:
    """Force reload configs and return count of events loaded."""
    load_event_configs()
    return len(NOTIFICATION_REGISTRY)

__all__ = ["load_notification_events", "load_event_configs", "reload_event_configs"]