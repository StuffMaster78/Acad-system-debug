import random
import string
from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from discounts.models import Discount, DiscountUsage, SeasonalEvent
from discounts.validators import DiscountValidator
from django.db.models import F
from django.db.models import Q
from decimal import Decimal, ROUND_HALF_UP
from notifications_system.services.send_notification import (
    notify_admin_of_error
)
from users.models import User
from orders.models import Order
import logging
from .seasonal_events import SeasonalEventService
from .discount_stacking import DiscountStackingService
from orders.models import OrderDiscount

# Set up logging
logger = logging.getLogger(__name__)


class DiscountService:
    def __init__(self, discount: Discount, order: Order, user: User):
        self.discount = discount
        self.user = user
        # self.discounts = discounts
        self.applied = []
        self.final_price = order.total_price

    def validate_clean(self):
        """Custom validation logic."""
        exists = Discount.objects.filter(
            code=self.discount.code,
            website=self.discount.website
        ).exclude(id=self.discount.id).exists()
        if exists:
            raise ValidationError(
                "A discount with this code already exists for this website."
            )
        if self.discount.discount_type == 'percentage':
            if (self.discount.value <= 0 or self.discount.value > 100):
                raise ValidationError(
                    "Percentage discount must be between 1 and 100."
                )
        if self.discount.start_date and self.discount.end_date:
            if self.discount.start_date > self.discount.end_date:
                raise ValidationError(
                    "End date must be after the start date."
                )
        if self.discount.max_uses is not None and self.discount.max_uses <= 0:
            raise ValidationError(
                "Max uses must be a positive number."
            )
        if not self.discount.stackable:
            if Discount.objects.filter(
            website=self.discount.website,
            stackable=True
            ).exists():
                    raise ValidationError(
                        "This discount cannot be stacked with others."
                    )

    def validate_discount(self) -> None:
        """Validates the discount before saving it."""
        validator = DiscountValidator(self.discount)
        if not validator.is_valid():
            raise ValidationError(validator.errors)

    def activate_discount(self) -> None:
        """Activates the discount if it's valid."""
        self.validate_discount()
        if not self.discount.is_active:
            self.discount.is_active = True
        self.discount.save()

    def deactivate_discount(self) -> None:
        """Deactivates the discount."""
        if self.discount.is_active:
            self.discount.is_active = False
        self.discount.save()

    def expire_discount(self) -> None:
        """Expires the discount based on its dates."""
        if self.discount.end_date:
            if self.discount.end_date < timezone.now():
                self.deactivate_discount()


    def check_usage_per_user_limit(self, user) -> None:
        """Checks if the discount has been used by a user beyond their limit."""
        user_used_count = DiscountUsage.objects.filter(
            user=user,
            discount=self.discount
        ).count()
        if user_used_count >= self.discount.max_uses_per_user:
            raise ValidationError(
                f"You've already used this discount {self.discount.max_uses_per_user} times."
            )
        
    def apply_discount(self, order_value):
        """Calculate the discount amount from order value."""
        if self.discount.discount_type == 'fixed':
            discount = self.discount.value
        else:
            discount = order_value * (self.discount.value / 100)

        if self.discount.max_discount_value:
            discount = min(discount, self.discount.max_discount_value)

        return Decimal(discount).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    def increment_usage(self):
        """Track usage count."""
        if (self.discount.max_uses and
                self.discount.used_count >= self.discount.max_uses):
            raise ValidationError("Discount usage limit reached.")
        Discount.objects.filter(id=self.discount.id).update(
            used_count=F("used_count") + 1
        )

    @property
    def usage_percentage(self):
        """Return % usage of the discount."""
        if not self.discount.max_uses:
            return None
        return round(
            (self.discount.used_count / self.discount.max_uses) * 100, 2
        )
    
    @classmethod
    def mark_expired_discounts(cls):
        """Automatically deactivate expired discounts."""
        cls.objects.filter(
            end_date__lt=now(),
            is_active=True
        ).update(is_active=False)
    
    def is_valid_for_order(self, order, user=None):
        """Check if discount is valid for a given order."""
        if not self.is_currently_active():
            return False
        if self.discount.min_order_value:
            if order.total < self.discount.min_order_value:
                return False
        if self.discount.applies_to_first_order_only:
            if order.user.orders.exists():
                return False
        return True
    
    def validate_unique_code(self):
        """Ensure uniqueness within the same website."""
        if Discount.objects.filter(
            code=self.discount.code,
            website=self.discount.website
        ).exists():
            raise ValidationError(
                "A discount with this code already exists for this website."
            )
        
    def duplicate_discounts(discounts_queryset):
        new_discounts = []
        for discount in discounts_queryset:
            discount.pk = None
            discount.code += "_" + ''.join(random.choices(string.ascii_uppercase, k=4))
            discount.start_date = now()
            discount.end_date = None
            discount.is_active = True
            discount.used_count = 0
            new_discounts.append(discount)
        return Discount.objects.bulk_create(new_discounts)
        
    def soft_delete(self):
        """Soft delete instead of removing the record."""
        self.discount.is_deleted = True
        self.discount.save(update_fields=['is_deleted'])
        
    def check_discount_stacking(self, user):
        """Check if the discount can be stacked with others for the user."""
        if not self.discount.stackable:
            return self.discount

        used_discounts = DiscountUsage.objects.filter(
            user=user
        ).values_list('discount', flat=True)

        # Ensure that no discounts are used that violate the stacking rule
        stackable_discounts = self.discount.stackable_with.all()
        for stackable_discount in stackable_discounts:
            if stackable_discount.id not in used_discounts:
                raise ValidationError(
                    f"{stackable_discount.code} cannot be stacked with the current discounts."
                )

        return self.discount

    def can_be_stacked(self, user=None, total_discount_percent=0):
        """Check if this discount can be stacked with others."""
        # Can't stack non-stackable discounts
        if not self.discount.stackable:
            return False

        # Check if the discount exceeds the max discount limit
        if self.discount.max_discount_percent:
            if total_discount_percent + self.discount.discount_value() > self.discount.max_discount_percent:
                return False

        # Check if the discount has exceeded the max usage count
        if self.discount.max_uses and self.discount.used_count >= self.discount.max_uses:
            return False

        # Check if the customer has used this discount too many times
        if self.discount.max_stackable_uses_per_customer:
            usage_count = DiscountUsage.objects.filter(user=user, discount=self.discount).count()
            if usage_count >= self.discount.max_stackable_uses_per_customer:
                return False

        return True
    
    def can_stack_with(self, other_discount):
        """Check if the discount can stack with another based on type."""
        return other_discount in self.discount.stackable_with.all()

    def validate_max_stackable_uses(self, user):
        """Validate that the discount can still be used by the user, based on stackable limit."""
        if self.discount.max_stackable_uses_per_customer is None:
            return True
        used_count = DiscountUsage.objects.filter(user=user, discount=self.discount).count()
        if used_count >= self.discount.max_stackable_uses_per_customer:
            raise ValidationError(
                f"You've already used this discount {self.discount.max_stackable_uses_per_customer} times."
            )
        return True
    
    @staticmethod
    def generate_unique_code(prefix="", length=8, max_attempts=10):
        """Generate a unique discount code with a limit on attempts."""
        for _ in range(max_attempts):
            code = prefix + ''.join(random.choices(
                string.ascii_uppercase + string.digits, k=length
            ))
            if not Discount.objects.filter(code=code).exists():
                return code
        raise RuntimeError("Failed to generate a unique discount code after multiple attempts.")

    def is_currently_active(self):
        """Check if the discount is currently active based on dates."""
        now_time = now()
        if not self.discount.is_active:
            return False
        if self.discount.start_date and self.discount.start_date > now_time:
            return False
        if self.discount.end_date and self.discount.end_date < now_time:
            return False
        return True
    

    def is_valid(self, user=None):
        """Check if the discount is valid and belongs to the client (if restricted)."""
        if not self.is_currently_active():
            return False
        if self.discount.seasonal_event and not self.discount.seasonal_event.is_active:
            return False  # Seasonal event is disabled, so the discount is invalid
        if self.discount.applies_to_first_order_only and user.orders.exists():
            return False  # Discount is for first-time orders only
        if not self.discount.is_general:
            if self.discount.assigned_to_client:
                if self.discount.assigned_to_client != user:
                    return False  # Prevent unauthorized clients from using a client-specific discount
        
        return True


    # @staticmethod
    # def apply_discounts_to_order(order, codes, user):
    #     """
    #     Apply one or more discounts to an order.
    #     Returns final price and breakdown.
    #     """
    #     errors = []

    #     if not codes:
    #         return {"final_price": order.total_price, "discounts_applied": []}

    #     try:
    #         # Get active discounts
    #         discounts = Discount.objects.filter(
    #             Q(code__in=codes),
    #             is_active=True,
    #             start_date__lte=now(),
    #         ).select_related("seasonal_event")

    #         if not discounts:
    #             raise ValueError("No valid discounts found.")

    #         # Validate codes
    #         found_codes = set(d.code for d in discounts)
    #         invalid = set(codes) - found_codes
    #         if invalid:
    #             raise ValueError(f"Invalid discount codes: {', '.join(invalid)}")

    #         original_price = order.total_price
    #         final_price = original_price
    #         applied = []
    #         stackable_discount = None

    #         # # Seasonal service handles the seasonal event logic
    #         # seasonal_service = SeasonalEventService()

    #         # Stacking service handles the logic of which discounts can stack
    #         stacking_service = DiscountStackingService()

    #         for d in sorted(discounts, key=lambda d: d.discount_type):  # % first
    #             if d.min_order_value and original_price < d.min_order_value:
    #                 continue

    #             # Check if there are seasonal events affecting the discount
    #             if SeasonalEventService.is_discount_applicable(d):
    #                 # Handle stackable logic using StackingService
    #                 stackable_discount = stacking_service.get_stackable_discounts(d)

    #                 if stackable_discount:
    #                     applied.append({
    #                         "code": stackable_discount.code,
    #                         "type": stackable_discount.discount_type,
    #                         "value": float(stackable_discount.value),
    #                         "amount": float(stackable_discount.value),
    #                     })

    #                 # Apply the discount
    #                 if d.discount_type == "percentage":
    #                     raw = final_price * (d.value / Decimal(100))
    #                 else:
    #                     raw = d.value

    #                 if d.max_discount_value:
    #                     raw = min(raw, d.max_discount_value)

    #                 raw = Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    #                 final_price = max(Decimal("0.00"), final_price - raw)

    #                 applied.append({
    #                     "code": d.code,
    #                     "type": d.discount_type,
    #                     "value": float(d.value),
    #                     "amount": float(raw),
    #                 })

    #                 # Track discount usage
    #                 DiscountUsage.objects.create(
    #                     website=order.website,
    #                     user=user,
    #                     base_discount=d,
    #                     stackable_with=stackable_discount if stackable_discount else None
    #                 )

    #     except ValueError as e:
    #         logger.error(f"ValueError applying discounts to order: {str(e)}")
    #         errors.append(str(e))
    #         return {
    #             "final_price": float(order.total_price),
    #             "discounts_applied": [],
    #             "errors": errors,
    #         }
    #     except Exception as e:
    #         logger.error(f"Unexpected error applying discounts to order: {str(e)}")
    #         notify_admin_of_error(str(e))
    #         errors.append(f"Unexpected error occurred: {str(e)}")
    #         return {
    #             "final_price": float(order.total_price),
    #             "discounts_applied": [],
    #             "errors": errors,
    #         }

    #     # Return the applied discount details
    #     return {
    #         "original_price": float(original_price),
    #         "final_price": float(final_price),
    #         "discounts_applied": applied,
    #         "errors": errors,
    #     }



