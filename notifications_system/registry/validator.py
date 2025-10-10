# notifications_system/registry/validator.py
# -*- coding: utf-8 -*-
"""
Schema validation utilities for notification event configs.

This module loads JSON Schemas from the installed package data first and
falls back to the filesystem. It validates event configuration objects
against those schemas and provides friendly error messages.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import importlib.resources as resources
# from jsonschema import Draft7Validator as _Validator
from jsonschema import (
    RefResolver,
    exceptions as js_exceptions,
    Draft202012Validator
)

logger = logging.getLogger(__name__)

# Package path that contains bundled schema JSON files. Ensure these are
# included in your package data (pyproject/MANIFEST.in).
SCHEMA_PACKAGE = "notifications_system.registry.configs.schemas"

# Filesystem fallback for local development.
SCHEMA_BASE_DIR = Path(__file__).resolve().parent / "configs" / "schemas"

# Cache to avoid re-reading the same schema multiple times.
_SCHEMA_CACHE: Dict[str, Dict[str, Any]] = {}

# At top-level (near SCHEMA_* constants)
# SCHEMA_BY_PREFIX = {
#     "user.": "user_event_schema",
#     "order.": "order_event_schema",
#     "wallet.": "wallet_event_schema",
# }
# DEFAULT_EVENT_SCHEMA = "event_config_schema"
SCHEMA_BY_PREFIX = {
    "user.": "user_event_schema",    # maps to user_event.schema.json
    "order.": "order_event_schema",  # maps to order_event.schema.json
    "wallet.": "wallet_event_schema" # maps to wallet_event.schema.json
}
DEFAULT_EVENT_SCHEMA = "event_config_schema"  # event_config_schema.json exists


@dataclass
class ValidationResult:
    """Structured result for schema validation.

    Attributes:
        ok: True if validation passed, False otherwise.
        errors: List of readable validation error messages.
    """

    ok: bool
    errors: List[str]

    def raise_if_failed(self) -> None:
        """Raise ValueError when validation failed.

        Raises:
            ValueError: If validation produced one or more errors.
        """
        if not self.ok:
            raise ValueError("\n".join(self.errors))

def select_schema_for_event(event_key: str) -> str:
    """Choose schema name based on event key prefix.

    Args:
        event_key: Dotted event key, e.g. "user.password_reset".

    Returns:
        Schema name without ".json".
    """
    for prefix, schema in SCHEMA_BY_PREFIX.items():
        if event_key.startswith(prefix):
            return schema
    return DEFAULT_EVENT_SCHEMA


def _load_from_pkg(name: str) -> Optional[Dict[str, Any]]:
    """Load a JSON file from package resources.

    Args:
        name: File name (e.g., "event_config_schema.json").

    Returns:
        Parsed JSON dict, or None if the file is not in the package.

    Raises:
        ValueError: If the file exists but is empty or invalid JSON.
    """
    try:
        file = resources.files(SCHEMA_PACKAGE).joinpath(name)
        with file.open("r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            raise ValueError(f"Schema '{name}' in package is empty.")
        return json.loads(content)
    except FileNotFoundError:
        return None


def _load_from_fs(path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file from the filesystem.

    Args:
        path: Full path to a JSON file.

    Returns:
        Parsed JSON dict, or None if the file does not exist.

    Raises:
        ValueError: If the file exists but is empty or invalid JSON.
    """
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Schema file is empty: {path}")
    return json.loads(content)


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load (and cache) a JSON Schema by name.

    This tries package data first, then falls back to the local filesystem.

    Args:
        schema_name: Schema name without ".json" (e.g., "event_config_schema").

    Returns:
        Parsed JSON schema dict.

    Raises:
        FileNotFoundError: When the schema is not found in either location.
        ValueError: When a found file is empty or invalid JSON.
    """
    if schema_name in _SCHEMA_CACHE:
        return _SCHEMA_CACHE[schema_name]

    filename = f"{schema_name}.json"

    data = _load_from_pkg(filename)
    if data is None:
        data = _load_from_fs(SCHEMA_BASE_DIR / filename)

    if data is None:
        raise FileNotFoundError(
            "Schema '{name}' not found in package '{pkg}' or filesystem "
            "path '{path}'.".format(
                name=schema_name,
                pkg=SCHEMA_PACKAGE,
                path=SCHEMA_BASE_DIR / filename,
            )
        )

    _SCHEMA_CACHE[schema_name] = data
        # also cache by $id to help any callers that look it up by id
    schema_id = data.get("$id")
    if isinstance(schema_id, str) and schema_id.strip():
        _SCHEMA_CACHE[schema_id] = data
    return data


def get_schema_names() -> List[str]:
    """List available schema names (without the .json suffix).

    Returns:
        Sorted list of schema names visible on the filesystem fallback.
        Note: This only inspects the filesystem, not the package.
    """
    if not SCHEMA_BASE_DIR.exists():
        logger.warning("Schema directory not found: %s", SCHEMA_BASE_DIR)
        return []
    return sorted(p.stem for p in SCHEMA_BASE_DIR.glob("*.json") if p.is_file())


def _schema_path(schema_name: str) -> Path:
    """Resolve a schema file path from a schema name.

    Args:
        schema_name: Schema name without ".json".

    Returns:
        Filesystem path for the schema.

    Raises:
        FileNotFoundError: If the schema file is missing on the filesystem.
    """
    path = SCHEMA_BASE_DIR / f"{schema_name}.json"
    if not path.exists():
        raise FileNotFoundError(
            f"Schema '{schema_name}' not found at {path}"
        )
    return path

def validate_event_pair(event_key: str, cfg: dict) -> ValidationResult:
    """Validate one event config chosen by its key.

    Args:
        event_key: Dotted key for the event.
        cfg: Config object (value of the map entry).

    Returns:
        ValidationResult for this item.
    """
    schema_name = select_schema_for_event(event_key)
    schema = load_schema(schema_name)
    resolver = _build_resolver(SCHEMA_BASE_DIR)
    return _validate_obj(cfg, schema, resolver=resolver)

def validate_event_list(items: list) -> ValidationResult:
    """Validate a list-style config: [{event_key: "...", ...}].

    Returns:
        ValidationResult aggregating item errors.
    """
    if not isinstance(items, list):
        return ValidationResult(False, ["$: expected array (list form)"])

    errors: List[str] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"$[{idx}]: must be an object")
            continue
        ek = item.get("event_key")
        if not isinstance(ek, str) or not ek:
            errors.append(f"$[{idx}].event_key: required non-empty string")
            continue
        cfg = {k: v for k, v in item.items() if k != "event_key"}
        res = validate_event_pair(ek, cfg)
        if not res.ok:
            pref = f"$[{idx}]"
            errors.extend([e.replace("$", pref, 1) if e.startswith("$")
                           else f"{pref}: {e}" for e in res.errors])

    return ValidationResult(not errors, errors)



def validate_event_map(data: dict) -> ValidationResult:
    """Validate a map-style config: { "ev.key": {..}, ... }.

    Returns:
        ValidationResult aggregating all key-specific errors.
    """
    if not isinstance(data, dict):
        return ValidationResult(False, ["$: expected object (map form)"])

    errors: List[str] = []
    for ek, cfg in data.items():
        if not isinstance(cfg, dict):
            errors.append(f"$.{ek}: value must be an object")
            continue
        res = validate_event_pair(ek, cfg)
        if not res.ok:
            prefixed = [f"$.{ek}{e[1:]}" if e.startswith("$") else
                        f"$.{ek}: {e}" for e in res.errors]
            errors.extend(prefixed)

    return ValidationResult(not errors, errors)


def validate_events_any(data: Any) -> ValidationResult:
    """Validate events in either map or list form.

    Args:
        data: Parsed JSON object (dict or list).

    Returns:
        ValidationResult.
    """
    if isinstance(data, dict):
        return validate_event_map(data)
    if isinstance(data, list):
        return validate_event_list(data)
    return ValidationResult(False, ["$: expected object or array"])


def validate_events_file(path: Union[str, Path]) -> ValidationResult:
    """Validate a config file containing events (map or list form)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"Config file is empty: {p}")
    data = json.loads(text)
    return validate_events_any(data)




