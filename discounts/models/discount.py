from django.db import models
from django.utils.timezone import now
from django.conf import settings

from discounts.managers import DiscountQuerySet
from websites.models import Website
from .promotions import PromotionalCampaign
from discounts.services.discount_engine import DiscountEngine
from discounts.services.discount_stacking import DiscountStackingService
from discounts.validators.discount_usage_validator import DiscountUsageValidator
from discounts.validators.code_format_validator import CodeFormatValidator
User = settings.AUTH_USER_MODEL


class Discount(models.Model):
    """Represents a discount code for client orders."""

    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percent', 'Percentage'),
    ]
    DISCOUNT_ORIGIN_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
        ('system', 'System Generated'),
        ('client', 'Client Specific'),
        ('promo', 'Promotional Campaign')
    ]
    # Basic fields
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='discounts'
    )
    discount_code = models.CharField(
        max_length=50,
        unique=True,
        validators=[CodeFormatValidator()],
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
        default='percent'
    )
    origin_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_ORIGIN_CHOICES,
        default='manual'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    used_count = models.PositiveIntegerField(default=0)

    # Time constraints
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)

    # Usage constraints
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    per_user_usage_limit = models.PositiveIntegerField(null=True, blank=True)
    applies_to_first_order_only = models.BooleanField(default=False)

    # Order constraints
    min_order_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Target audience
    is_general = models.BooleanField(default=True)
    assigned_to_client = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    promotional_campaign = models.ForeignKey(
        'discounts.PromotionalCampaign',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='discounts'
    )

    objects = DiscountQuerySet.as_manager()
    # Stacking
    stackable = models.BooleanField(default=False)
    stackable_with = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        through='DiscountStackingRule',
        related_name='stackable_discount_types'
    )
    stacking_priority = models.PositiveIntegerField(default=0)
    max_discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    max_stackable_uses_per_customer = models.PositiveIntegerField(default=1)

    # Link to Promotional Campaign
    promotional_campaign = models.ForeignKey(
        'discounts.PromotionalCampaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discounts',
        help_text="Optional campaign this discount is part of"
    )
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the discount is currently active"   
    )
    is_expired = models.BooleanField(
        default=False,
        help_text="Indicates if the discount has expired"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Indicates if the discount is archived and not available for use"
    )   
    is_deleted = models.BooleanField(
        default=False,
        help_text="Indicates if the discount is soft-deleted")
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when the discount was soft-deleted"
    )

    def hard_delete(self):
        """
        Permanently delete the discount.
        """
        super().delete()

    def restore(self):
        """
        Restore a soft-deleted discount.
        """
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])
    

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['discount_code', 'website'],
                condition=models.Q(is_deleted=False),
                name='unique_discount_code_per_website'
            )
        ]
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['discount_code', 'website']),
            models.Index(fields=['start_date']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        try:
            return f"{self.discount_code} ({self.discount_value}" \
                   f"{'%' if self.discount_type == 'percent' else '$'})"
        except Exception:
            return "Discount"

    # --- Service Method Proxies ---

    def validate_discount(self):
        engine = DiscountEngine(self)
        engine.validate_clean()
        engine.validate_discount()

    def apply_discount(self, order_value):
        return DiscountEngine(self).apply_discount_to_order(order_value)

    def can_stack_with(self, other_discount):
        return DiscountStackingService._can_stack(self, other_discount)

    def check_usage_limit(self, user):
        DiscountUsageValidator.validate_per_user_limit(self, user)

    def is_valid(self, order):
        return DiscountEngine(self).is_valid_for_order(order)

    def activate(self):
        DiscountEngine(self).activate_discount()

    def deactivate(self):
        DiscountEngine(self).deactivate_discount()

    def expire(self):
        DiscountEngine(self).expire_discount()

    def check_stackable(self, user, total_discount_percent=0):
        return DiscountStackingService(self)._can_stack(
            self, user, total_discount_percent
        )

    def soft_delete(self):
        DiscountEngine(self).soft_delete()

    @classmethod
    def generate_unique_code(cls, prefix='', length=8, max_attempts=10):
        return DiscountEngine.generate_unique_discount_code(
            prefix, length, max_attempts
        )


class DiscountUsage(models.Model):
    """Tracks how and when a user used a discount."""

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='discount_usages'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    discount_code = models.CharField(max_length=50)
    discount_type = models.CharField(
        max_length=20,
        choices=Discount.DISCOUNT_TYPE_CHOICES
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='discount_usages'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    # usage_count = models.PositiveIntegerField(default=0)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'discount'],
                name='unique_discount_usage_per_user'
            )
        ]

    def __str__(self):
        try:
            return f"{self.discount_code} ({self.value}" \
                   f"{'%' if self.discount_type == 'percent' else '$'})"
        except Exception:
            return "Discount Usage"