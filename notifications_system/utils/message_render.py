"""Digest email rendering utilities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from django.template.loader import render_to_string


def render_digest_email(digest: Any) -> str:
    """Render a digest into HTML for email.

    Args:
        digest: An object representing a digest, typically a model instance
            with attributes like ``user``, ``items`` (related manager or
            sequence), and optional ``summary``.

    Returns:
        str: Rendered HTML for the digest email.
    """
    items: List[Any] = []
    if hasattr(digest, "items"):
        try:
            # Support related manager (e.g., digest.items.all())
            items = list(digest.items.all())
        except Exception:
            # Fallback when ``items`` is already a list/iterable
            items = list(getattr(digest, "items", []) or [])

    context: Dict[str, Optional[Any]] = {
        "user": getattr(digest, "user", None),
        "digest": digest,
        "items": items,
        "summary": getattr(digest, "summary", None),
    }

    # Match your repo path: templates/notifications/emails/digest_email.html
    return render_to_string(
        "notifications/emails/digest_email.html",
        context,
    )