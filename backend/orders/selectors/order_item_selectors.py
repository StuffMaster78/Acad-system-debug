"""
Selectors for order items.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from orders.models.orders.order import Order
from orders.models.orders.order_item import OrderItem


def get_order_items(*, order: Order) -> QuerySet[OrderItem]:
    """
    Return ordered items for a given order.
    """
    return OrderItem.objects.filter(
        order=order,
        website=order.website,
    ).order_by("sort_order", "id")


def get_order_item_by_id(
    *,
    order: Order,
    item_id: int,
) -> OrderItem:
    """
    Return one order item scoped to the provided order.
    """
    try:
        return OrderItem.objects.get(
            id=item_id,
            order=order,
            website=order.website,
        )
    except OrderItem.DoesNotExist as exc:
        raise ValidationError(
            {"item_id": "Order item not found."}
        ) from exc


def get_order_items_for_website(*, website) -> QuerySet[OrderItem]:
    """
    Return all order items for a website.
    """
    return OrderItem.objects.filter(
        website=website,
    ).select_related(
        "order",
        "pricing_snapshot",
    ).order_by("-created_at")


def get_composite_order_items(*, website) -> QuerySet[OrderItem]:
    """
    Return order items belonging to composite orders for a website.
    """
    return OrderItem.objects.filter(
        website=website,
        order__is_composite=True,
    ).select_related(
        "order",
        "pricing_snapshot",
    ).order_by("-created_at")


def get_order_items_by_service_family(
    *,
    website,
    service_family: str,
) -> QuerySet[OrderItem]:
    """
    Return order items filtered by service family.
    """
    return OrderItem.objects.filter(
        website=website,
        service_family=service_family,
    ).select_related(
        "order",
        "pricing_snapshot",
    ).order_by("-created_at")


def get_order_items_by_service_code(
    *,
    website,
    service_code: str,
) -> QuerySet[OrderItem]:
    """
    Return order items filtered by service code.
    """
    return OrderItem.objects.filter(
        website=website,
        service_code=service_code,
    ).select_related(
        "order",
        "pricing_snapshot",
    ).order_by("-created_at")