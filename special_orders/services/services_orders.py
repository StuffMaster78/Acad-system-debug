from django.core.exceptions import PermissionDenied
from special_orders.models import SpecialOrder
import logging
from special_orders.models import EstimatedSpecialOrderSettings

logger = logging.getLogger("special_orders")

def approve_order(special_order, user):
    """
    Approve a special order. Only staff can approve.
    """
    if not user.is_staff:
        raise PermissionDenied("Only admins can approve orders.")
    if not special_order.is_approved:
        special_order.is_approved = True
        special_order.save()
        logger.info(
            f"Special order #{special_order.id} approved successfully."
        )
    return special_order


def override_payment(special_order: SpecialOrder, user):
    """
    Manually mark a special order as paid. Only staff allowed.
    """
    if not user.is_staff:
        raise PermissionDenied(
            "Only admins can override payment."
        )
    if not special_order.admin_marked_paid:
        special_order.admin_marked_paid = True
        special_order.save()
        logger.info(
            f"Payment overridden for special order #{special_order.id}."
        )
    return special_order


def complete_order(special_order, user):
    """
    Mark an order as completed. Admins or clients can do this.
    """
    if not user.is_staff and special_order.client != user:
        raise PermissionDenied("Not authorized to complete this order.")
    special_order.status = 'completed'
    special_order.save()
    return special_order


def calculate_special_order_payment(special_order: SpecialOrder) -> dict:
    """
    Calculate payment details for a special order based on its type.
    """
    if special_order.order_type == 'predefined' and special_order.predefined_type:
        duration_price = special_order.predefined_type.durations.filter(
            duration_days=special_order.duration_days
        ).first()
        if not duration_price:
            raise ValueError("Invalid duration for selected predefined order type.")
        return {
            'total_cost': duration_price.price,
            'deposit_required': duration_price.price  # Full payment upfront
        }

    elif special_order.order_type == 'estimated':
        if special_order.total_cost is None or special_order.deposit_required is None:
            raise ValueError("Estimated orders require total_cost and deposit.")
        return {
            'total_cost': special_order.total_cost,
            'deposit_required': special_order.deposit_required
        }

    raise ValueError("Unsupported or incomplete special order configuration.")

def get_deposit_percentage(website):
    """
    Get the deposit percentage for estimated special orders for a specific website.
    Returns a default of 50% if no setting is found for the website.

    Args:
        website: The website for which to fetch the deposit percentage.

    Returns:
        Decimal: The deposit percentage for the website.
    """
    try:
        return (
            EstimatedSpecialOrderSettings.objects
            .get(website=website).default_deposit_percentage
        )
    except EstimatedSpecialOrderSettings.DoesNotExist:
        return 50  # fallback default