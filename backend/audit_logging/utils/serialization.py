from typing import Any


def safe_serialize(value: Any) -> Any:
    """
    Ensures audit metadata is JSON-safe.
    """

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {k: safe_serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [safe_serialize(v) for v in value]

    # fallback for models/objects
    return str(value)