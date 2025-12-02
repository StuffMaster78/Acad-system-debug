from decimal import Decimal
from django.core.exceptions import ValidationError
from pricing_configs.models import (
    PricingConfiguration,
    AcademicLevelPricing,
    WriterLevelOptionConfig,
    PreferredWriterConfig,
    DeadlineMultiplier,
    AdditionalService,
    TypeOfWorkMultiplier
)
from pricing_configs.services.deadline_multiplier_service import DeadlineMultiplierService
from pricing_configs.services.urgency_service import UrgencyService


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
        if order_input.get("num_pages", 0) < 0 or order_input.get("num_slides", 0) < 0:
            raise ValidationError("Pages and slides must be non-negative.")

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

        # Academic Level Multiplier
        academic_level = order_input.get("academic_level")
        level_pricing = AcademicLevelPricing.objects.filter(
            website=website, academic_level=academic_level
        ).first()
        level_multiplier = (
            level_pricing.multiplier if level_pricing else Decimal("1.0")
        )
        base_price *= level_multiplier
        breakdown["multipliers"]["academic_level"] = float(level_multiplier)

        # Type of Work Multiplier
        order_type_name = order_input.get("order_type")
        if order_type_name:
            order_type = TypeOfWorkMultiplier.objects.filter(
                website=website,
                name__iexact=order_type_name
            ).first()
            if order_type and order_type.is_active:
                base_price *= order_type.multiplier
                breakdown["multipliers"]["order_type"] = float(
                    order_type.multiplier
                )

        # Technicality Multiplier
        is_technical = order_input.get("is_technical", False)
        tech_multiplier = (
            pricing_config.technical_multiplier
            if is_technical else pricing_config.non_technical_order_multiplier
        )
        base_price *= tech_multiplier
        breakdown["multipliers"]["technical"] = float(tech_multiplier)

        # Deadline & Urgency
        raw_deadline_hours = float(order_input.get("deadline_hours", 24))
        pages = int(order_input.get("num_pages", 0) or 0)

        urgency_result = UrgencyService.normalize_deadline(
            pages=pages,
            requested_hours=raw_deadline_hours,
        )
        deadline_hours = urgency_result.normalized_hours

        deadline_multiplier = DeadlineMultiplierService.get_multiplier_for_hours(
            website=website,
            hours=deadline_hours
        )
        base_price *= deadline_multiplier
        breakdown["multipliers"]["deadline"] = float(deadline_multiplier)
        
        # Add deadline & urgency info to breakdown
        deadline_info = DeadlineMultiplierService.get_multiplier_info(
            website=website,
            hours=deadline_hours
        )
        breakdown["deadline_info"] = deadline_info
        breakdown["urgency"] = UrgencyService.to_dict(urgency_result)

        return base_price

    @staticmethod
    def _apply_add_ons(base_price, order_input,
                       pricing_config, breakdown):
        """ Applies additional costs for preferred writer,
        additional services, and high-value order bump.
        """
        website = order_input["website"]
        breakdown["add_ons"] = {}

        # Preferred Writer Cost
        preferred_writer = order_input.get("preferred_writer")
        if preferred_writer:
            try:
                preferred_writer_config = PreferredWriterConfig.objects.get(website=website)
                if preferred_writer_config.is_active:
                    base_price += preferred_writer_config.preferred_writer_cost
                    breakdown["add_ons"]["preferred_writer"] = float(
                        preferred_writer_config.preferred_writer_cost
                    )
            except PreferredWriterConfig.DoesNotExist:
                pass

        writer_level = order_input.get("writer_level")
        if writer_level:
            level = WriterLevelOptionConfig.objects.filter(
                website=website,
                name__iexact=writer_level,
                is_active=True
            ).first()
            if level:
                base_price += level.value
                breakdown["add_ons"]["writer_level"] = float(
                    level.value
                )


        # Additional Services Cost
        total_service_cost = Decimal(0)
        for slug in order_input.get("additional_services", []):
            service = AdditionalService.objects.filter(
                website=website, slug=slug, is_active=True
            ).first()
            if service:
                total_service_cost += service.cost
                breakdown["add_ons"][service.slug] = float(service.cost)

        base_price += total_service_cost
        return base_price