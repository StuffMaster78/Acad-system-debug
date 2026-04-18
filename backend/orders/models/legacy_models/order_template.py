from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from datetime import timedelta
from django.db import models
from django.utils import timezone

from websites.models.websites import Website
from discounts.models.discount import Discount
from order_configs.models import WriterDeadlineConfig
from order_configs.models import AcademicLevel
from pricing_configs.models import PricingConfiguration
from django.core.exceptions import ValidationError

from orders.services.pricing_calculator import PricingCalculatorService
from orders.models.orders import Order

from django.apps import apps
from orders.order_enums import (
    OrderStatus, OrderFlags,
    DisputeStatusEnum,
    SpacingOptions,
    OrderRequestStatus
)
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL 


class OrderTemplate(models.Model):
    """Template for quick order creation."""
    
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='order_templates',
        limit_choices_to={'role': 'client'}
    )
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    
    # Template details
    name = models.CharField(max_length=200, help_text="Template name for easy identification")
    description = models.TextField(blank=True, help_text="Optional description")
    
    # Order fields (matching Order model)
    topic = models.CharField(max_length=500)
    paper_type = models.ForeignKey(
        'order_configs.PaperType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    academic_level = models.ForeignKey(
        'order_configs.AcademicLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    subject = models.ForeignKey(
        'order_configs.Subject',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    number_of_pages = models.PositiveIntegerField(default=1)
    order_instructions = models.TextField()
    
    # Additional services (stored as JSON)
    additional_services = models.JSONField(default=list, blank=True)
    
    # Preferred settings
    preferred_writer_id = models.IntegerField(null=True, blank=True)
    preferred_deadline_days = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Default number of days from now for deadline"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-last_used_at', '-created_at']
        indexes = [
            models.Index(fields=['client', 'is_active']),
            models.Index(fields=['website']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.client.username}"
    
    def mark_used(self):
        """Mark template as used and update usage count."""
        self.last_used_at = timezone.now()
        self.usage_count += 1
        self.save(update_fields=['last_used_at', 'usage_count'])

    def to_order_data(self):
        """Convert template data to a format suitable for creating an Order."""
        return {
            'topic': self.topic,
            'paper_type_id': self.paper_type_id,
            'academic_level_id': self.academic_level_id,
            'subject_id': self.subject_id,
            'number_of_pages': self.number_of_pages,
            'order_instructions': self.order_instructions,
            'additional_services': self.additional_services,
            'preferred_writer_id': self.preferred_writer_id,
            'preferred_deadline_days': self.preferred_deadline_days,
        }
    
