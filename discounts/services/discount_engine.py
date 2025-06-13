"""
Core engine to validate, stack, and apply discount codes to orders.
"""

import logging
import secrets
import string
import random
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Dict, Optional
from copy import deepcopy

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now

from .config import DiscountConfigService
from ..validators.discount_validation import DiscountValidationService
from .discount_stacking import DiscountStackingService
from .discount_cloning_service import DiscountCloningService
from .discount_code_service import DiscountCodeService
# from .usage_service import DiscountUsageService
from .discount_usage_tracker import DiscountUsageTracker
from discounts.utils import (
    get_discount_model, get_discount_usage_model,
    get_discount_config
)
from audit_logging.services import log_audit_action as audit_log

logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL

DISCOUNT_TYPE_PERCENT = "percent"
DISCOUNT_TYPE_FIXED = "fixed"
DECIMAL_ZERO = Decimal("0.00")
DECIMAL_ONE = Decimal("1.00")
ROUNDING = ROUND_HALF_UP


class DiscountEngine:
    """
    Orchestrates discount validation, stacking, application, and utility logic.

    This class provides the main interface for applying discount codes to orders,
    ensuring that all business rules around stacking, tiers, usage limits, and
    activation windows are respected. It also offers utilities for generating
    unique codes, duplicating discounts, and batch-expiring expired discounts.

    Usage:
        engine = DiscountEngine(discount_codes, order, website, user)
        final_price, applied_discounts = engine.apply_discount_to_order(order, discount_codes, website, user)

    Key Responsibilities:
        - Validate discount codes and their applicability.
        - Resolve stackable combinations of discounts.
        - Apply discounts in the correct order and calculate reductions.
        - Track usage and audit discount applications.
        - Manage discount lifecycle (activate, deactivate, expire).
        - Generate unique codes and duplicate discounts for campaigns.
    """

    def __init__(self, discount_codes=None, order=None, website=None, user=None):
        """
        Initializes the DiscountEngine with necessary parameters.
        Args:
            discount_codes (List[str]): List of discount codes to validate and apply.
            order: The order object to which discounts will be applied.
            website: The website context for which discounts are valid.
            user: The user applying the discounts, if applicable.
        """
        self.discount_codes = discount_codes or []
        self.order = order
        self.website = website
        self.user = user
        self.config = DiscountConfigService.get_config(website)
        self.discount_model = get_discount_model()
        self.usage_model = get_discount_usage_model()

    @staticmethod
    def calculate_discounted_amount(discount, tier, price: Decimal) -> Decimal:
        """
        Calculates the discount amount based on tier settings and discount type.

        Args:
            discount: The Discount instance (contains type and value).
            tier: The applicable DiscountTier instance (may cap percent-based discount).
            price (Decimal): The original price of the order.

        Returns:
            Decimal: The discount amount to subtract from the price.
        """
        if discount.discount_type == "percent":
            percent = tier.percent_off if tier else Decimal(discount.value)
            raw_discount = (percent / Decimal("100.0")) * price
            if tier and tier.max_discount_amount:
                raw_discount = min(raw_discount, tier.max_discount_amount)
            return raw_discount.quantize(Decimal("0.01"), rounding=ROUNDING)

        elif discount.discount_type == "fixed":
            fixed_value = Decimal(discount.value)
            return min(price, fixed_value).quantize(Decimal("0.01"), rounding=ROUNDING)

        raise ValidationError(f"Unsupported discount type: {discount.discount_type}")
    
    @staticmethod
    def get_applicable_tier(discount, order_total):
        """
        Get the applicable tier discount based on the order total.
        Args:
            discount (Discount): The discount object with tiers.
            order_total (Decimal): The total value of the order.
        Returns:
            Decimal: The applicable discount percentage for the order total.
        """
        if not discount:
            return 0
        if not order_total or order_total <= 0:
            return 0
        if discount.discount_type != DISCOUNT_TYPE_PERCENT:
            raise ValidationError("Tiers are only applicable for percentage discounts.")
        if not discount.has_tiers and discount.percent_off is None:
            raise ValidationError("Discount must have tiers or a percent_off value.")
        if order_total < 0:
            raise ValidationError("Order total must be a positive value.")
        if not discount.has_tiers and discount.percent_off is not None:
            return discount.percent_off
        if not discount.tiers.exists():
            raise ValidationError("Discount has no tiers defined.")
        if order_total < discount.tiers.first().min_order_value:
            raise ValidationError(
                "Order total does not meet the minimum value for any tier."
            )
        if not discount.is_active:
            raise ValidationError("Discount is not active.")
        if not discount.start_date or not discount.end_date:
            raise ValidationError("Discount must have a valid start and end date.")
        if discount.start_date and discount.start_date > timezone.now():
            raise ValidationError("Discount has not started yet.")
        if discount.end_date and discount.end_date < timezone.now():
            raise ValidationError("Discount has already expired.")
        if discount.max_uses is not None and discount.used_count >= discount.max_uses:
            raise ValidationError("Discount has reached its maximum usage limit.")
        if not discount.has_tiers:
            return discount.percent_off
        tiers = (
            discount.tiers.filter(
                is_active=True,
                min_order_value__lte=order_total,
                start_date__lte=now(),
                end_date__gte=now(),
            )
            .order_by("-min_order_value")
            .first()
        )

        active_tiers = [
            tier for tier in tiers
            if tier.is_currently_active() and order_total >= tier.min_order_value
        ]
        if not active_tiers:
            logger.debug(
                f"No active tiers found for discount {discount.code} "
                f"and order total {order_total}."
            )
            return None
        return active_tiers[0]
    
    
    @classmethod
    def apply_discount_to_order(cls, order, codes, website, user=None) -> Tuple[Decimal, List[Dict]]:
        """
        Apply one or more discount codes to an order.
        """
        if isinstance(codes, str):
            codes = [codes]

        valid_discounts = DiscountValidationService.validate_discount_codes(
            codes,
            website
        )

        if not valid_discounts:
            raise ValidationError("No valid discount codes found.")
        
        if user is None:
            user = getattr(order, "user", None)
        stacking_service = DiscountStackingService(user, website)
        stackable_discounts = stacking_service.resolve_stack_from_list(valid_discounts)
        if not stackable_discounts:
            logger.warning(f"Stacking failed: {valid_discounts}")
            raise ValidationError("No compatible discounts can be stacked together.")

        final_price = order.total_price
        applied_discounts = []

        for discount in stackable_discounts:
            order_total = final_price
            tier = cls.get_applicable_tier(discount, final_price)
            reduction = cls.calculate_discounted_amount(discount, tier, final_price)
            reduction = min(reduction, final_price)
            if reduction > 0:
                applied_discounts.append({
                    "code": discount.code,
                    "amount": float(reduction),
                    "type": discount.discount_type,
                })
                final_price -= reduction
        
        DiscountUsageTracker.track_multiple(
                    discounts=stackable_discounts,
                    order=order,
                    user=user
                )
        
        final_price = final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        audit_log(
            actor=user,
            target=order,
            action="discount_applied",
            metadata={"codes": codes, "applied": applied_discounts}
        )

        return max(final_price, 0), applied_discounts

    def validate_clean(self, discount):
        """
        Validate discount fields before activation.
        """
        if self.discount_model.objects.filter(
            code=discount.code,
            website=discount.website
        ).exclude(id=discount.id).exists():
            raise ValidationError("A discount with this code already exists.")

        if discount.discount_type == DISCOUNT_TYPE_PERCENT:
            if not (0 < discount.value <= 100):
                raise ValidationError("Percentage discount must be between 1 and 100.")

        if discount.start_date and discount.end_date:
            if discount.start_date > discount.end_date:
                raise ValidationError("End date must be after start date.")

        if discount.max_uses is not None and discount.max_uses <= 0:
            raise ValidationError("Max uses must be a positive number.")

        if not discount.stackable and self.discount_model.objects.filter(
            website=discount.website, stackable=True
        ).exists():
            raise ValidationError("This discount cannot be stacked with others.")

    def activate_discount(self, discount):
        """
        Activate a discount if it's valid.
        """
        self.validate_clean(discount)
        if not discount.is_active:
            discount.is_active = True
        discount.save()

    def deactivate_discount(self, discount):
        """
        Deactivate a discount.
        """
        if discount.is_active:
            discount.is_active = False
            discount.save()

    def expire_discount(self, discount):
        """
        Deactivate if the discount has expired.
        """
        if discount.end_date and discount.end_date < timezone.now():
            self.deactivate_discount(discount)


    @staticmethod
    def mark_expired_discounts():
        """
        Batch-expire all discounts past their end date.
        """
        get_discount_model().objects.filter(
            end_date__lt=now(), is_active=True
        ).update(is_active=False)

    def generate_unique_discount_code(self, prefix="", length=8, max_attempts=10):
        """
        Generate a unique discount code.
        """
        return DiscountCodeService.create_discount_code(
            prefix=prefix,
            length=length,
            max_attempts=max_attempts
        )

    @staticmethod
    def fetch_by_codes(codes: List[str], website):
        """
        Fetch active, valid discounts by codes.
        Can be used to validate codes before applying them.
        Args:
            codes (List[str]): List of discount codes to fetch.
            website: The website context for which discounts are valid.
        Returns:
            QuerySet: A queryset of active Discount objects matching the codes. 
        """
        Discount = get_discount_model()
        return Discount.objects.filter(
            website=website,
            code__in=codes,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).only("id", "code", "value", "discount_type", "percent_off")

    @staticmethod
    def clone_campaign_discounts(self, original_queryset):
        """
        Clone a queryset of discounts, resetting fields and ensuring unique codes.
        Args:
            original_queryset (QuerySet): Discounts to clone.
        Returns:
            List: List of newly created Discount objects.
        """
        if not original_queryset.exists():
            return []
        if not isinstance(original_queryset, self.discount_model.objects.__class__):
            raise TypeError("Expected a QuerySet of Discount objects.")
        if not all(isinstance(d, self.discount_model) for d in original_queryset):
            raise TypeError("All items in the queryset must be Discount instances.")
        if not original_queryset.filter(is_active=True).exists():
            logger.warning("No active discounts found in the queryset.")
            return []
        if not original_queryset.filter(website=self.website).exists():
            logger.warning("No discounts found for the specified website.")
            return []
        if not original_queryset.filter(start_date__lte=now()).exists():
            logger.warning("No discounts with a valid start date found in the queryset.")
            return []
        return DiscountCloningService.duplicate_discounts(original_queryset)
    
    @staticmethod
    def clone_discount_code(self, discount, actor=None):
        """
        Clone a single discount, generating a new unique code and resetting relevant fields.

        Args:
            discount: The Discount instance to clone.
            actor: Optional user performing the action, for audit logging.

        Returns:
            The newly created Discount object.
        """
        return DiscountCloningService.duplicate_discounts([discount], actor=actor)[0]