class DiscountFetcherService:
    @staticmethod
    def fetch_by_codes(codes, website, client=None):
        """
        Fetches discounts for the client, considering whether they
        are general or client-specific.
        
        Args:
            codes (list): List of discount codes.
            website (Website): The website to which the discounts are applied.
            client (User, optional): The client for whom the discount is being applied.
            
        Returns:
            list: List of discounts applicable to the client.
        """
        # Fetch all active general and client-specific discounts in one query
        discounts = Discount.objects.filter(
            code__in=codes,
            is_active=True,
            website=website,
            start_date__lte=now()
        ).select_related('seasonal_event')


        if client:
            client_discounts = Discount.objects.filter(
                code__in=codes,
                assigned_to_client=client,
                is_active=True,
                website=website,
                start_date__lte=now()
            ).select_related('seasonal_event')
            discounts = discounts | client_discounts  # Union the querysets
        # Check for any codes that didn't return a valid discount
        found_codes = set(d.code for d in discounts)
        missing_codes = set(codes) - found_codes
        if missing_codes:
            raise ValidationError(f"Invalid discount codes: {', '.join(missing_codes)}")

        return discounts


class DiscountApplicatorService:
    def __init__(self, order, user, discounts):
        self.order = order
        self.user = user
        self.discounts = discounts
        self.applied = []
        self.final_price = order.total_price

    def apply(self):
        """
        Applies valid, stackable discounts to the order.
        Clears any previously applied discounts.
        """
        applicable = self._filter_valid_discounts()
        stackable_sets = self._resolve_stackable_sets(applicable)
        OrderDiscount.objects.filter(order=self.order).delete()
        for discount in stackable_sets:
            self._apply_single(discount)
        return self._response()

    def _filter_valid_discounts(self):
        """
        Filters discounts to only those valid for the given user.
        """
        return [d for d in self.discounts if DiscountService(d).is_valid(self.user)]

    def _resolve_stackable_sets(self, discounts):
        """
        Picks the maximum set of mutually stackable discounts.
        """
        # Pick max mutually stackable set (simplified for now)
        selected = []
        discounts.sort(key=lambda d: d.code)
        for d in discounts:
            if all(DiscountStackingService.can_stack(d, s) for s in selected):
                selected.append(d)
        return selected

    def _apply_single(self, discount):
        """
        Applies a single discount, persists it, and updates final price.
        """
        discount_service = DiscountService(discount)
        discount_value = discount_service.apply_discount(
            self.final_price
        )
        discount_value = max(
            Decimal("0.00"),
            discount_value
        )

        if discount_value <= 0:
            return

        self.final_price = max(
            Decimal("0.00"),
            self.final_price - discount_value
        )

        # Save applied discount to DB
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

    def _response(self):
        """
        Returns the result of the discount application.
        """
        return {
            "original_price": float(self.order.total_price),
            "final_price": float(self.final_price),
            "discounts_applied": self.applied,
        }


