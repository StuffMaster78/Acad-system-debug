from core.models.base import WebsiteSpecificBaseModel
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now


class Discount(WebsiteSpecificBaseModel):
    DISCOUNT_TYPE_CHOICES = [
        ('fixed', 'Fixed Amount'),
        ('percentage', 'Percentage'),
    ]

    # Basic details
    code = models.CharField(max_length=50, unique=True, help_text="Unique discount code")
    description = models.TextField(null=True, blank=True, help_text="Description of the discount")

    # Discount configuration
    discount_type = models.CharField(
        max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage', help_text="Type of discount"
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Discount value (e.g., $10 or 15%)"
    )
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum number of uses allowed")
    used_count = models.PositiveIntegerField(default=0, help_text="Number of times the code has been used")

    # Restrictions
    start_date = models.DateTimeField(default=now, help_text="Start date for the discount")
    end_date = models.DateTimeField(null=True, blank=True, help_text="End date for the discount")
    min_order_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, help_text="Minimum order value to apply the discount"
    )

    # Status
    is_active = models.BooleanField(default=True, help_text="Whether the discount is active")

    class Meta:
        ordering = ['-start_date']
        unique_together = ('code', 'website')  # Ensure unique codes per website

    def clean(self):
        """Custom validation logic."""
        if self.discount_type == 'percentage' and (self.value <= 0 or self.value > 100):
            raise ValidationError("Percentage discount value must be between 0 and 100.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after the start date.")

    def is_valid(self):
        """Check if the discount is valid (active and within date range)."""
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now():
            return False
        if self.end_date and self.end_date < now():
            return False
        return True

    def increment_usage(self):
        """Increment the used count of the discount."""
        if self.max_uses and self.used_count >= self.max_uses:
            raise ValidationError("This discount code has reached its maximum usage.")
        self.used_count += 1
        self.save()

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()}: {self.value})"
