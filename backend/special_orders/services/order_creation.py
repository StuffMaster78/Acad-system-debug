"""
Handles creation of special orders with optional predefined pricing.
"""

from django.db import transaction
from special_orders.models import SpecialOrder
from .pricing import calculate_predefined_price
from .installment_payment_service import InstallmentPaymentService
from .validation import validate_special_order


def create_special_order(data, user):
    """
    Creates a new special order with optional predefined pricing
    and installment generation.

    Args:
        data (dict): Dictionary of order fields to be saved.
        user (User): The client submitting the special order.

    Returns:
        SpecialOrder: The created special order instance.
    """
    # Validate the incoming order data
    validate_special_order(data)

    # Use a transaction to ensure atomicity
    with transaction.atomic():
        # Create the SpecialOrder instance
        order = SpecialOrder.objects.create(client=user, **data)

        # Apply predefined pricing if the order type is 'predefined'
        if order.order_type == 'predefined':
            order.total_cost = calculate_predefined_price(order)
            order.save()

        # Generate installments for the special order
        InstallmentPaymentService.generate_installments(order)

    return order