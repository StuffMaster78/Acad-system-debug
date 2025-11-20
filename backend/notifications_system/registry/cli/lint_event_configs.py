import os
import json
import argparse
from jsonschema import validate, ValidationError
from notifications_system.registry.validator import get_schema
from notifications_system.registry.event_config_loader import load_all_configs

CONFIG_DIR = "notifications_system/registry/config"
SCHEMA_DIR = f"{CONFIG_DIR}/schemas"
CONFIG_FILE = f"{CONFIG_DIR}/notification_event_config.json"

def main():
    try:
        load_all_configs()
        print("✅ All notification + broadcast configs are valid.")
    except Exception as e:
        print(f"❌ Config validation failed: {e}")

def lint(config_path, schema_path):
    with open(config_path) as f:
        config = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)

    errors = []
    for event_key, event_data in config.items():
        try:
            validate(instance=event_data, schema=schema)
            print(f"✅ Valid: {event_key}")
        except ValidationError as e:
            print(f"❌ Invalid: {event_key}")
            print(f"    ↪ {e.message}")
            errors.append((event_key, e.message))
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", default=f"{SCHEMA_DIR}/base_event.schema.json")
    parser.add_argument("--config", default=CONFIG_FILE)
    args = parser.parse_args()
    lint(args.config, args.schema)