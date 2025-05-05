from datetime import datetime
from django.utils.timezone import now
from .models import DiscountUsage

class DiscountValidator:
    def __init__(self, discount, user=None, order=None):
        self.discount = discount
        self.user = user
        self.order = order
        self.errors = []

    def is_valid(self) -> bool:
        self._check_dates()
        self._check_usage_limits()
        self._check_user_usage()
        self._check_order_status()
        self._check_repeat_use_on_order()
        self._check_stackability()
        return not bool(self.errors)

    def _check_dates(self):
        if self.discount.start_date > self.discount.end_date:
            self.errors.append("Start date cannot be later than end date.")
        if self.discount.end_date < now():
            self.errors.append("Discount has already expired.")

    def _check_usage_limits(self):
        if self.discount.max_uses is not None:
            count = DiscountUsage.objects.filter(
                base_discount=self.discount
            ).count()
            if count >= self.discount.max_uses:
                self.errors.append(
                    "Discount usage exceeds the maximum allowed."
                )

    def _check_user_usage(self):
        if not self.user:
            return
        if self.discount.max_uses_per_user is not None:
            count = DiscountUsage.objects.filter(
                base_discount=self.discount,
                user=self.user
            ).count()
            if count >= self.discount.max_uses_per_user:
                self.errors.append("User usage limit exceeded.")

    def _check_order_status(self):
        if not self.order:
            return
        if self.order.status in [
            'paid', 'in progress', 'completed', 'cancelled'
        ]:
            self.errors.append(
                "Cannot apply discounts to finalized orders."
            )

    def _check_repeat_use_on_order(self):
        if not self.order:
            return
        if DiscountUsage.objects.filter(
            order=self.order,
            base_discount=self.discount
        ).exists():
            self.errors.append(
                "This discount has already been applied to this order."
            )

    def _check_stackability(self):
        if not self.order or not self.user:
            return

        applied_discounts = DiscountUsage.objects.filter(order=self.order)
        applied_codes = {d.base_discount.code for d in applied_discounts}

        # Case 1: Non-stackable discount trying to stack
        if not self.discount.stackable and applied_discounts.exists():
            self.errors.append(
                f"{self.discount.code} cannot be stacked with other discounts."
            )
            return

        # Case 2: Incompatible discounts based on stackable_with
        for applied in applied_discounts:
            if not self.discount.stackable_with.filter(id=applied.base_discount.id).exists():
                self.errors.append(
                    f"{self.discount.code} cannot be stacked with "
                    f"{applied.base_discount.code}."
                )

        # Case 3: Exceeded per-customer stack count
        if self.discount.max_stackable_uses_per_customer is not None:
            user_stack_count = DiscountUsage.objects.filter(
                base_discount=self.discount,
                user=self.user,
                discount__stackable=True
            ).count()
            if user_stack_count >= self.discount.max_stackable_uses_per_customer:
                self.errors.append(
                    f"{self.discount.code} exceeded max stackable uses "
                    f"({self.discount.max_stackable_uses_per_customer}) for user."
                )