"""
Generic code generation utility.

Use this for generating unique codes across any model + field combo.
"""

import secrets
import string

from django.db.models import Model


def generate_unique_discount_code(
    model: type[Model],
    field: str = "code",
    prefix: str = "",
    length: int = 10,
    max_attempts: int = 10,
    charset: str = string.ascii_uppercase + string.digits
) -> str:
    """
    Generate a secure, unique discount code for a given model and field.
    
    Args:
        model: Django model class to check uniqueness against.
        field: The model field name to validate uniqueness on.
        prefix: Optional prefix to prepend to the code (e.g., "SPRING").
        length: Number of random characters (excluding prefix).
        max_attempts: Retry attempts before giving up.
        charset: Characters to use for the random part of the code.

    Returns:
        A unique discount code as a string.

    Raises:
        RuntimeError: If unique code generation fails after max_attempts.
    """
    for _ in range(max_attempts):
        # Generate a secure random code
        code = prefix + ''.join(secrets.choice(charset) for _ in range(length))
        lookup = {field: code}
        if not model.objects.filter(**lookup).exists():
            return code  # Code is unique
    raise RuntimeError(f"Failed to generate a unique discount code after {max_attempts} attempts.")


def get_discount_model():
    """
    Get the Discount model class.
    
    Returns:
        Discount model class.
    """
    from discounts.models import Discount
    return Discount

def get_discount_usage_model():
    """
    Get the DiscountUsage model class.
    
    Returns:
        DiscountUsage model class.
    """
    from discounts.models import DiscountUsage
    return DiscountUsage

def get_discount_config():
    """
    Get the DiscountConfig model instance.
    Returns:
        DiscountConfig model instance.
    """
    from models.discount_configs import DiscountConfig
    return DiscountConfig.objects.first()