def _build_resolver(base_dir: Path) -> RefResolver:
    """Build a RefResolver for local $ref resolution (no network)."""
    base_uri = base_dir.as_uri() + "/"
    store: Dict[str, dict] = {}

    # Preload all schemas in the directory into the store
    for p in base_dir.glob("*.json"):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            # 1) map by file URI
            store[p.as_uri()] = doc
            # 2) map by $id, if present
            schema_id = doc.get("$id")
            if isinstance(schema_id, str) and schema_id.strip():
                store[schema_id] = doc
        except Exception as exc:
            logger.warning("Failed to preload schema %s: %s", p, exc)

    # Handler that resolves http(s) URIs to local files in base_dir
    def _local_handler(uri: str) -> dict:
        # Direct hit in store?
        if uri in store:
            return store[uri]
        # Try by filename suffix
        name = uri.rsplit("/", 1)[-1]
        candidate = base_dir / name
        if candidate.exists():
            try:
                doc = json.loads(candidate.read_text(encoding="utf-8"))
                store[uri] = doc
                return doc
            except Exception as exc:  # pragma: no cover
                raise RuntimeError(f"Failed reading local schema for {uri}: {exc}") from exc
        raise RuntimeError(f"No local schema mapped for {uri}")

    # Save handlers on the resolver (Draft202012Validator will consume them)
    resolver = RefResolver(base_uri=base_uri, referrer=None, store=store)
    resolver.handlers = {"http": _local_handler, "https": _local_handler}
    return resolver



def _normalize_errors(
    errors: Iterable[js_exceptions.ValidationError],
) -> List[str]:
    """Convert jsonschema ValidationError objects to readable strings.

    Args:
        errors: Iterable of jsonschema ValidationError.

    Returns:
        List of human-readable error messages with JSON pointer paths.
    """
    normalized: List[str] = []
    for err in sorted(errors, key=lambda e: e.path):
        path = "$"
        if err.path:
            path = "$." + ".".join(str(x) for x in err.path)
        normalized.append(f"{path}: {err.message}")
    return normalized


