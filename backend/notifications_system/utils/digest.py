"""Digest helpers for summarizing notifications."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List, Dict, Any, Sequence, Union

from django.db.models import QuerySet
from django.utils.html import escape


NotificationLike = Any  # keep loose to avoid import cycles


def _safe_len(items: Union[Sequence, QuerySet]) -> int:
    """Return length without materializing a queryset."""
    if isinstance(items, QuerySet):
        return items.count()
    return len(items)


def summarize_entries(
    notifications: Union[Sequence[NotificationLike], QuerySet],
    *,
    max_items: int = 3,
    group_by_event: bool = False,
    fmt: str = "json",
) -> Union[Dict[str, Any], str]:
    """Summarize notifications for digests, grouped UIs, and emails.

    Args:
        notifications: Iterable or QuerySet of Notification-like objects.
            Each item should expose: .event, .title, .message,
            .rendered_title, .rendered_message, .rendered_link
        max_items: Maximum entries (or groups) to include.
        group_by_event: If True, aggregate by event key.
        fmt: "json", "text", or "html".

    Returns:
        Dict for "json" or a string for "text"/"html".
    """
    total = _safe_len(notifications)

    if group_by_event:
        grouped: Dict[str, List[NotificationLike]] = defaultdict(list)

        # We only need at most max_items groups for output, but
        # we must scan to build accurate counts. If performance is
        # critical, pre-aggregate in SQL and pass that in instead.
        for n in notifications:
            grouped[n.event].append(n)

        groups_out: List[Dict[str, Any]] = []
        for event, group in list(grouped.items())[:max_items]:
            first = group[0]
            groups_out.append(
                {
                    "event": event,
                    "count": len(group),
                    "title": first.rendered_title or first.title,
                    "message": first.rendered_message or first.message,
                    "link": first.rendered_link or "#",
                }
            )

        if fmt == "html":
            return _render_html(groups_out, total, grouped=True)
        if fmt == "text":
            return _render_text(groups_out, total, grouped=True)
        return {
            "count": total,
            "grouped": True,
            "items": groups_out,
            "more": total > max_items,
        }

    # Non-grouped
    if isinstance(notifications, QuerySet):
        # Avoid loading all rows when only a few are needed
        head = list(notifications[:max_items])
    else:
        head = list(notifications[:max_items])

    items = [
        {
            "event": n.event,
            "title": n.rendered_title or n.title,
            "message": n.rendered_message or n.message,
            "link": n.rendered_link or "#",
        }
        for n in head
    ]

    if fmt == "html":
        return _render_html(items, total, grouped=False)
    if fmt == "text":
        return _render_text(items, total, grouped=False)

    return {
        "count": total,
        "grouped": False,
        "items": items,
        "more": total > max_items,
    }


def _render_text(
    items: List[Dict[str, Any]], total: int, *, grouped: bool
) -> str:
    """Render a plain-text summary."""
    lines: List[str] = []
    for item in items:
        title = item.get("title") or ""
        message = item.get("message") or ""
        count = item.get("count")
        suffix = ""
        if grouped and isinstance(count, int) and count > 1:
            suffix = f" (+{count - 1} similar)"
        lines.append(f"{title}: {message}{suffix}")
    if total > len(items):
        lines.append(f"... +{total - len(items)} more")
    return "\n".join(lines)


def _render_html(
    items: List[Dict[str, Any]], total: int, grouped: bool = False
) -> str:
    """Render items as an email-safe HTML table."""
    rows: List[str] = []
    for item in items:
        title = escape(item.get("title", "") or "")
        message = escape(item.get("message", "") or "")
        link = escape(item.get("link", "#") or "#")
        count = item.get("count")

        more_html = ""
        if grouped and isinstance(count, int) and count > 1:
            more_html = (
                f"<br/><small>+{count - 1} more like this</small>"
            )

        row = (
            "<tr>"
            '<td style="padding:6px;width:6px;"></td>'
            '<td style="padding:6px;">'
            f"<strong>{title}</strong><br/>{message}{more_html}"
            "</td>"
            '<td style="padding:6px;text-align:right;">'
            f'<a href="{link}" target="_blank">View</a>'
            "</td>"
            "</tr>"
        )
        rows.append(row)

    footer = ""
    remaining = total - len(items)
    if remaining > 0:
        footer = (
            "<tr>"
            "<td colspan='3' style='text-align:right;padding:6px;'>"
            f"+{remaining} more..."
            "</td>"
            "</tr>"
        )

    table = (
        "<table style='width:100%;font-family:sans-serif;"
        "font-size:14px;border-collapse:collapse;'>"
        f"{''.join(rows)}{footer}</table>"
    )
    return table