from django.apps import apps
from decimal import Decimal
from functools import lru_cache
from discounts.models import Discount
from discounts.services.engine import DiscountEngine  # Import the discount engine
from django.core.exceptions import ValidationError

class PricingCalculatorService:
    """
    Service to calculate pricing components and final price for orders.
    Handles base price, extras, writer quality, urgent fees, discounts, 
    and applies discount codes with validation.
    """

    @lru_cache(maxsize=1)
    def get_pricing_config():
        """
        Retrieves and caches the pricing configuration to avoid repeated DB hits.
        """
        PricingConfiguration = apps.get_model("orders", "PricingConfiguration")
        config = PricingConfiguration.objects.first()
        if not config:
            raise ValueError("PricingConfiguration is not defined in the database.")
        return config


    def calculate_base_price(order_id) -> Decimal:
        """
        Calculates the base price of the order based on number of pages, slides,
        and type of work.
        
        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The base price of the order.
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        config = PricingCalculatorService.get_pricing_config()

        base_price = config.base_price_per_page * order.number_of_pages
        base_price += config.base_price_per_slide * order.number_of_slides

        if order.type_of_work:
            base_price += config.base_price_per_type_of_work.get(
                order.type_of_work.id, Decimal(0)
            )

        return base_price


    def calculate_extra_services_price(order_id) -> Decimal:
        """
        Calculates the total cost of all extra services selected for the order.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The total price of extra services.
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        return sum((service.price for service in order.extra_services.all()), Decimal(0))


    def calculate_writer_quality_price(order_id) -> Decimal:
        """
        Calculates the additional cost for a selected writer quality level.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: Additional price for higher-tier writer quality.
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        return order.writer_quality.additional_price if order.writer_quality else Decimal(0)


    def calculate_urgent_price(order_id) -> Decimal:
        """
        Calculates the additional cost for an urgent order based on deadline.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The additional urgent fee, if applicable.
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        config = PricingCalculatorService.get_pricing_config()

        if order.is_urgent and order.deadline < config.urgent_deadline_threshold:
            return config.urgent_fee
        return Decimal(0)


    def calculate_discount(order_id) -> Decimal:
        """
        Calculates the discount applied to the order.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The discount amount (always positive).
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        return order.discount.amount if order.discount else Decimal(0)


    # orders/services/calculate_additional_cost.py

    def calculate_additional_cost(order, discount_codes=None):
        """
        Calculate the additional cost for the order based on page count, slide count,
        extra services, and applicable discounts.

        Args:
            order (Order): The order object containing the details of the order.
            discount_codes (list): List of discount codes to apply.

        Returns:
            float: The additional cost to be paid by the client after applying discounts.
        """
        # Fetch the relevant prices per unit (these might be attributes of the Order or related models)
        page_price = order.page_price  # Price per page
        slide_price = order.slide_price  # Price per slide

        # Calculate the total cost for additional pages and slides
        additional_pages_cost = order.additional_pages * page_price if order.additional_pages else 0
        additional_slides_cost = order.additional_slides * slide_price if order.additional_slides else 0

        # Calculate the cost for extra services
        extra_services_cost = sum(service.service_cost for service in order.extra_services.all())

        # Base total additional cost
        total_additional_cost = additional_pages_cost + additional_slides_cost + extra_services_cost

        # Apply discount if any codes are provided
        if discount_codes:
            discount_engine = DiscountEngine(
                discount_codes=discount_codes,
                order=order,
                website=order.website,
                user=order.user
            )
            try:
                applied_discounts = discount_engine.apply_discounts()
                total_additional_cost = order.total_after_discounts  # Discounted price after applying all valid discounts
            except ValidationError as e:
                # Handle any validation errors if discount codes are invalid
                raise ValidationError(f"Error applying discounts: {str(e)}")

        return total_additional_cost

    @staticmethod
    def calculate_preferred_writer_fee(order) -> Decimal:
        """
        Calculate the additional fee for the preferred writer assigned to the order.

        Args:
            order (Order): The order instance to calculate the fee for.

        Returns:
            Decimal: The additional fee for the preferred writer if assigned,
                    otherwise Decimal(0).
        """
        if order.preferred_writer:
            return order.preferred_writer.additional_fee
        return Decimal(0)

    def calculate_total_price(order_id) -> Decimal:
        """
        Aggregates all pricing components to compute the final total order price.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The total payable price after all additions and deductions.
        """
        Order = apps.get_model("orders", "Order")
        order = Order.objects.get(id=order_id)
        base = PricingCalculatorService.calculate_base_price(order)
        extras = PricingCalculatorService.calculate_extra_services_price(order)
        writer_quality = PricingCalculatorService.calculate_writer_quality_price(order)
        urgent_fee = PricingCalculatorService.calculate_urgent_price(order)
        preferred_writer_fee = PricingCalculatorService.calculate_preferred_writer_fee(order)
        discount = PricingCalculatorService.calculate_discount(order)

        return base + extras + writer_quality + preferred_writer_fee + urgent_fee - discount