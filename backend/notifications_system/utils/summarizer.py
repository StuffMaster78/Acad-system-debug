"""Helpers to summarize notifications for digests and UIs."""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable, List, Mapping, MutableMapping

from django.utils.html import escape

# Optional: map event key → emoji/icon for visual hints.
EVENT_ICONS: Mapping[str, str] = {
    "order.assigned": "📦",
    "order.approved": "✅",
    "order.cancelled": "❌",
    "payment.failed": "💸",
    "message.new": "💬",
    "ticket.created": "🎫",
    "account.suspended": "⛔",
}


def summarize_entries(
    notifications: Iterable,
    *,
    max_items: int = 3,
    group_by_event: bool = False,
    out_format: str = "json",
) -> Mapping:
    """Summarize notifications for digests or grouped UIs.

    Args:
        notifications: Iterable of Notification-like objects. Each item is
            expected to expose `.event`, `.title`, `.message`, and optionally
            `.rendered_title`, `.rendered_message`, `.rendered_link`.
        max_items: Maximum number of items or groups to include.
        group_by_event: If True, group items by their ``event`` key and show
            one representative row per event (with a count).
        out_format: One of ``"json"``, ``"text"``, or ``"html"``. For
            ``"html"`` this returns a safe HTML table string suitable for
            emails.

    Returns:
        Mapping or str: A JSON-like dict summary, or a formatted string for
        ``"text"``/``"html"`` outputs.
    """
    items: List = list(notifications)
    total = len(items)

    if group_by_event:
        grouped: MutableMapping[str, List] = defaultdict(list)
        for n in items:
            grouped[getattr(n, "event", "unknown")].append(n)

        rows = []
        for event, group in list(grouped.items())[:max_items]:
            first = group[0]
            rows.append(
                {
                    "event": event,
                    "icon": EVENT_ICONS.get(event, ""),
                    "count": len(group),
                    "title": getattr(first, "rendered_title", None)
                    or getattr(first, "title", ""),
                    "message": getattr(first, "rendered_message", None)
                    or getattr(first, "message", ""),
                    "link": getattr(first, "rendered_link", None) or "#",
                }
            )

        if out_format == "html":
            return _render_html(rows, total, grouped=True)
        if out_format == "text":
            return "\n".join(
                _text_line(r["icon"], r["title"], r["message"]) for r in rows
            )
        return {
            "count": total,
            "grouped": True,
            "items": rows,
            "more": total > max_items,
        }

    rows = [
        {
            "event": getattr(n, "event", "unknown"),
            "icon": EVENT_ICONS.get(getattr(n, "event", "unknown"), ""),
            "title": getattr(n, "rendered_title", None)
            or getattr(n, "title", ""),
            "message": getattr(n, "rendered_message", None)
            or getattr(n, "message", ""),
            "link": getattr(n, "rendered_link", None) or "#",
        }
        for n in items[:max_items]
    ]

    if out_format == "html":
        return _render_html(rows, total, grouped=False)
    if out_format == "text":
        return "\n".join(_text_line(r["icon"], r["title"], r["message"])
                         for r in rows)

    return {
        "count": total,
        "grouped": False,
        "items": rows,
        "more": total > max_items,
    }


def _text_line(icon: str, title: str, message: str) -> str:
    """Build a single line for plaintext summaries."""
    icon_part = f"{icon} " if icon else ""
    return f"{icon_part}{title}: {message}"


def _render_html(items: List[Mapping], total: int, *, grouped: bool) -> str:
    """Render items as an email-safe HTML table.

    Args:
        items: Rows to render (already summarized dicts).
        total: Total number of original notifications.
        grouped: Whether the rows represent grouped events.

    Returns:
        str: HTML table markup (no external CSS).
    """
    rows_html: List[str] = []
    for r in items:
        icon = escape(r.get("icon", ""))
        title = escape(r.get("title", "") or "")
        message = escape(r.get("message", "") or "")
        link = escape(r.get("link", "#") or "#")
        count = r.get("count")
        extra = ""
        if grouped and isinstance(count, int) and count > 1:
            extra = f"<br/><small>+{count - 1} more like this</small>"
        rows_html.append(
            (
                "<tr>"
                "<td style='padding:6px;'>{icon}</td>"
                "<td style='padding:6px;'>"
                "<strong>{title}</strong><br/>{message}{extra}"
                "</td>"
                "<td style='padding:6px;'>"
                "<a href='{link}' target='_blank'>View</a>"
                "</td>"
                "</tr>"
            ).format(icon=icon, title=title, message=message, extra=extra,
                     link=link)
        )

    more_html = ""
    if total > len(items):
        more_html = (
            "<tr>"
            "<td colspan='3' style='text-align:right;'>"
            f"+{total - len(items)} more..."
            "</td>"
            "</tr>"
        )

    return (
        "<table style='width:100%;font-family:sans-serif;"
        "font-size:14px;border-collapse:collapse;'>"
        f"{''.join(rows_html)}"
        f"{more_html}"
        "</table>"
    )