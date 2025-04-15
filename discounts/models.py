from django.contrib.auth import get_user_model
from core.models.base import WebsiteSpecificBaseModel
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.db.models import F
import random
import string

User = get_user_model()

class SeasonalEvent(models.Model):
    """Model for seasonal discounts (e.g., Black Friday, Cyber Monday)."""
    name = models.CharField(max_length=100, unique=True, help_text="Event name (e.g., Black Friday, Christmas Sale)")
    description = models.TextField(null=True, blank=True, help_text="Optional description of the event")
    start_date = models.DateTimeField(help_text="When the event starts")
    end_date = models.DateTimeField(help_text="When the event ends")
    is_active = models.BooleanField(default=True, help_text="Whether this event is currently active")

    class Meta:
        ordering = ['-start_date']

    def clean(self):
        """Ensure end date is after start date."""
        if self.start_date > self.end_date:
            raise ValidationError("End date must be after start date.")

    def __str__(self):
        return f"{self.name} ({self.start_date.date()} - {self.end_date.date()})"

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


    # Target Audience
    is_general = models.BooleanField(default=True, help_text="If True, discount is available for everyone")
    assigned_to_client = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Assign this discount to a specific client (leave blank for general use)"
    )

    # Seasonal event (Optional)
    seasonal_event = models.ForeignKey(
        SeasonalEvent, null=True, blank=True, on_delete=models.SET_NULL,
        help_text="Attach this discount to a seasonal event"
    )

    # Status
    is_active = models.BooleanField(default=True, help_text="Whether the discount is active")
    is_deleted = models.BooleanField(default=False, help_text="Soft delete flag for archiving discounts")

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

    @classmethod
    def mark_expired_discounts(cls):
        """Automatically deactivate expired discounts."""
        cls.objects.filter(end_date__lt=now(), is_active=True).update(is_active=False)

    @property
    def is_currently_active(self):
        """Check if the event is currently active based on dates."""
        return self.start_date <= now() <= self.end_date if self.end_date else self.start_date <= now()

    def delete(self, *args, **kwargs):
        """Soft delete instead of removing the record."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def is_valid(self, user=None):
        """Check if the discount is valid and belongs to the client (if restricted)."""
        if not self.is_active:
            return False
        if self.start_date and self.start_date > now():
            return False
        if self.end_date and self.end_date < now():
            self.is_active = False  # Auto-disable expired discount
            self.save(update_fields=['is_active'])
            return False
        if self.seasonal_event and not self.seasonal_event.is_active:
            return False  # Seasonal event is disabled, so the discount is invalid
        if not self.is_general and self.assigned_to_client and self.assigned_to_client != user:
            return False  # Prevent unauthorized clients from using a client-specific discount
        return True
    
    def clean(self):
        """Custom validation logic."""
        if Discount.objects.filter(code=self.code, website=self.website).exclude(id=self.id).exists():
            raise ValidationError("A discount with this code already exists for this website.")
        if self.discount_type == 'percentage' and (self.value <= 0 or self.value > 100):
            raise ValidationError("Percentage discount must be between 1 and 100.")
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("End date must be after the start date.")
        if self.max_uses is not None and self.max_uses <= 0:
            raise ValidationError("Max uses must be a positive number.")

    def increment_usage(self):
        if self.max_uses and self.used_count >= self.max_uses:
            raise ValidationError("This discount code has reached its maximum usage.")
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
        if Discount.objects.filter(code=self.code, website=self.website).exists():
            raise ValidationError("A discount with this code already exists for this website.")
        
        super().save(*args, **kwargs)


    def __str__(self):
        target = "Everyone" if self.is_general else f"Client: {self.assigned_to_client}"
        event_info = f" ({self.seasonal_event.name})" if self.seasonal_event else ""
        return f"{self.code} ({self.get_discount_type_display()}: {self.value}) - {target}{event_info}"