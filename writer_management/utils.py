from django.utils import timezone
from orders.models import Order
from users.models import User  # Assuming writers are Users
from django.db.models import Count, Avg, Q


def get_available_writer_for_order(order, max_active_orders=5, min_rating=4.0):
    """
    Fetches an available writer suitable for the given order.
    
    Criteria:
        - Not overloaded (below `max_active_orders`)
        - Has a rating >= `min_rating`
        - Not currently suspended or deactivated
        - Not the one requesting reassignment (if writer-initiated)

    Args:
        order (Order): The order needing a writer.
        max_active_orders (int): Max concurrent orders a writer can have.
        min_rating (float): Minimum average rating to be considered.

    Returns:
        User: Best-matched writer, or None if none found.
    """
    # Optionally avoid assigning to the current writer if reassignment
    excluded_writer_ids = []

    if order.assigned_writer:
        excluded_writer_ids.append(order.assigned_writer.id)

    # Get writer stats (customize to your schema)
    qualified_writers = (
        User.objects.filter(is_writer=True, is_active=True)
        .exclude(id__in=excluded_writer_ids)
        .annotate(
            active_orders=Count('orders_assigned', filter=Q(orders_assigned__status__in=["in_progress", "revision"])),
            avg_rating=Avg('orders_assigned__rating')
        )
        .filter(
            active_orders__lt=max_active_orders,
            avg_rating__gte=min_rating
        )
        .order_by('-avg_rating', 'active_orders')  # Prefer best-rated, least loaded
    )

    return qualified_writers.first()



class WebhookPayloadFormatter:
    """
    Formats webhook payloads for different platforms (Slack, Discord, etc).
    """

    @staticmethod
    def format(event_type, payload, platform):
        if platform.lower() == "slack":
            return WebhookPayloadFormatter._format_slack(event_type, payload)
        elif platform.lower() == "discord":
            return WebhookPayloadFormatter._format_discord(event_type, payload)
        else:
            return payload  # raw fallback

    @staticmethod
    def _format_slack(event_type, payload):
        order = payload.get("order", {})
        return {
            "text": f"*{event_type.replace('_', ' ').title()}*\n"
                    f"Order #{order.get('id')} - {order.get('title')}\n"
                    f"Status: `{order.get('status')}`\n"
                    f"<{payload.get('order_url', '')}|View Order>",
        }

    @staticmethod
    def _format_discord(event_type, payload):
        order = payload.get("order", {})
        return {
            "embeds": [
                {
                    "title": f"{event_type.replace('_', ' ').title()}",
                    "description": (
                        f"**Order #{order.get('id')}** - {order.get('title')}\n"
                        f"Status: `{order.get('status')}`"
                    ),
                    "url": payload.get("order_url", ""),
                    "color": 0x00ff99,
                }
            ]
        }