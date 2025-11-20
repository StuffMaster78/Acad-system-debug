"""
Handles price calculation logic for predefined orders.
"""

def calculate_predefined_price(order):
    """
    Returns the price based on the predefined type and duration.

    Args:
        order (SpecialOrder): The special order to calculate the price for.

    Returns:
        float: The calculated price for the predefined order.

    Raises:
        ValueError: If no duration is found for the specified predefined type.
    """
    duration_obj = order.predefined_type.durations.filter(
        duration_days=order.duration_days
    ).first()

    if not duration_obj:
        raise ValueError("Invalid duration for predefined type.")

    return duration_obj.price