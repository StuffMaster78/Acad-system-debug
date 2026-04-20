"""
Deadline and urgency validators for the order_pricing_core app.
"""

from __future__ import annotations


def get_recommended_deadline_hours(
    *,
    pages: int,
    max_pages_per_hour: int,
    extra_hour_per_extra_page: int,
) -> int:
    """
    Return the recommended minimum deadline hours for a page count.
    """
    if pages <= 0:
        return 0

    if max_pages_per_hour <= 0:
        return pages

    base_hours = pages // max_pages_per_hour
    remainder = pages % max_pages_per_hour

    recommended = base_hours
    if remainder:
        recommended += extra_hour_per_extra_page

    if recommended <= 0:
        return pages

    return recommended


def deadline_is_tight(
    *,
    pages: int,
    deadline_hours: int,
    max_pages_per_hour: int,
) -> bool:
    """
    Return whether the selected deadline is tight for the page count.
    """
    if max_pages_per_hour <= 0:
        return pages > deadline_hours
    return pages > (deadline_hours * max_pages_per_hour)