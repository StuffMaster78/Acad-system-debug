"""
Core discount engine to orchestrate validation, stacking, application.
"""

import logging
import random
import secrets
import string
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import F, Q
from django.utils import timezone
from django.utils.timezone import now

from .config import DiscountConfigService
from .usage import DiscountUsageService
from .validation import DiscountValidationService
from .stacking import DiscountStackingService
logger = logging.getLogger(__name__)
User = settings.AUTH_USER_MODEL

def get_discount_model():
    from discounts.models import Discount
    return Discount

def get_discount_usage_model():
    from discounts.models import DiscountUsage
    return DiscountUsage

def get_discount_config():
    from models.discount_configs import DiscountConfig  # Move import here
    return DiscountConfig.objects.first()

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

    def apply_discounts(self):
        """
        Validates, stacks, and applies discount codes to the order.
        """
        from orders.models import OrderDiscount 
        if len(self.discount_codes) > self.config.max_stackable_discounts:
            raise ValidationError(
                f"You can only stack up to "
                f"{self.config.max_stackable_discounts} discount codes."
            )

        validated = DiscountValidationService.validate_codes(
            self.discount_codes, self.website, self.config
        )

        # Sort by priority or value, then pick top-N stackable ones
        validated = sorted(validated, key=lambda d: d.priority or 0, reverse=True)
        stackable_discounts = validated[: self.config.max_stackable_discounts]

        # Apply each discount in order
        total = self.order.total
        applied_discounts = []

        for discount in stackable_discounts:
            discounted_amount = discount.apply(total)
            if discounted_amount > 0:
                total -= discounted_amount
                applied_discounts.append({
                    "code": discount.code,
                    "amount": discounted_amount,
                    "final_total": total
                })

        self.order.total_after_discounts = max(total, 0)
        self.order.applied_discounts = applied_discounts
        return applied_discounts


    def validate_clean(self, discount):
        if self.discount_model.objects.filter(
            code=discount.code,
            website=discount.website
        ).exclude(id=discount.id).exists():
            raise ValidationError(
                "A discount with this code already exists for this website."
            )

        if discount.discount_type == 'percentage':
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
        self.validate_clean(discount)
        if not discount.is_active:
            discount.is_active = True
        discount.save()

    def deactivate_discount(self, discount):
        if discount.is_active:
            discount.is_active = False
            discount.save()

    def expire_discount(self, discount):
        if discount.end_date and discount.end_date < timezone.now():
            self.deactivate_discount(discount)


    @staticmethod
    def mark_expired_discounts():
        get_discount_model().objects.filter(
            end_date__lt=now(), is_active=True
        ).update(is_active=False)

    @classmethod
    def generate_unique_discount_code(cls, prefix="", length=8, max_attempts=10):
        """
        Securely generate a unique discount code using the class's model.

        Args:
            prefix (str): Optional prefix for the code.
            length (int): Length of the random part.
            max_attempts (int): Max tries before giving up.

        Returns:
            str: A unique discount code.

        Raises:
            RuntimeError: If uniqueness can't be guaranteed.
        """
        charset = string.ascii_uppercase + string.digits

        for _ in range(max_attempts):
            random_part = ''.join(secrets.choice(charset) for _ in range(length))
            code = f"{prefix}{random_part}"
            if not cls.model.objects.filter(code=code).exists():
                return code

        raise RuntimeError("Failed to generate a unique discount code.")
    
    @staticmethod
    def fetch_by_codes(codes: list[str], website):
        """
        Fetch discounts by their codes for a given website.

        Args:
            codes (list[str]): List of discount codes to fetch.
            website (Website): The website for which to fetch applicable discounts.

        Returns:
            list[Discount]: List of valid discounts for the given website and codes.
        """
        def get_discount_model():
            from discounts.models import Discount
            return Discount
        Discount = get_discount_model()
        # Filter discounts based on the website and validate codes
        discounts = Discount.objects.filter(
            website=website,
            code__in=codes,
            is_active=True,  # Ensure the discount is active
            valid_from__lte=timezone.now(),  # Ensure the discount is active from this date
            valid_until__gte=timezone.now()  # Ensure the discount is still valid
        )

        valid_discounts = []

        # Check if codes match any discounts and are applicable
        for discount in discounts:
            if discount.code in codes:  # You can extend this check as needed
                valid_discounts.append(discount)

        return valid_discounts

    def is_valid_for_order(self, discount):
        if not discount.is_active:
            return False
        if discount.min_order_value and self.order.total < discount.min_order_value:
            return False
        if discount.applies_to_first_order_only and self.order.user.orders.exists():
            return False
        return True

    def check_discount_stacking(self, discount, user):
        if not discount.stackable:
            return discount

        used_ids = self.usage_model.objects.filter(
            user=user
        ).values_list('discount', flat=True)
        used_discounts = self.discount_model.objects.filter(id__in=used_ids)
        allowed_ids = discount.stackable_with.values_list('id', flat=True)

        if used_discounts.exclude(id__in=allowed_ids).exists():
            raise ValidationError("You're using incompatible discounts.")

        return discount

    def can_be_stacked(self, discount, total_percent=0):
        if not discount.stackable:
            return False
        if discount.max_discount_percent and (
            total_percent + discount.value > discount.max_discount_percent
        ):
            return False
        if discount.max_uses and discount.used_count >= discount.max_uses:
            return False
        if discount.max_stackable_uses_per_customer:
            count = self.usage_model.objects.filter(
                user=self.user, discount=discount
            ).count()
            if count >= discount.max_stackable_uses_per_customer:
                return False
        return True

    def validate_max_stackable_uses(self, discount):
        if discount.max_stackable_uses_per_customer is None:
            return True
        count = self.usage_model.objects.filter(
            user=self.user, discount=discount
        ).count()
        if count >= discount.max_stackable_uses_per_customer:
            raise ValidationError(
                f"You've already used this discount "
                f"{discount.max_stackable_uses_per_customer} times."
            )
        return True

    def soft_delete(self, discount):
        discount.is_deleted = True
        discount.save(update_fields=['is_deleted'])

    @staticmethod
    def duplicate_discounts(queryset):
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
    @staticmethod
    def apply_discount_to_order(order, discount, current_price):
        """
        Apply a single discount to the order based on its type.

        Args:
            order (Order): The order being discounted
            discount (Discount): The discount to apply
            current_price (Decimal): Current price before this discount

        Returns:
            Decimal: The amount reduced from the order price
        """
        if discount.discount_type == "percent":
            reduction = (discount.value / Decimal("100.0")) * current_price
        elif discount.discount_type == "fixed":
            reduction = discount.value
        else:
            raise ValidationError("Unsupported discount type.")

        reduction = min(reduction, current_price)
        logger.info(
            f"Applied discount {discount.code}: -{reduction} on "
            f"order {order.id}"
        )
        return reduction

    def _apply_single(self, discount):
        """
        Applies a single discount directly and persists it.

        Args:
            discount (Discount): The discount to apply.

        Updates:
            - self.final_price
            - self.applied list
            - OrderDiscount entry
        """
        from orders.models import OrderDiscount
        # Calculate the discount value
        if discount.discount_type == "percentage":
            discount_value = (
                self.final_price * (Decimal(discount.value) / Decimal("100.0"))
            )
        elif discount.discount_type == "fixed":
            discount_value = Decimal(discount.value)
        else:
            logger.error(f"Unsupported discount type: {discount.discount_type}")
            return

        discount_value = min(self.final_price, discount_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        if discount_value <= 0:
            logger.warning(f"Discount {discount.code} applied zero value")
            return

        self.final_price = max(Decimal("0.00"), self.final_price - discount_value)

        OrderDiscount.objects.update_or_create(
            order=self.order,
            discount=discount,
            defaults={"amount": discount_value}
        )

        self.applied.append({
            "code": discount.code,
            "type": discount.discount_type,
            "value": float(discount.value),
            "amount": float(discount_value),
        })

        logger.info(f"Applied discount {discount.code} to order {self.order.id}")

    def apply_stacked_discounts(order, discounts):
        """
        Applies stackable discounts and returns new total and breakdown.
        """
        DiscountConfig = get_discount_config()
        applicable, _ = DiscountStackingService.check_discount_stacking_for_order(
            order, discounts
        )

        if not applicable:
            raise ValidationError("No valid stackable discounts found.")

        final_price = order.total_price
        applied_discounts = []
        config = DiscountConfig.objects.get(website=order.website)

        for discount in applicable:
            try:
                applied_value = DiscountEngine.apply_discount(
                    order, discount, final_price, config
                )
                final_price -= applied_value

                applied_discounts.append({
                    "discount": discount.code,
                    "applied_amount": applied_value,
                })

                # Track discount usage separately
                DiscountUsageService.track_discount_usage(discount, order.user, order)

            except Exception as e:
                logger.error(f"Failed to apply discount {discount.code}: {e}")
                continue

        return final_price, applied_discounts