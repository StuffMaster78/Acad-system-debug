"""
Core engine to validate, stack, and apply discount codes to orders.
"""

import logging
import secrets
import string
import random
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple, Dict, Optional

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.timezone import now

from .config import DiscountConfigService
from ..validators.discount_validation import DiscountValidationService
from .discount_stacking import DiscountStackingService
# from .usage_service import DiscountUsageService
from .discount_usage_tracker import DiscountUsageTracker
from discounts.utils import (
    get_discount_model, get_discount_usage_model,
    get_discount_config
)
from audit_logging.services import audit_log

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
    """

    def __init__(self, discount_codes=None, order=None, website=None, user=None):
        self.discount_codes = discount_codes or []
        self.order = order
        self.website = website
        self.user = user
        self.config = DiscountConfigService.get_config(website)
        self.discount_model = get_discount_model()
        self.usage_model = get_discount_usage_model()

    @staticmethod
    def calculate_discounted_amount(discount, price: Decimal) -> Decimal:
        """
        Calculate the discount amount based on type and price.
        """
        if discount.discount_type == DISCOUNT_TYPE_PERCENT:
            return (price * Decimal(discount.value) / Decimal("100.0")).quantize(
                Decimal("0.01"), rounding=ROUNDING
            )
        elif discount.discount_type == DISCOUNT_TYPE_FIXED:
            return min(price, Decimal(discount.value)).quantize(
                Decimal("0.01"), rounding=ROUNDING
            )
        raise ValidationError(f"Unsupported discount type: {discount.discount_type}")

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
            reduction = cls.calculate_discounted_amount(discount, final_price)
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
        charset = string.ascii_uppercase + string.digits
        for _ in range(max_attempts):
            random_part = ''.join(secrets.choice(charset) for _ in range(length))
            code = f"{prefix}{random_part}"
            if not self.discount_model.objects.filter(code=code).exists():
                return code
        raise RuntimeError("Failed to generate a unique discount code.")

    @staticmethod
    def fetch_by_codes(codes: List[str], website):
        """
        Fetch active, valid discounts by codes.
        """
        Discount = get_discount_model()
        return Discount.objects.filter(
            website=website,
            code__in=codes,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
    
    @staticmethod
    def duplicate_discounts(queryset):
        """
        Duplicate a queryset of discounts, resetting their fields.
        Args:
            queryset (QuerySet): The queryset of discounts to duplicate.
        Returns:
            list[Discount]: List of newly created discount objects.
        """  
        new_discounts = []
        for discount in queryset:
            discount.pk = None
            discount.code += "_" + ''.join(random.choices(string.ascii_uppercase, k=4))
            discount.start_date = now()
            discount.end_date = None
            discount.is_active = True
            discount.used_count = 0
            new_discounts.append(discount)
        return get_discount_model().objects.bulk_create(new_discounts)