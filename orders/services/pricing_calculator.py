from django.apps import apps
from decimal import Decimal
from functools import lru_cache
from discounts.services.discount_engine import DiscountEngine  # Import the discount engine
from django.core.exceptions import ValidationError

class PricingCalculatorService:
    """
    Service to calculate pricing components and final price for orders.
    Handles base price, extras, writer quality, urgent fees, discounts, 
    and applies discount codes with validation.
    """

    def __init__(self, order):
        self.order = order
        self.website = order.website
        self.config = self.get_pricing_config()

    @staticmethod
    @lru_cache(maxsize=32)
    def get_pricing_config_for_website(website_id):
        """
        Retrieves and caches the pricing configuration to avoid repeated DB hits.
        """
        PricingConfiguration = apps.get_model(
            "orders", "PricingConfiguration"
        )

        config = PricingConfiguration.objects.filter(
            website_id=website_id
        ).latest("created_at")

        if not config:
            raise ValueError("PricingConfiguration is not defined in the database.")
        
        return config

    def get_pricing_config(self):
        """
        Retrieves the latest pricing configuration for the website associated with the order.
        This method uses caching to optimize performance by avoiding repeated database queries.
        """
        return self.get_pricing_config_for_website(self.website.id)

    def calculate_base_price(self) -> Decimal:
        """
        Calculates the base price of the order based on number of pages, slides,
        and type of work.
        
        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The base price of the order.
        """
        return (
            self.config.base_price_per_page * self.order.number_of_pages +
            self.config.base_price_per_slide * self.order.number_of_slides
        )


    def calculate_extra_services_price(self) -> Decimal:
        """
        Calculates the total cost of all extra services selected for the order.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The total price of extra services.
        """
        return sum(
            (service.service_cost for service in self.order.extra_services.all()),
            Decimal(0)
        )


    def calculate_writer_quality_price(self) -> Decimal:
        """
        Calculates the additional cost for a selected writer quality level.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: Additional price for higher-tier writer quality.
        """
        if self.order.writer_quality:
            return self.order.writer_quality.additional_price
        return Decimal(0)
    
    def calculate_preferred_writer_fee(self) -> Decimal:
        """
        Calculates the additional fee for the preferred writer assigned to the order.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: Additional fee for the preferred writer.
        """
        if self.order.preferred_writer:
            return self.order.preferred_writer.additional_fee
        return Decimal(0)


    def calculate_urgent_price(self) -> Decimal:
        """
        Calculates the additional cost for an urgent order based on deadline.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The additional urgent fee, if applicable.
        """
        if (
            self.order.is_urgent and
            self.order.deadline and
            self.order.deadline < self.config.urgent_order_threshold
        ):
            return self.config.urgent_fee
        return Decimal(0)


    def calculate_discount(self) -> Decimal:
        """
        Calculates the discount applied to the order.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The discount amount (always positive).
        """
        if self.order.discount:
            return self.order.discount.amount

        return Decimal(0)


    def apply_discount_engine(self, codes=None) -> Decimal:
        """
        Optional: use discount engine to apply codes dynamically.
        """
        if not codes:
            return Decimal(0)

        discount_engine = DiscountEngine(
            discount_codes=codes,
            order=self.order,
            website=self.website,
            user=self.order.user
        )

        try:
            discount_engine.apply_discounts()
            return self.order.total_after_discounts
        except ValidationError:
            return Decimal(0)

    # orders/services/calculate_additional_cost.py

    def calculate_additional_cost(self, discount_codes=None) -> Decimal:
        """
        Calculate the additional cost for added work after order creation,
        such as extra pages, slides, or services.

        Args:
            discount_codes (list, optional): Discount codes to apply.

        Returns:
            Decimal: Net additional amount the client needs to pay.
        """
        order = self.order

        # Extra content costs
        additional_pages_cost = (
            order.additional_pages * order.page_price
            if order.additional_pages else Decimal(0)
        )
        additional_slides_cost = (
            order.additional_slides * order.slide_price
            if order.additional_slides else Decimal(0)
        )

        # Extra services cost
        extra_services_cost = sum(
            service.service_cost for service in order.extra_services.all()
        )

        # Raw additional total
        total_additional_cost = (
            additional_pages_cost +
            additional_slides_cost +
            extra_services_cost
        )

        # Apply discount codes (optional)
        if discount_codes:
            discount_engine = DiscountEngine(
                discount_codes=discount_codes,
                order=order,
                website=order.website,
                user=order.user
            )
            try:
                discount_engine.apply_discounts()
                total_additional_cost = order.total_after_discounts
            except ValidationError as e:
                raise ValidationError(f"Discount error: {e}")

        return total_additional_cost


    def calculate_total_price(self) -> Decimal:
        """
        Aggregates all pricing components to compute the final total order price.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The total payable price after all additions and deductions.
        """
        base = self.calculate_base_price()
        extras = self.calculate_extra_services_price()
        quality = self.calculate_writer_quality_price()
        preferred = self.calculate_preferred_writer_fee()
        urgent = self.calculate_urgent_price()
        discount = self.calculate_discount()

        return base + extras + quality + preferred + urgent - discount

    def calculate_breakdown(self) -> dict:
        """
        Returns a detailed breakdown of the price components.
        Useful for frontend display or admin review.
        """
        base = self.calculate_base_price()
        extras = self.calculate_extra_services_price()
        quality = self.calculate_writer_quality_price()
        preferred = self.calculate_preferred_writer_fee()
        urgent = self.calculate_urgent_price()
        discount = self.calculate_discount()

        total = base + extras + quality + preferred + urgent - discount

        return {
            "base_price": float(base),
            "extra_services": float(extras),
            "writer_quality": float(quality),
            "preferred_writer": float(preferred),
            "urgent_fee": float(urgent),
            "discount": float(discount),
            "final_total": float(total)
        }

    def calculate_total_price(self) -> Decimal:
        """
        Aggregates all pricing components to compute the final total order price.

        Args:
            order (Order): The order instance.

        Returns:
            Decimal: The total payable price after all additions and deductions.
        """
        base = self.calculate_base_price()
        extras = self.calculate_extra_services_price()
        quality = self.calculate_writer_quality_price()
        preferred = self.calculate_preferred_writer_fee()
        urgent = self.calculate_urgent_price()
        discount = self.calculate_discount()

        return base + extras + quality + preferred + urgent - discount
    

    def calculate_breakdown(self) -> dict:
        """
        Returns a detailed breakdown of the price components.
        Useful for frontend display or admin review.
        """
        base = self.calculate_base_price()
        extras = self.calculate_extra_services_price()
        quality = self.calculate_writer_quality_price()
        preferred = self.calculate_preferred_writer_fee()
        urgent = self.calculate_urgent_price()
        discount = self.calculate_discount()

        total = base + extras + quality + preferred + urgent - discount

        return {
            "base_price": float(base),
            "extra_services": float(extras),
            "writer_quality": float(quality),
            "preferred_writer": float(preferred),
            "urgent_fee": float(urgent),
            "discount": float(discount),
            "final_total": float(total)
        }
    

    def save_snapshot(self):
        """
        Saves or updates a snapshot of the pricing breakdown.
        """
        from orders.models import OrderPricingSnapshot

        data = self.calculate_breakdown()

        OrderPricingSnapshot.objects.update_or_create(
            order=self.order,
            defaults={"pricing_data": data}
        )