class DiscountUsageTracker:
    """
    Service class for tracking and untracking discount usage
    against specific orders and users.
    """
    @staticmethod
    def track(discounts, order, user):
        """
        Records usage of each discount for the given order and user,
        and increments the used_count on the discount.

        Args:
            discounts (list): List of Discount instances to track.
            order (Order): The order to associate with the usage.
            user (User): The user who used the discounts.
        """
        for d in discounts:
            DiscountUsage.objects.create(
                user=user,
                website=order.website,
                base_discount=d,
                order=order  # Make sure this field exists
            )
            Discount.objects.filter(id=d.id).update(
                used_count=F("used_count") + 1
            )
    @staticmethod
    def untrack(order):
        """
        Reverts usage of any discounts tied to the given order.
        This is typically called on refund to make the discount
        reusable.

        Args:
            order (Order): The order whose discount usage should
                           be removed.
        """
        usages = DiscountUsage.objects.filter(order=order)
        count = usages.count()
        if count:
            logger.info(
                f"Untracking {count} discount usages for order {order.id}"
            )
            # Decrement used_count per discount
            for usage in usages:
                Discount.objects.filter(
                    id=usage.base_discount_id
                ).update(
                    used_count=F("used_count") - 1
                )
            usages.delete()
        else:
            logger.info(
                f"No discount usages found to untrack for order {order.id}"
            )