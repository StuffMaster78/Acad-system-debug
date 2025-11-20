import os
import sys
import json
import glob
import logging
from pathlib import Path

from jsonschema import validate, RefResolver, ValidationError, SchemaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("event_config_validator")

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"
DEFAULT_SCHEMA = SCHEMA_DIR / "base_event.schema.json"

def load_json_file(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def build_resolver():
    """Builds a JSON Schema resolver to handle $refs across schemas."""
    schema_map = {}
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            schema_map[str(schema_path.name)] = schema
    return RefResolver(base_uri="", referrer=None, store=schema_map)

def get_schema_for_event(event_data: dict) -> dict:
    """Returns the correct schema based on event type."""
    event_type = event_data.get("type")
    schema_file = f"{event_type}_event.schema.json"
    full_path = SCHEMA_DIR / schema_file
    if full_path.exists():
        return load_json_file(full_path)
    logger.warning(f"Schema for '{event_type}' not found. Using base schema.")
    return load_json_file(DEFAULT_SCHEMA)

def validate_config_file(config_path: Path):
    """Validates a notification config JSON file against per-event schemas."""
    try:
        config_data = load_json_file(config_path)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON file: {e}")
        sys.exit(1)

    resolver = build_resolver()
    total, passed, failed = 0, 0, 0

    for event_key, event_config in config_data.items():
        total += 1
        try:
            schema = get_schema_for_event(event_config)
            validate(instance=event_config, schema=schema, resolver=resolver)
            logger.info(f"✅ Valid: {event_key}")
            passed += 1
        except ValidationError as ve:
            logger.error(f"❌ Invalid: {event_key}\n{ve.message}")
            failed += 1
        except SchemaError as se:
            logger.error(f"❌ Schema error in schema for {event_key}: {se.message}")
            failed += 1

    logger.info(f"\nValidation completed: {passed}/{total} valid, {failed} failed")
    if failed:
        sys.exit(2)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python validate_config.py path/to/notification_event_config.json")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    if not config_path.exists():
        logger.error(f"File not found: {config_path}")
        sys.exit(1)

    validate_config_file(config_path)