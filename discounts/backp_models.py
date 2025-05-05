from django.contrib.auth import get_user_model
from core.models.base import WebsiteSpecificBaseModel
from django.db import models
from websites.models import Website
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import F
import random
import string

User = get_user_model()

class SeasonalEvent(models.Model):
    """
    Represents a seasonal event that discounts can be associated with.
    Examples: Summer, Black Friday, CyberMonday etc.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='seasonal_event'
    )
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Event name (e.g., Black Friday, Christmas Sale)"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description of the event"
    )
    start_date = models.DateTimeField(help_text="When the event starts")
    end_date = models.DateTimeField(help_text="When the event ends")
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this event is currently active"
    )

    class Meta:
        ordering = ['-start_date']

    def clean(self):
        """Ensure end date is after start date."""
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

    def __str__(self):
        return f"{self.name} ({self.start_date.date()} - {self.end_date.date()})"

class Discount(models.Model):
    """
    Represents a discount that can be applied to orders, including seasonal 
    discounts and usage tracking.
    """
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ]

    DISCOUNT_ORIGIN_CHOICES = [
        ('manual', 'Manual'),
        ('seasonal', 'Seasonal Event'),
        ('promo', 'Promotional Campaign'),
    ]
    # Basic details
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique discount code"
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Description of the discount"
    )

    # Discount configuration
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage',
        help_text="Type of discount"
    )
    origin_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_ORIGIN_CHOICES,
        default='manual',
        help_text="Where or why the discount was created"
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Discount value (e.g., $10 or 15%)"
    )
    max_uses = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Maximum number of uses allowed"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times the code has been used"
    )

    # Restrictions
    start_date = models.DateTimeField(
        default=now,
        help_text="Start date for the discount"
    )
    end_date = models.DateTimeField(
        null=True, blank=True,
        help_text="End date for the discount"
    )
    min_order_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Minimum order value to apply the discount"
    )
    max_discount_value = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Absolute cap on discount value"
    )

    applies_to_first_order_only = models.BooleanField(default=False)


    # Target Audience
    is_general = models.BooleanField(
        default=True,
        help_text="If True, discount is available for everyone"
    )
    assigned_to_client = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        help_text="Assign this discount to a specific client (leave blank for general use)"
    )

    # Seasonal event (Optional)
    seasonal_event = models.ForeignKey(
        SeasonalEvent, null=True,
        blank=True, on_delete=models.SET_NULL,
        help_text="Attach this discount to a seasonal event"
    )

    # Stacking fileds
    max_discount_percent = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        help_text="Maximum percentage discount allowed when stacking"
    )
    stackable = models.BooleanField(default=False)
    stackable_with = models.ManyToManyField(
        'self',
        blank=True,
        related_name='stackable_discount_types',
        through='DiscountStackingRule',
        help_text="Defines which discount types this discount can be combined with."
    )
    max_stackable_uses_per_customer = models.PositiveIntegerField(
        default=1,
        help_text="Maximum number of times a customer can stack this discount"
    )
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the discount is active"
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag for archiving discounts"
    )

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=["code", "website"], 
                condition=models.Q(is_deleted=False),  # Ignore deleted discounts
                name="unique_discount_code_per_website"
            )
        ]
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code', 'website']),
            models.Index(fields=['start_date']),
        ]

    def clean(self):
        """Custom validation logic."""
        if Discount.objects.filter(
            code=self.code,
            website=self.website
        ).exclude(id=self.id).exists():
            raise ValidationError(
                "A discount with this code already exists for this website."
            )
        if self.discount_type == 'percentage' and (self.value <= 0 or self.value > 100):
            raise ValidationError(
                "Percentage discount must be between 1 and 100."
            )
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(
                "End date must be after the start date."
            )
        if self.max_uses is not None and self.max_uses <= 0:
            raise ValidationError(
                "Max uses must be a positive number."
            )
        if not self.stackable and Discount.objects.filter(
            website=self.website,
            stackable=True
        ).exists():
                raise ValidationError(
                    "This discount cannot be stacked with others."
                )
        super().clean()


    @classmethod
    def mark_expired_discounts(cls):
        """Automatically deactivate expired discounts."""
        cls.objects.filter(
            end_date__lt=now(),
            is_active=True
        ).update(is_active=False)

    @property
    def is_currently_active(self):
        """Check if the event is currently active based on dates."""
        now_time = now()
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now_time:
            return False
        if self.end_date and self.end_date < now_time:
            return False
        return True
    
    def is_valid(self, user=None):
        """Check if the discount is valid and belongs to the client (if restricted)."""
        if not self.is_currently_active:
            return False
        if self.seasonal_event and not self.seasonal_event.is_active:
            return False  # Seasonal event is disabled, so the discount is invalid
        if self.applies_to_first_order_only and user.orders.exists():
            return False  # Discount is for first-time orders only
        if not self.is_general and self.assigned_to_client and self.assigned_to_client != user:
            return False  # Prevent unauthorized clients from using a client-specific discount
        
        return True
    
    def is_valid_for_order(self, order, user=None):
        if not self.is_currently_active:
            return False
        if self.min_order_value and order.total < self.min_order_value:
            return False
        # Check if the discount applies to first-time orders only
        if self.applies_to_first_order_only:
            # Check if the user has placed any orders before
            if order.user.orders.count() > 0:  # Assuming 'orders' is related to the User model
                return False  # Not a first-time order
        return True
    
    def can_be_stacked(self, user=None, total_discount_percent=0):
        """
        Check if this discount can be stacked with others.
        """
        from .models import DiscountUsage

        # Can't stack non-stackable discounts
        if not self.stackable:
            return False

        # Check if the discount exceeds the max discount limit
        if self.max_discount_percent and total_discount_percent + self.value > self.max_discount_percent:
            return False

        # Check if the discount has exceeded the max usage count
        if self.max_uses and self.used_count >= self.max_uses:
            return False

        # Check if the customer has used this discount too many times
        if self.max_stackable_uses_per_customer:
            usage_count = DiscountUsage.objects.filter(user=user, discount=self).count()
            if usage_count >= self.max_stackable_uses_per_customer:
                return False

        return True

    
    def can_stack_with(self, other_discount):
        """Check if the discount can stack with another based on type."""
        return other_discount in self.stackable_with.all()
    
    def validate_max_stackable_uses(self, user):
        from .models import DiscountUsage
        if self.max_stackable_uses_per_customer is None:
            return True
        used_count = DiscountUsage.objects.filter(user=user, discount=self).count()
        if used_count >= self.max_stackable_uses_per_customer:
            raise ValidationError(
                f"You've already used this discount {self.max_stackable_uses_per_customer} times."
            )
        return True
    
    def delete(self, *args, **kwargs):
        """Soft delete instead of removing the record."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
    
    def apply_discount(self, order_value):
        """Apply the discount to the order value."""
        if self.discount_type == 'fixed':
            discount = self.value
        else:
            discount = order_value * (self.value / 100)
        if self.max_discount_value and discount > self.max_discount_value:
            return self.max_discount_value
        return discount
    
    
    def increment_usage(self):
        if self.max_uses and self.used_count >= self.max_uses:
            raise ValidationError(
                "This discount code has reached its maximum usage."
            )
        Discount.objects.filter(id=self.id).update(used_count=F('used_count') + 1)

    @property
    def usage_percentage(self):
        """Returns the percentage of the discount usage."""
        if not self.max_uses:
            return None  # No limit set
        return round((self.used_count / self.max_uses) * 100, 2)


    @staticmethod
    def generate_unique_code(prefix="", length=8, max_attempts=10):
        """Generate a truly unique discount code with a limit on attempts."""
        for _ in range(max_attempts):
            code = f"{prefix}{''.join(random.choices(string.ascii_uppercase + string.digits, k=length))}"
            if not Discount.objects.filter(code=code).exists():
                return code
        raise RuntimeError("Failed to generate a unique discount code after multiple attempts.")

    def save(self, *args, **kwargs):
        """Ensure the discount code is unique within the website and generate one if empty."""
        if not self.code:
            self.code = self.generate_unique_code()
        
        # Ensure uniqueness within the same website
        if Discount.objects.filter(
            code=self.code,
            website=self.website
        ).exists():
            raise ValidationError(
                "A discount with this code already exists for this website."
            )
        


    def __str__(self):
        target = "Everyone" if self.is_general else f"Client: {self.assigned_to_client}"
        event_info = f" ({self.seasonal_event.name})" if self.seasonal_event else ""
        return f"{self.code} ({self.get_discount_type_display()}: {self.value}) - {target}{event_info}"
    
class DiscountStackingRule(models.Model):
    """
    A model that links discounts that can be combined.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount_stacking_rule'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE
    )
    stackable_discount = models.ForeignKey(
        Discount,
        related_name='stackable_discounts',
        on_delete=models.CASCADE
    )
class DiscountUsage(models.Model):
    """
    A model for tracking the ussage of discounts to
    prevent overuse
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='discount_usage'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    base_discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.CASCADE,
        related_name="base_discount_rules"
    )
    stackable_with = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.CASCADE,
        related_name="stackable_discount_rules"
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("base_discount", "stackable_with")

    def __str__(self):
        return f"{self.base_discount.code} can stack with {self.stackable_with.code}"