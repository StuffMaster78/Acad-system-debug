from django.contrib.auth import get_user_model
from django.db import models
from websites.models import Website
from django.utils.timezone import now
from django.db.models import F
from .seasonal_event import SeasonalEvent
from users.models import User
import random
import string

from services import DiscountService, DiscountStackingService

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
        Website,
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

    def __str__(self):
        return f"{self.code} ({self.percentage}% off)"
    
    def validate_discount(self):
        """Validates the discount using DiscountService."""
        service = DiscountService(self)
        service.validate_clean()
        service.validate_discount()

    def apply_discount(self, order_value):
        """Apply the discount using DiscountService."""
        service = DiscountService(self)
        return service.apply_discount(order_value)

    def can_stack_with(self, other_discount):
        """Check if this discount can stack with another using DiscountStackingService."""
        return DiscountStackingService.can_stack(self, other_discount)

    def check_usage_limit(self, user):
        """Check usage limit using DiscountService."""
        service = DiscountService(self)
        service.check_usage_per_user_limit(user)

    def is_valid(self, order):
        """Check if this discount is valid for an order."""
        service = DiscountService(self)
        return service.is_valid_for_order(order)

    def activate(self):
        """Activate the discount using DiscountService."""
        service = DiscountService(self)
        service.activate_discount()

    def deactivate(self):
        """Deactivate the discount using DiscountService."""
        service = DiscountService(self)
        service.deactivate_discount()

    def expire(self):
        """Expire the discount using DiscountService."""
        service = DiscountService(self)
        service.expire_discount()

    def check_stackable(self, user, total_discount_percent=0):
        """Check if discount can be stacked."""
        service = DiscountService(self)
        return service.can_be_stacked(user, total_discount_percent)

    @classmethod
    def generate_unique_code(cls, prefix="", length=8, max_attempts=10):
        """Generate a unique discount code."""
        return DiscountService.generate_unique_code(prefix, length, max_attempts)

    def soft_delete(self):
        """Soft delete the discount."""
        service = DiscountService(self)
        service.soft_delete()
    

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