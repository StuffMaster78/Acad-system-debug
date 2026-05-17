import hashlib
import json


def generate_idempotency_key(*args, **kwargs) -> str:
    """
    Creates a deterministic idempotency key.
    """

    raw = json.dumps(
        {
            "args": args,
            "kwargs": kwargs,
        },
        sort_keys=True,
    )

    return hashlib.sha256(raw.encode()).hexdigest()