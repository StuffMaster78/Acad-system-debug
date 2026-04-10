from __future__ import annotations

from uuid import uuid4


def generate_payment_reference(prefix: str = "pay") -> str:
    """
    Generate a unique internal payment reference.
    """
    return f"{prefix}_{uuid4().hex[:20]}"