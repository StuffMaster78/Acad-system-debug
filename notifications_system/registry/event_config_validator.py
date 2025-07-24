import json
import os
from jsonschema import validate, ValidationError # type: ignore
from django.conf import settings

SCHEMA_PATH = os.path.join(
    settings.BASE_DIR,
    "notifications_system",
    "registry",
    "event_config_schema.json",
)

def validate_event_config(config: dict):
    with open(SCHEMA_PATH) as schema_file:
        schema = json.load(schema_file)

    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Invalid event config: {e.message}")
