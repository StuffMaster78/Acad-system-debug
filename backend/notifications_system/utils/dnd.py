"""Do-not-disturb helpers."""

from __future__ import annotations

from datetime import time
from typing import Optional


def is_dnd_now(profile: Optional[object]) -> bool:
    """Return True if user's DND window is active right now.

    Args:
        profile: Object with optional fields:
            - dnd_enabled (bool)
            - dnd_start (datetime.time)
            - dnd_end (datetime.time)

    Returns:
        bool: Whether we are inside the DND window.

    Notes:
        Handles overnight windows (e.g., 22:00 - 07:00).
        If profile is missing or disabled, returns False.
    """
    if not profile or not getattr(profile, "dnd_enabled", False):
        return False

    start: Optional[time] = getattr(profile, "dnd_start", None)
    end: Optional[time] = getattr(profile, "dnd_end", None)
    if not start or not end:
        return False

    now_t = getattr(profile, "now_time", None)
    # Allow tests to inject a clock via profile.now_time
    now_t = now_t() if callable(now_t) else now_t
    if now_t is None:
        # Late import to avoid Django at import time
        from django.utils import timezone
        now_t = timezone.localtime().time()

    if start <= end:
        # Normal window (e.g., 21:00–23:00)
        return start <= now_t <= end

    # Overnight window (e.g., 22:00–07:00)
    return now_t >= start or now_t <= end
