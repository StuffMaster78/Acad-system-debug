"""
Houses input and business rule validations for special orders.
"""

def validate_special_order(data):
    """
    Validates input before creating a special order.

    Args:
        data (dict): The data for the special order to validate.

    Raises:
        ValueError: If any validation checks fail.
    """
    if data["order_type"] == "predefined" and not data.get("predefined_type"):
        raise ValueError("Predefined order type requires a configuration.")

    if data["duration_days"] < 1:
        raise ValueError("Duration must be at least 1 day.")