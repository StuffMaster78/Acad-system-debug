import json
import jsonschema # type: ignore
from jsonschema import validate, ValidationError # type: ignore

def validate_event_config(config, schema_path) -> None:
    with open(schema_path) as f:
        schema = json.load(f)

    for key, event in config.items():
        try:
            validate(instance=event, schema=schema)
        except ValidationError as e:
            raise ValueError(f"Validation failed for event '{key}': {e.message}")
        
    print("All events validated successfully.")
    return None

def validate_event_config(config: dict, schema_path: str):
    with open(schema_path) as f:
        schema = json.load(f)
    jsonschema.validate(instance=config, schema=schema)


def get_schema(schema_path: str) -> dict:
    """
    Load and return the JSON schema from the given path.
    
    Args:
        schema_path (str): Path to the JSON schema file.
    
    Returns:
        dict: Loaded JSON schema.
    """
    with open(schema_path, 'r', encoding='utf-8') as f:
        return json.load(f)