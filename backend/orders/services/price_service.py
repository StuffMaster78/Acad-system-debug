from orders.services.pricing_calculator import calculate_total_price
from discounts.models import Discount
from decimal import Decimal
from django.core.exceptions import ValidationError

class PriceService:
    """Handles pricing updates and flow orchestration."""

    @staticmethod
    def update_total_price(order):
        """Recalculate and persist the total price."""
        order.total_cost = calculate_total_price(order)
        order.save(update_fields=["total_cost"])

    @staticmethod
    def apply_discount(order, discount_code: str):
        """Apply a discount code and trigger price update."""
        discount = Discount.objects.get(code=discount_code)

        if not discount.is_valid(order.user):
            raise ValidationError("Discount is not valid for this order.")

        order.discount = discount
        PriceService.update_total_price(order)

    @staticmethod
    def add_pages(order, additional_pages: int):
        """Add pages and update price."""
        order.number_of_pages += additional_pages
        PriceService.update_total_price(order)

    @staticmethod
    def add_slides(order, additional_slides: int):
        """Add slides and update price."""
        order.number_of_slides += additional_slides
        PriceService.update_total_price(order)

    @staticmethod
    def add_extra_service(order, service):
        """Attach an extra service and update total price."""
        order.extra_services.add(service)
        PriceService.update_total_price(order)

    @staticmethod
    def add_discount(order, discount):
        """Manually attach a discount and update price."""
        order.discount = discount
        PriceService.update_total_price(order)



# Axe Out 