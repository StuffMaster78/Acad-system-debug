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
from order_pricing_core.models import PricingConfiguration
from django.core.exceptions import ValidationError

from orders.services.pricing_calculator import PricingCalculatorService
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


class ClientFeedback(models.Model):
    """
    Stores feedback from a client about an order experience.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name="client_feedbacks"
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="order_feedbacks"
    )
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Optional rating from 1 (worst) to 5 (best)."
    )
    comment = models.TextField(
        blank=True,
        help_text="Optional client comment about the order."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback from {self.client} on Order #{self.order.id}"
    
    class Meta:
        unique_together = ('order', 'client')
    def save(self, *args, **kwargs):
        # Auto-set website from order if not set
        if not self.website_id and self.order_id:
            self.website = self.order.website
        super().save(*args, **kwargs)