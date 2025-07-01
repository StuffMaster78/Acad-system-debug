from decimal import Decimal
from django.core.exceptions import ValidationError
from pricing_configs.models import (
    PricingConfiguration,
    AcademicLevelPricing,
    WriterQuality,
    PreferredWriterConfig,
    DeadlineMultiplier,
    AdditionalService,
    OrderTypeMultiplier
)


class PricingEstimationService:
    """
    Service to estimate the total price of an order
    based on various dynamic pricing factors.
    """

    @staticmethod
    def calculate(order_input: dict) -> dict:
        website = order_input["website"]

        pricing_config = PricingEstimationService._get_pricing_config(
            website
        )

        base_price = PricingEstimationService._calculate_base_price(
            pricing_config, order_input
        )

        breakdown = {
            "base_price": base_price,
            "multipliers": {},
            "add_ons": {},
            "final_price": Decimal(0)
        }

        base_price = PricingEstimationService._apply_multipliers(
            base_price, order_input, pricing_config, breakdown
        )

        base_price = PricingEstimationService._apply_add_ons(
            base_price, order_input, pricing_config, breakdown
        )

        final_price = base_price.quantize(Decimal("0.01"))
        breakdown["final_price"] = float(final_price)

        return breakdown
    
    @staticmethod
    def _get_pricing_config(website):
        """ Retrieves the latest pricing configuration for the given website. """
        try:
            return PricingConfiguration.objects.filter(
                website=website
            ).latest("created_at")
        except PricingConfiguration.DoesNotExist:
            raise ValidationError("Pricing config not found for this website.")

    @staticmethod
    def _calculate_base_price(pricing_config, order_input):
        """ Calculates the base price based on number of pages and slides. """
        return (
            Decimal(order_input.get("num_pages", 0)) *
            pricing_config.base_price_per_page +
            Decimal(order_input.get("num_slides", 0)) *
            pricing_config.base_price_per_slide
        )

    @staticmethod
    def _apply_multipliers(base_price, order_input,
                           pricing_config, breakdown):
        """ Applies various multipliers to the base price
        based on academic level, order type, technicality,
        deadline, and writer quality.
        """
        website = order_input["website"]

        academic_level = order_input["academic_level"]
        level_pricing = AcademicLevelPricing.objects.filter(
            website=website, academic_level=academic_level
        ).first()
        level_multiplier = (
            level_pricing.multiplier if level_pricing else Decimal(1.0)
        )
        base_price *= level_multiplier
        breakdown["multipliers"]["academic_level"] = float(level_multiplier)

        order_type_name = order_input.get("order_type")
        if order_type_name:
            order_type = OrderTypeMultiplier.objects.filter(
                website=website,
                name__iexact=order_type_name
            ).first()
            if order_type:
                base_price *= order_type.multiplier
                breakdown["multipliers"]["order_type"] = float(
                    order_type.multiplier
                )

        is_technical = order_input.get("is_technical", False)
        tech_multiplier = (
            pricing_config.technical_multiplier
            if is_technical else pricing_config.non_technical_order_multiplier
        )
        base_price *= tech_multiplier
        breakdown["multipliers"]["technical"] = float(tech_multiplier)

        deadline_hours = order_input.get("deadline_hours", 24)
        deadline = DeadlineMultiplier.objects.filter(
            website=website, hours__lte=deadline_hours
        ).order_by("-hours").first()
        if deadline:
            base_price *= deadline.multiplier
            breakdown["multipliers"]["deadline"] = float(
                deadline.multiplier
            )

        writer_quality = order_input.get("writer_quality")
        if writer_quality:
            quality = WriterQuality.objects.filter(
                website=website, name__iexact=writer_quality
            ).first()
            if quality:
                base_price *= quality.cost_multiplier
                breakdown["multipliers"]["writer_quality"] = float(
                    quality.cost_multiplier
                )

        return base_price

    @staticmethod
    def _apply_add_ons(base_price, order_input,
                       pricing_config, breakdown):
        """ Applies additional costs for preferred writer,
        additional services, and high-value order bump.
        """
        website = order_input["website"]

        preferred_writer = order_input.get("preferred_writer")
        if preferred_writer:
            pref = PreferredWriterConfig.objects.filter(
                website=website, name__iexact=preferred_writer
            ).first()
            if pref:
                base_price += pref.preferred_writer_cost
                breakdown["add_ons"]["preferred_writer"] = float(
                    pref.preferred_writer_cost
                )

        total_service_cost = Decimal(0)
        for slug in order_input.get("additional_services", []):
            service = AdditionalService.objects.filter(
                website=website, slug=slug, is_active=True
            ).first()
            if service:
                total_service_cost += service.cost
                breakdown["add_ons"][service.slug] = float(service.cost)

        base_price += total_service_cost

        if base_price >= pricing_config.hvo_threshold:
            hvo_fee = getattr(pricing_config, "hvo_additional_cost", 0)
            base_price += hvo_fee
            breakdown["add_ons"]["high_value_order_bump"] = float(hvo_fee)

        return base_price