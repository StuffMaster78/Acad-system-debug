from collections import defaultdict
from django.utils.html import escape
from notifications_system.enums import EventType

# Optional: Map event → icon or emoji for visual hints
EVENT_ICONS = {
    EventType.ORDER_ASSIGNED: "📦",
    EventType.ORDER_APPROVED: "✅",
    EventType.ORDER_CANCELLED: "❌",
    EventType.PAYMENT_FAILED: "💸",
    EventType.NEW_MESSAGE: "💬",
    EventType.TICKET_CREATED: "🎫",
    EventType.ACCOUNT_SUSPENDED: "⛔",
    # ... add more as needed
}

def summarize_entries(notifications, max=3, group_by_event=False, format="json"):
    """
    Summarize notification entries for digests, grouped UIs, and emails.

    Args:
        notifications: list or queryset of Notification objects
        max: maximum entries to include
        group_by_event: whether to group entries by event type
        format: "json", "text", or "html"

    Returns:
        dict or str: formatted summary
    """
    total = len(notifications)

    if group_by_event:
        grouped = defaultdict(list)
        for n in notifications:
            grouped[n.event].append(n)

        result = []
        for event, group in list(grouped.items())[:max]:
            icon = EVENT_ICONS.get(event, "")
            first = group[0]
            result.append({
                "event": event,
                "icon": icon,
                "count": len(group),
                "title": first.rendered_title or first.title,
                "message": first.rendered_message or first.message,
                "link": first.rendered_link or "#"
            })

        if format == "html":
            return _render_html(result, total, grouped=True)
        return {
            "count": total,
            "grouped": True,
            "items": result,
            "more": total > max
        }

    # Non-grouped version
    items = [
        {
            "event": n.event,
            "icon": EVENT_ICONS.get(n.event, ""),
            "title": n.rendered_title or n.title,
            "message": n.rendered_message or n.message,
            "link": n.rendered_link or "#"
        }
        for n in notifications[:max]
    ]

    if format == "html":
        return _render_html(items, total)
    elif format == "text":
        return "\n".join(
            f"{item['icon']} {item['title']}: {item['message']}"
            for item in items
        )

    return {
        "count": total,
        "grouped": False,
        "items": items,
        "more": total > max
    }


def _render_html(items, total, grouped=False):
    """
    Renders items as an HTML table (email-safe).
    """
    rows = []
    for item in items:
        icon = escape(item.get("icon", ""))
        title = escape(item.get("title", ""))
        message = escape(item.get("message", ""))
        link = escape(item.get("link", "#"))
        count = item.get("count", None)

        row = f"""
        <tr>
            <td style="padding: 6px;">{icon}</td>
            <td style="padding: 6px;">
                <strong>{title}</strong><br/>
                {message}
                {"<br/><small>+" + str(count - 1) + " more like this</small>" if grouped and count and count > 1 else ""}
            </td>
            <td style="padding: 6px;">
                <a href="{link}" target="_blank">View</a>
            </td>
        </tr>
        """
        rows.append(row)

    return f"""
    <table style="width: 100%; font-family: sans-serif; font-size: 14px; border-collapse: collapse;">
        {"".join(rows)}
        {"<tr><td colspan='3' style='text-align:right;'>+{} more...</td></tr>".format(total - len(items)) if total > len(items) else ""}
    </table>
    """