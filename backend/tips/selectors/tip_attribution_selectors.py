from __future__ import annotations

from typing import Any

from tips.models.tip_attribution import TipAttribution


def get_attribution_by_tip(*, tip_id: int) -> TipAttribution | None:
    """
    Fetch attribution metadata for a tip.
    """
    return (
        TipAttribution.objects
        .select_related("tip")
        .filter(tip_id=tip_id)
        .first()
    )


def get_tips_by_context(*, context_type: str):
    """
    Tips grouped by contextual origin.

    Example:
        - "assignment"
        - "profile"
        - "direct_message"
    """
    return (
        TipAttribution.objects
        .select_related("tip", "tip__sender", "tip__receiver")
        .filter(context_type=context_type)
    )