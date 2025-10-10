from __future__ import annotations
"""
Digest event config loader.

Loads digestable event configs from JSON, validates them against the
digest schema, and fills DIGEST_EVENT_REGISTRY. Optional 'forced_channels'
in a digest config will be registered with ForcedChannelRegistry.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from django.conf import settings

from .main_registry import DIGEST_EVENT_REGISTRY
from .compat import normalize_digest
from .validator import validate_config_file  # use generic validator with schema_name

try:
    from .forced_channels import ForcedChannelRegistry  # optional
except Exception:  # pragma: no cover
    ForcedChannelRegistry = None  # type: ignore

logger = logging.getLogger(__name__)

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"
DEFAULT_CONFIG_FILE = CONFIGS_DIR / "digest_event_config.json"
CONFIG_FILE = Path(getattr(settings, "NOTIFY_DIGEST_CONFIG_FILE", str(DEFAULT_CONFIG_FILE)))


# ---------- helpers ----------

def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed reading JSON: {path}: {exc}") from exc


def _map_to_list(d: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    {"user.activity_digest": {...}}  -->
    [{"event_key": "user.activity_digest", ...}]
    """
    return [{**v, "event_key": k} for k, v in d.items()]


def _load_and_normalize(path: Path) -> List[Dict[str, Any]]:
    """
    Validate the file against the digest schema, accept mapping or list,
    normalize to a list, run tolerant normalizer, and sanity-check items.
    """
    # Validate the raw file against the digest schema (no ".json" in name)
    res = validate_config_file(path, schema_name="digest_event.schema")
    res.raise_if_failed()

    raw = _read_json(path)

    # Accept either list or mapping; normalize to list
    if isinstance(raw, dict):
        items = _map_to_list(raw)
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError(
            "digest_event_config.json must be either a list of objects or a mapping "
            "{event_key: { ... }}."
        )

    # Apply tolerant normalizer (idempotent if already normalized)
    try:
        items = normalize_digest(items)
    except Exception:
        pass

    # Minimal sanity
    for idx, it in enumerate(items):
        if not isinstance(it, dict):
            raise ValueError(f"digest_event_config item #{idx} is not an object")
        if not it.get("event_key"):
            raise ValueError(f"digest_event_config item #{idx} missing 'event_key'")

    return items


# ---------- registry population ----------

def autoload_digest_events(path: Optional[Path] = None) -> int:
    """
    Load, validate, and register digest events.
    Returns number of events registered.
    """
    cfg_path = path or CONFIG_FILE
    if not cfg_path.exists():
        logger.info("Digest config not found: %s (skipping)", cfg_path)
        DIGEST_EVENT_REGISTRY.clear()
        return 0

    items = _load_and_normalize(cfg_path)

    new_registry: Dict[str, Dict[str, Any]] = {}

    for item in items:
        ek = str(item["event_key"]).strip()
        if not ek:
            raise ValueError("Digest item has empty 'event_key'.")

        # Required fields (schema enforces; we double-check)
        interval = item.get("interval")
        group_by = item.get("group_by")
        digest = item.get("digest")

        if not isinstance(interval, str) or not interval:
            raise ValueError(f"'{ek}': 'interval' must be a non-empty string.")
        if not isinstance(group_by, str) or not group_by:
            raise ValueError(f"'{ek}': 'group_by' must be a non-empty string.")
        if not isinstance(digest, dict):
            raise ValueError(f"'{ek}': 'digest' must be an object.")

        cfg = dict(item)
        cfg["__source__"] = str(cfg_path)
        new_registry[ek] = cfg

        # Optional forced channels
        forced = cfg.get("forced_channels") or []
        if ForcedChannelRegistry and isinstance(forced, list) and forced:
            try:
                for ch in forced:
                    ForcedChannelRegistry.add(ek, ch)  # type: ignore[attr-defined]
            except Exception:
                logger.debug("Forced channel registration skipped for %s", ek)

    DIGEST_EVENT_REGISTRY.clear()
    DIGEST_EVENT_REGISTRY.update(new_registry)

    logger.info("Loaded %d digest events from %s", len(new_registry), cfg_path)
    return len(new_registry)


__all__ = ["autoload_digest_events"]