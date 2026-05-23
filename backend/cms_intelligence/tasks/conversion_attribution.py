"""
Conversion Attribution
========================

Computes content attribution for completed orders using four models:
- first_touch: 100% credit to the first content page in the visitor's session
- last_touch: 100% credit to the last content page before the order form
- linear: equal credit across all pages in the path
- position_based: 40% first, 40% last, 20% distributed across middle

Attribution is computed from PageView session data (cms_engagement).

Celery beat::

    "compute-conversion-attribution": {
        "task": "cms_intelligence.tasks.conversion_attribution.compute_attribution",
        "schedule": crontab(hour=6, minute=0),
    }
"""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

logger = logging.getLogger(__name__)

ATTRIBUTION_MODELS = ["first_touch", "last_touch", "linear", "position_based"]


@shared_task
def compute_attribution():
    """Compute attribution for all orders completed in the last 48 hours."""
    from django.apps import apps

    try:
        Order = apps.get_model("orders", "Order")
    except LookupError:
        logger.warning("orders.Order model not found — skipping attribution")
        return {"error": "orders app not installed"}

    cutoff = timezone.now() - timedelta(hours=48)

    # Get completed orders not yet attributed
    from cms_intelligence.models import ConversionAttribution

    attributed_order_ids = set(
        ConversionAttribution.objects.values_list("order_id", flat=True).distinct()
    )

    recent_orders = Order.objects.filter(
        status="completed",
        completed_at__gte=cutoff,
    ).exclude(id__in=attributed_order_ids)

    orders_processed = 0
    for order in recent_orders.iterator(chunk_size=50):
        try:
            _attribute_order(order)
            orders_processed += 1
        except Exception as exc:
            logger.error("Attribution failed for order %s: %s", order.id, exc)

    logger.info("Attribution computed for %d orders", orders_processed)
    return {"orders_processed": orders_processed}


def _attribute_order(order):
    """Build the content path and compute all four attribution models."""
    from cms_engagement.models import PageView
    from cms_intelligence.models import ConversionAttribution

    # Get the visitor's session — try to find the session that led to this order
    # Look for the user's pageviews in the 24 hours before the order
    user = getattr(order, "client", None) or getattr(order, "user", None)
    website = getattr(order, "website", None)

    if not user:
        return

    cutoff = order.completed_at - timedelta(hours=24) if hasattr(order, "completed_at") else timezone.now() - timedelta(hours=24)

    # Get all page views by this user in the attribution window
    views = PageView.objects.filter(
        user=user,
        created_at__gte=cutoff,
        created_at__lte=order.completed_at if hasattr(order, "completed_at") else timezone.now(),
    ).order_by("created_at")

    if not views.exists():
        # Try session-based matching if no user is set
        return

    # Build the content path — deduplicate consecutive same-page views
    path = []
    last_key = None
    for view in views:
        key = (view.content_type_id, view.object_id)
        if key != last_key and view.content_type_id and view.object_id:
            path.append({
                "content_type_id": view.content_type_id,
                "object_id": view.object_id,
                "position": len(path) + 1,
            })
            last_key = key

    if not path:
        return

    path_length = len(path)
    order_value = float(getattr(order, "total_price", 0) or getattr(order, "amount", 0) or 0)

    # Compute each attribution model
    for model_name in ATTRIBUTION_MODELS:
        credits = _compute_credits(path, model_name)

        for entry in path:
            credit = credits.get(entry["position"], 0.0)
            if credit <= 0:
                continue

            ConversionAttribution.objects.create(
                order=order,
                content_type_id=entry["content_type_id"],
                object_id=entry["object_id"],
                attribution_model=model_name,
                credit_share=round(credit, 4),
                attributed_revenue=round(order_value * credit, 2),
                path_position=entry["position"],
                path_length=path_length,
            )


def _compute_credits(path: list[dict], model: str) -> dict[int, float]:
    """Compute credit shares for each position in the path."""
    n = len(path)
    if n == 0:
        return {}

    credits = {}

    if model == "first_touch":
        for entry in path:
            credits[entry["position"]] = 1.0 if entry["position"] == 1 else 0.0

    elif model == "last_touch":
        for entry in path:
            credits[entry["position"]] = 1.0 if entry["position"] == n else 0.0

    elif model == "linear":
        share = 1.0 / n
        for entry in path:
            credits[entry["position"]] = share

    elif model == "position_based":
        if n == 1:
            credits[1] = 1.0
        elif n == 2:
            credits[1] = 0.5
            credits[2] = 0.5
        else:
            middle_share = 0.2 / (n - 2) if n > 2 else 0
            for entry in path:
                pos = entry["position"]
                if pos == 1:
                    credits[pos] = 0.4
                elif pos == n:
                    credits[pos] = 0.4
                else:
                    credits[pos] = middle_share

    return credits
