from decimal import Decimal
from functools import lru_cache
from orders.models import PricingConfiguration, Order


@lru_cache(maxsize=1)
def get_pricing_config() -> PricingConfiguration:
    """
    Retrieves and caches the pricing configuration to avoid repeated DB hits.
    """
    config = PricingConfiguration.objects.first()
    if not config:
        raise ValueError("PricingConfiguration is not defined in the database.")
    return config


def calculate_base_price(order: Order) -> Decimal:
    """
    Calculates the base price of the order based on number of pages, slides,
    and type of work.
    
    Args:
        order (Order): The order instance.

    Returns:
        Decimal: The base price of the order.
    """
    config = get_pricing_config()

    base_price = config.base_price_per_page * order.number_of_pages
    base_price += config.base_price_per_slide * order.number_of_slides

    if order.type_of_work:
        base_price += config.base_price_per_type_of_work.get(
            order.type_of_work.id, Decimal(0)
        )

    return base_price


def calculate_extra_services_price(order: Order) -> Decimal:
    """
    Calculates the total cost of all extra services selected for the order.

    Args:
        order (Order): The order instance.

    Returns:
        Decimal: The total price of extra services.
    """
    return sum((service.price for service in order.extra_services.all()), Decimal(0))


def calculate_writer_quality_price(order: Order) -> Decimal:
    """
    Calculates the additional cost for a selected writer quality level.

    Args:
        order (Order): The order instance.

    Returns:
        Decimal: Additional price for higher-tier writer quality.
    """
    return order.writer_quality.additional_price if order.writer_quality else Decimal(0)


def calculate_urgent_price(order: Order) -> Decimal:
    """
    Calculates the additional cost for an urgent order based on deadline.

    Args:
        order (Order): The order instance.

    Returns:
        Decimal: The additional urgent fee, if applicable.
    """
    config = get_pricing_config()

    if order.is_urgent and order.deadline < config.urgent_deadline_threshold:
        return config.urgent_fee
    return Decimal(0)


def calculate_discount(order: Order) -> Decimal:
    """
    Calculates the discount applied to the order.

    Args:
        order (Order): The order instance.

    Returns:
        Decimal: The discount amount (always positive).
    """
    return order.discount.amount if order.discount else Decimal(0)


def calculate_total_price(order: Order) -> Decimal:
    """
    Aggregates all pricing components to compute the final total order price.

    Args:
        order (Order): The order instance.

    Returns:
        Decimal: The total payable price after all additions and deductions.
    """
    base = calculate_base_price(order)
    extras = calculate_extra_services_price(order)
    writer_quality = calculate_writer_quality_price(order)
    urgent_fee = calculate_urgent_price(order)
    discount = calculate_discount(order)

    return base + extras + writer_quality + urgent_fee - discount