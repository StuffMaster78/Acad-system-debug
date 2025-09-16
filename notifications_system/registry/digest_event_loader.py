from __future__ import annotations

"""
Digest event config loader.

Loads digestable event configs from JSON, validates them against the
schema, and fills DIGEST_EVENT_REGISTRY. Optional 'forced_channels' in
a digest config will be registered with ForcedChannelRegistry.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from django.conf import settings

from .main_registry import DIGEST_EVENT_REGISTRY
from .validator import validate_event_config
from .forced_channels import ForcedChannelRegistry  # if you expose this

logger = logging.getLogger(__name__)

CONFIGS_DIR = Path(__file__).resolve().parent / "configs"
DEFAULT_CONFIG_FILE = CONFIGS_DIR / "digest_event_config.json"

# Allow override via settings, else use default path.
CONFIG_FILE = Path(
    getattr(settings, "NOTIFY_DIGEST_CONFIG_FILE", str(DEFAULT_CONFIG_FILE))
)

SCHEMA_NAME = "digest_event_schema"  # your validator’s schema label


def _load_json(path: Path) -> Any:
    """Read JSON from file."""
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _flatten(items: Any) -> List[Tuple[str, Dict[str, Any]]]:
    """Normalize list/map forms to pairs of (event_key, config)."""
    out: List[Tuple[str, Dict[str, Any]]] = []
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict) or "event_key" not in it:
                raise ValueError("List items must be dicts with event_key.")
            ek = it["event_key"]
            cfg = {k: v for k, v in it.items() if k != "event_key"}
            out.append((ek, cfg))
        return out
    if isinstance(items, dict):
        # { "event.key": { ... } } form
        for ek, cfg in items.items():
            if not isinstance(cfg, dict):
                raise ValueError(f"Config for '{ek}' must be an object.")
            out.append((ek, cfg))
        return out
    raise ValueError("Unsupported digest config shape (list or map only).")


def autoload_digest_events() -> int:
    """Load, validate, and register digest events from CONFIG_FILE.

    Returns:
        int: Number of digest events registered.
    """
    if not CONFIG_FILE.exists():
        logger.info("Digest config not found: %s (skipping)", CONFIG_FILE)
        DIGEST_EVENT_REGISTRY.clear()
        return 0

    data = _load_json(CONFIG_FILE)
    pairs = _flatten(data)

    new_registry: Dict[str, Dict[str, Any]] = {}

    for ek, cfg in pairs:
        # Validate against your JSON schema registry by name
        res = validate_event_config(cfg, schema_name=SCHEMA_NAME)
        res.raise_if_failed()

        # Normalize minimal fields; keep others as-is
        delay = cfg.get("delay_minutes")
        group_by = cfg.get("group_by")

        if delay is None or not isinstance(delay, int) or delay < 0:
            raise ValueError(
                f"'{ek}': delay_minutes must be non-negative int"
            )
        if not isinstance(group_by, str) or not group_by.strip():
            raise ValueError(f"'{ek}': group_by must be a non-empty string")

        new_registry[ek] = {
            "delay_minutes": delay,
            "group_by": group_by,
            **{k: v for k, v in cfg.items() if k not in
               {"delay_minutes", "group_by"}},
            "__source__": str(CONFIG_FILE),
        }

        # Optional: register forced channels if present
        forced = cfg.get("forced_channels") or []
        if forced:
            try:
                ForcedChannelRegistry.add  # type: ignore[attr-defined]
                for ch in forced:
                    ForcedChannelRegistry.add(ek, ch)  # pyright: ignore
            except Exception:
                # If your ForcedChannelRegistry has a static .get(...) API
                # and not .add, ignore gracefully
                logger.debug("Forced channel registration skipped for %s", ek)

    DIGEST_EVENT_REGISTRY.clear()
    DIGEST_EVENT_REGISTRY.update(new_registry)

    logger.info(
        "Loaded %d digest events from %s", len(new_registry), CONFIG_FILE
    )
    return len(new_registry)


__all__ = ["autoload_digest_events"]