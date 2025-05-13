from django.db import models
from django.utils.timezone import now
from django.apps import apps
from django.conf import settings
from websites.models import Website
from .seasonal_event import SeasonalEvent
from discounts.services import DiscountEngine, DiscountStackingService




User = settings.AUTH_USER_MODEL


class Discount(models.Model):
    """
    Represents a discount code that can be applied to orders,
    including seasonal events and optional stacking rules.
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
    # @staticmethod
    # def get_website_model():
    #     return apps.get_model('websites', 'Website')

    # # @staticmethod
    # # def get_order_model():
    # #     return apps.get_model('orders', 'Order')
    
    # Website = get_website_model()
    # Basic info
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='discounts'
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
        help_text="How this discount was generated"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Value of the discount (e.g., 10 for $10 or 15%)"
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of times this discount can be used"
    )
    used_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this discount has been used"
    )

    # Date constraints
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)

    # Order constraints
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum order total required to use this discount"
    )
    max_discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum absolute discount that can be applied"
    )
    applies_to_first_order_only = models.BooleanField(default=False)

    # Target audience
    is_general = models.BooleanField(default=True)
    assigned_to_client = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Specific user this discount is assigned to"
    )

    seasonal_event = models.ForeignKey(
        SeasonalEvent,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="The seasonal event this discount applies to (optional)"
    )

    # Stacking logic
    stackable = models.BooleanField(
        default=False,
        help_text="Is this discount code stackable?"
    )
    stackable_with = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        through='DiscountStackingRule',
        related_name='stackable_discount_types'
    )
    max_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Max percent discount when stacking (e.g., 30%)"
    )
    max_stackable_uses_per_customer = models.PositiveIntegerField(default=1)

    # Status
    expiry_date = models.DateTimeField(
        null=True, blank=True, help_text="The date the discount expires (optional)"
    )
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="The maximum number of times this discount can be used"
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=["code", "website"],
                condition=models.Q(is_deleted=False),
                name="unique_discount_code_per_website"
            )
        ]
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['code', 'website']),
            models.Index(fields=['start_date']),
        ]

    def __str__(self):
        try:
            return f"{self.code} ({self.value}{'%' if self.discount_type == 'percentage' else '$'})"
        except Exception:
            return "Discount"

    # Service method proxies
    def validate_discount(self):
        DiscountEngine(self).validate_clean()
        DiscountEngine(self).validate_discount()

    def apply_discount(self, order_value):
        return DiscountEngine(self).apply_discount(order_value)

    def can_stack_with(self, other_discount):
        return DiscountStackingService.can_stack(self, other_discount)

    def check_usage_limit(self, user):
        DiscountEngine(self).check_usage_per_user_limit(user)

    def is_valid(self, order):
        return DiscountEngine(self).is_valid_for_order(order)

    def activate(self):
        DiscountEngine(self).activate_discount()

    def deactivate(self):
        DiscountEngine(self).deactivate_discount()

    def expire(self):
        DiscountEngine(self).expire_discount()

    def check_stackable(self, user, total_discount_percent=0):
        return DiscountEngine(self).can_be_stacked(user, total_discount_percent)

    def soft_delete(self):
        DiscountEngine(self).soft_delete()

    @classmethod
    def generate_unique_code(cls, prefix: str = "", length: int = 8, max_attempts: int = 10):
        return DiscountEngine.generate_unique_discount_code(prefix, length, max_attempts)


class DiscountUsage(models.Model):
    """
    Tracks how and when a user used a discount.
    Prevents overuse or abuse of discounts.
    """
    # @staticmethod
    # def get_website_model():
    #     return apps.get_model('websites', 'Website')

    # @staticmethod
    # def get_order_model():
    #     return apps.get_model('orders', 'Order')
    
    # Website = get_website_model()

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='discount_usages'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount = models.ForeignKey(
        "discounts.Discount",
        on_delete=models.CASCADE,
        related_name="usages"
    )
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="The number of times this discount has been used"
    )
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "discount")

    def __str__(self):
        return f"{self.user} used {self.discount.code} on {self.used_at}"