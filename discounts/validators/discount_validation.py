"""
Validates discount codes before use.
"""
import logging
import random
import string
from typing import List, Dict, Any
from django.db import transaction
from django.db.models import Q
# from discounts.models import Discount, DiscountUsage
from discounts.services.discount_stacking import DiscountStackingService
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from discounts.utils import get_discount_model, get_discount_usage_model

logger = logging.getLogger(__name__)

class DiscountValidationService:
    """
    Service for validating discount codes before applying them to an order.
    """
    def __init__(self, order, discount_model=None, usage_model=None):
        self.order = order
        self.discount_model = discount_model or get_discount_model()
        self.usage_model = usage_model or get_discount_usage_model()


    def validate_campaign(self):
        """
        Validate the promotional campaign associated with the discount.
        Raises:
            ValidationError: If the campaign is deleted, inactive, or not live.
        """
        campaign = self.discount.promotional_campaign
        if not campaign:
            return  # No campaign — nothing to validate

        if campaign.is_deleted:
            raise ValidationError("Campaign has been deleted.")

        if not campaign.is_active:
            raise ValidationError("Campaign is not active.")

        if not campaign.is_live:
            raise ValidationError("Campaign is not within its active date range.")

    @staticmethod
    def validate_discounts(self, codes, website, config):
        """
        Validate discount codes for a website and config.

        Args:
            codes (list): Discount codes.
            website (Website): Website context.
            config (DiscountConfig): Discount config.

        Returns:
            list: Validated Discount instances.
        """
        if not codes:
            return []
        
        current_time = now()

        discounts = self.discount_model.objects.filter(
            code__in=codes, website=website, is_active=True
        )

        if not discounts.exists():
            raise ValidationError("No valid discounts found.")

        validated = []
        for discount in discounts:
            if self._validate_discount(discount, website, current_time):
                try:
                    self.stacking_service.validate_stacking(discount)
                    validated.append(discount)
                except ValidationError:
                    # Skip invalid stackers silently; use resolve_stack instead
                    continue
        if not validated:
            raise ValidationError("All provided discounts were invalid or "
                                  "violated stacking rules.")
        # Auto-resolve stacking if more than 1
        return self.stacking_service.resolve_stack_from_list(validated)
            
    def _validate_discount(self, discount, website, current_time):
        """
        Validates a single discount code.

        Args:
            discount: Discount instance to validate
            website: Website instance to check against
            current_time: The current time to check validity

        Raises:
            ValidationError if the discount code is invalid.
        """
        
        if discount.website != website:
            raise ValidationError(
                f"Discount {discount.code} is not valid on this website."
            )

        if not discount.is_active:
            raise ValidationError(
                f"Discount {discount.code} is inactive."
            )

        if discount.valid_from and discount.valid_from > current_time:
            raise ValidationError(
                f"Discount {discount.code} is not yet valid."
            )

        if discount.valid_until and discount.valid_until < current_time:
            raise ValidationError(
                f"Discount {discount.code} has expired."
            )

        if discount.usage_limit is not None:
            if discount.used_count >= discount.usage_limit:
                raise ValidationError(
                    f"Discount {discount.code} has reached its usage limit."
                )

        return True
    

    def is_valid_for_order(self, discount):
        """
        Check if a discount is valid for the current order.

        Args:
            discount (Discount): The discount to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not discount.is_active:
            return False
        if discount.start_date and discount.start_date > now():
            return False
        if discount.end_date and discount.end_date < now():
            return False
        if discount.min_order_value and discount.min_order_value > self.order.total:
            return False
        if discount.applies_to_first_order_only and self.order.user.orders.exists():
            return False
        if discount.per_user_limit is not None:
            try:
                self.validate_per_user_limit(discount, self.order.user)
            except ValidationError:
                return False
        return True
    @staticmethod
    def check_discount_stacking_for_order(order, discounts):
        """
        Check if the provided discounts can be stacked for the given order.

        Args:
            order (Order): The order to check against.
            discounts (list[Discount]): List of discounts to validate.

        Returns:
            tuple: (bool, list[Discount]) - Whether stacking is valid and the valid discounts.
        """
        if not discounts:
            return True, []

        Discount = get_discount_model()
        usage_model = get_discount_usage_model()

        used_ids = usage_model.objects.filter(
            user=order.user
        ).values_list('discount', flat=True)
        used_discounts = Discount.objects.filter(id__in=used_ids)

        allowed_ids = [d.id for d in discounts if d.stackable_with.exists()]

        incompatible = used_discounts.exclude(id__in=allowed_ids)
        if incompatible.exists():
            return False, []

        return True, discounts
    @staticmethod
    def check_discount_stacking(discount, user):
        """
        Check if a discount can be stacked based on its properties and user's usage.

        Args:
            discount (Discount): The discount to check.
            user (User): The user applying the discount.

        Returns:
            bool: True if the discount can be stacked, False otherwise.
        """
        usage_model = get_discount_usage_model()
        count = usage_model.objects.filter(user=user, discount=discount).count()

        if not discount.stackable:
            return False
        if discount.max_discount_percent and (
            count + discount.value > discount.max_discount_percent
        ):
            return False
        if discount.max_uses and count >= discount.max_uses:
            return False
        if discount.max_stackable_uses_per_customer and (
            count >= discount.max_stackable_uses_per_customer
        ):
            return False

        return True

    @staticmethod
    def can_apply_discount(discount, order):
        """
        Check if a discount can be applied to the order based on its properties.

        Args:
            discount (Discount): The discount to check.
            order (Order): The order to check against.

        Returns:
            bool: True if the discount can be applied, False otherwise.
        """
        if not discount.is_active:
            return False
        if discount.start_date and discount.start_date > now():
            return False
        if discount.end_date and discount.end_date < now():
            return False
        if discount.min_order_value and order.total < discount.min_order_value:
            return False
        if discount.applies_to_first_order_only and order.user.orders.exists():
            return False
        
        return True
    @staticmethod
    def validate_max_stackable_uses(discount, user):
        """
        Validate if the user can still use the discount based on max stackable uses.

        Args:
            discount (Discount): The discount to validate.
            user (User): The user applying the discount.

        Returns:
            bool: True if the user can still use the discount, False otherwise.

        Raises:
            ValidationError: If the user has exceeded the max stackable uses.
        """
        usage_model = get_discount_usage_model()
        count = usage_model.objects.filter(user=user, discount=discount).count()

        if discount.max_stackable_uses_per_customer is not None and count >= discount.max_stackable_uses_per_customer:
            raise ValidationError(
                f"You've already used this discount {discount.max_stackable_uses_per_customer} times."
            )
        return True