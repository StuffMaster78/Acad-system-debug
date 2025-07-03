from decimal import Decimal
from django.core.exceptions import ValidationError
from discounts.services.discount_engine import DiscountEngine
from orders.services.pricing_calculator import (
    PricingCalculatorService
)


class WriterRequestPricingService:
    """
    Service to handle pricing calculations for writer-initiated
    order change requests (pages, slides).
    """

    def __init__(self, writer_request):
        self.writer_request = writer_request
        self.order = writer_request.order
        self.website = self.order.website
        self.config = PricingCalculatorService.get_pricing_config_for_website(
            self.website.id
        )

    def calculate_estimated_cost(self):
        """
        Calculates the raw cost for the request, before discounts.
        Stores result in `writer_request.estimated_cost`.
        """
        pages_cost = Decimal("0")
        slides_cost = Decimal("0")

        if self.writer_request.additional_pages:
            pages_cost = (
                self.writer_request.additional_pages *
                self.config.base_price_per_page
            )

        if self.writer_request.additional_slides:
            slides_cost = (
                self.writer_request.additional_slides *
                self.config.base_price_per_slide
            )

        total = pages_cost + slides_cost
        self.writer_request.estimated_cost = total
        return total

    def calculate_discounted_cost(self):
        """
        Applies applicable discounts to the estimated cost.
        Stores result in `writer_request.final_cost`.
        """
        estimated_cost = (
            self.writer_request.estimated_cost or
            self.calculate_estimated_cost()
        )

        if not self.order.discount:
            self.writer_request.final_cost = estimated_cost
            return estimated_cost

        try:
            discount_engine = DiscountEngine(
                discount_codes=[self.order.discount.code],
                order=self.order,
                website=self.website,
                user=self.order.user,
                custom_cost_context={
                    "additional_pages": self.writer_request.additional_pages,
                    "additional_slides": self.writer_request.additional_slides,
                    "base_price_per_page": self.config.base_price_per_page,
                    "base_price_per_slide": self.config.base_price_per_slide,
                }
            )
            discount_engine.apply_discounts()
            discounted = discount_engine.discounted_total
            self.writer_request.final_cost = discounted
            return discounted
        except ValidationError:
            # If discount fails, fallback to raw estimate
            self.writer_request.final_cost = estimated_cost
            return estimated_cost

    def update_writer_request_costs(self, save=True):
        """
        Calculates and assigns both estimated and final cost.
        Optionally saves the instance.
        """
        self.calculate_estimated_cost()
        self.calculate_discounted_cost()

        if save:
            self.writer_request.save()