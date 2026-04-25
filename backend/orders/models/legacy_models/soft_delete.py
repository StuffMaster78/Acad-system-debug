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





class SoftDeletableMixin(models.Model):
    """Soft deletion flags and metadata."""

    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_%(class)ss",
    )
    delete_reason = models.CharField(max_length=255, blank=True, default="")
    restored_at = models.DateTimeField(null=True, blank=True)
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="restored_%(class)ss",
    )

    class Meta:
        abstract = True

    def mark_deleted(self, user, reason=""):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.delete_reason = reason[:255] if reason else ""
        self.restored_at = None
        self.restored_by = None

    def mark_restored(self, user):
        self.is_deleted = False
        self.restored_at = timezone.now()
        self.restored_by = user