def _validate_obj(
    obj: dict,
    schema: dict,
    resolver: Optional[RefResolver] = None,
) -> ValidationResult:
    """Validate an object against a schema.

    Args:
        obj: The JSON-like dict to validate.
        schema: The loaded JSON Schema dict.
        resolver: Optional RefResolver for local $ref lookups.

    Returns:
        ValidationResult with success flag and error messages.
    """
    try:
        validator = Draft202012Validator(schema, resolver=resolver)
        errors = list(validator.iter_errors(obj))
        if errors:
            return ValidationResult(False, _normalize_errors(errors))
        return ValidationResult(True, [])
    except js_exceptions.SchemaError as exc:
        msg = f"Invalid schema: {exc.message}"
        logger.error(msg)
        return ValidationResult(False, [msg])
    except Exception as exc:
        msg = f"Unexpected validation error: {exc}"
        logger.exception(msg)
        return ValidationResult(False, [msg])


def validate_event_config(
    config: Union[dict, str, Path],
    schema_name: str = "event_config_schema",
) -> ValidationResult:
    """Validate a single event config against a named schema.

    Args:
        config: Dict to validate or a path (str/Path) to a JSON file.
        schema_name: Schema name without ".json" to validate against.

    Returns:
        ValidationResult describing success or errors.

    Raises:
        ValueError: If loading a file yields empty/invalid JSON.
        FileNotFoundError: If the schema cannot be located.
    """
    if isinstance(config, (str, Path)):
        path = Path(config)
        text = path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Config file is empty: {path}")
        config = json.loads(text)

    schema = load_schema(schema_name)
    resolver = _build_resolver(SCHEMA_BASE_DIR)
    return _validate_obj(config, schema, resolver=resolver)


def validate_config_file(
    file_path: Union[str, Path],
    schema_name: str = "event_config_schema",
) -> ValidationResult:
    """Validate a JSON config file against a named schema.

    Args:
        file_path: Path to a JSON file.
        schema_name: Schema name without ".json".

    Returns:
        ValidationResult describing success or errors.
    """
    return validate_event_config(Path(file_path), schema_name=schema_name)


def validate_all_in_dir(
    config_dir: Union[str, Path],
    schema_name: str = "event_config_schema",
    glob: str = "*.json",
) -> Tuple[bool, List[Tuple[Path, ValidationResult]]]:
    """Validate all JSON config files in a directory.

    Args:
        config_dir: Directory containing JSON configs.
        schema_name: Schema name without ".json".
        glob: Glob to select files (default: "*.json").

    Returns:
        Tuple of (overall_ok, results), where:
          - overall_ok is True iff all files validated successfully.
          - results is a list of (path, ValidationResult).
    """
    base = Path(config_dir)
    results: List[Tuple[Path, ValidationResult]] = []
    overall_ok = True

    for p in sorted(base.glob(glob)):
        if not p.is_file():
            continue
        result = validate_config_file(p, schema_name=schema_name)
        results.append((p, result))
        if not result.ok:
            overall_ok = False

    return overall_ok, results

# ----------------------------
# File-level validators we call from loaders
# ----------------------------

def validate_broadcast_events(data: Any) -> ValidationResult:
    """
    Validate broadcast events file (list form or wrapped {"events":[...]}).
    Uses broadcast_event.schema.json (root may be array or object).
    """
    schema = load_schema("broadcast_event")  # broadcast_event.schema.json
    resolver = _build_resolver(SCHEMA_BASE_DIR)

    # Many configs may use {"events":[...]} as root; accept both.
    inst = data.get("events") if isinstance(data, dict) and "events" in data else data
    return _validate_obj(inst, schema, resolver=resolver)


def validate_digest_events(data: Any) -> ValidationResult:
    """
    Validate digest events file (list form or wrapped {"events":[...]}).
    Uses digest_event.schema.json.
    """
    schema = load_schema("digest_event")  # digest_event.schema.json
    resolver = _build_resolver(SCHEMA_BASE_DIR)
    inst = data.get("events") if isinstance(data, dict) and "events" in data else data
    return _validate_obj(inst, schema, resolver=resolver)


def validate_notification_events(data: Any) -> ValidationResult:
    """
    Validate notification events file.
    Accepts:
      - list of event dicts (must contain key/event_key per item)
      - wrapped {"events":[...]}
      - mapping {"order.paid": {...}} (we validate per-item via per-event schemas)
    """
    # If wrapped object, peel to list
    if isinstance(data, dict) and "events" in data and isinstance(data["events"], list):
        return validate_events_any(data["events"])

    # If list or dict, validate via our per-item logic which picks schema by prefix.
    if isinstance(data, (list, dict)):
        return validate_events_any(data)

    return ValidationResult(False, ["$: expected object or array"])