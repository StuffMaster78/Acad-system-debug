# my_app/services/discount_manager.py

# from .models.discount import Discount, DiscountUsage
from discounts.models.discount_configs import DiscountConfig
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import datetime


def get_discount_model():
    from discounts.models import Discount
    return Discount

def get_discount_usage_model():
    from discounts.models import DiscountUsage
    return DiscountUsage

class DiscountManager:

    def get_discount_model():
        from discounts.models import Discount
        return Discount

    def get_discount_usage_model():
        from discounts.models import DiscountUsage
        return DiscountUsage

    def __init__(self, discount_code, order_total, website, user, order):
        self.discount_code = discount_code
        self.order_total = order_total
        self.website = website  # Website for fetching specific DiscountConfig
        self.discount = None
        self.config = DiscountConfig.objects.get(website=self.website)  # Fetch config for the given website
        self.user = user
        self.order = order

    def _fetch_discount(self):
        """ Fetches the discount based on the discount code """
        discount = DiscountManager.get_discount_model
        try:
            self.discount = discount.objects.get(code=self.discount_code)
        except discount.DoesNotExist:
            raise ValidationError("Invalid discount code.")
    
    def _check_validity(self):
        """ Check if the discount is valid (e.g., active, not expired) """
        if not self.discount.is_active:
            raise ValidationError("This discount is not active.")
        
        if self.discount.expiration_date and self.discount.expiration_date < datetime.now():
            raise ValidationError("This discount has expired.")

    def _check_stackable_limit(self, used_discounts_count):
        """ Check if the number of stackable discounts exceeds the limit """
        if used_discounts_count >= self.config.max_stackable_discounts:
            raise ValidationError(
                f"Maximum of {self.config.max_stackable_discounts} discount codes can be applied."
            )
    
    def _check_discount_threshold(self, new_order_total):
        """ Check if additional discounts can be applied based on threshold """
        if new_order_total < self.config.discount_threshold:
            raise ValidationError(
                f"Order total after first discount must exceed {self.config.discount_threshold} to apply additional discounts."
            )

    def _apply_discount(self):
        """ Applies the discount to the order total """
        if self.discount.discount_type == 'percentage':
            if self.discount.value > self.config.max_discount_percent:
                raise ValidationError(f"Discount cannot exceed {self.config.max_discount_percent}%")
            return self.order_total * (1 - Decimal(self.discount.value) / 100)
        elif self.discount.discount_type == 'fixed':
            return self.order_total - Decimal(self.discount.value)
        else:
            raise ValidationError("Unknown discount type.")
    
    def _apply_seasonal_discount(self):
        """ Applies the seasonal discount if it's active """
        if self.config.seasonal_discount_active:
            seasonal_discount = Decimal(self.config.seasonal_discount_value) / 100
            seasonal_discount_value = self.order_total * seasonal_discount
            return self.order_total - seasonal_discount_value
        return self.order_total

    def validate_and_apply(self, used_discounts_count):
        """ Main method to validate and apply the discount """
        self._fetch_discount()
        self._check_validity()
        self._check_stackable_limit(used_discounts_count)
        
        new_total = self._apply_discount()

        # Apply the seasonal discount if active
        new_total = self._apply_seasonal_discount()

        # Check if this new total exceeds the threshold for additional discounts
        self._check_discount_threshold(new_total)
        
        return new_total

    def apply_discount_usage(self):
        """ Marks the discount as used """
        discount_usage = DiscountManager.get_discount_usage_model()
        discount_usage.objects.create(
            discount=self.discount,
            user=self.user,
            order=self.order
        )