from decimal import Decimal
from class_management.models import ClassBundleConfig
from websites.models import Website

class InvalidPricingError(Exception):
    """Raised when no price is found for the given combination."""

def get_class_price(
    program: str,
    duration: str,
    bundle_size: int,
    website: Website
) -> Decimal:
    """
    Retrieves class pricing dynamically from ClassBundleConfig in DB.

    Args:
        program (str): 'undergrad' or 'graduate'
        duration (str): e.g. '1-2', '3-4', etc.
        bundle_size (int): bundle size from 1 to 4
        website (Website): The active tenant/site

    Returns:
        Decimal: The price from the admin config

    Raises:
        InvalidPricingError: If no config is found
    """
    config = ClassBundleConfig.objects.filter(
        program=program,
        duration_range=duration,
        bundle_size=bundle_size,
        website=website
    ).first()

    if not config:
        raise InvalidPricingError(
            f"No price configured for program={program}, "
            f"duration={duration}, bundle_size={bundle_size}, "
            f"website={website.domain}"
        )

    return config.price