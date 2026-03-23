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



class OrderTransitionLog(models.Model):
    """
    Logs all status transitions for an order.
    This is useful for auditing and tracking changes in order status.
    """
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="transitions"
    )
    user = models.ForeignKey(
        'users.User',
        null=True, blank=True,
        on_delete=models.SET_NULL
    )
    old_status = models.CharField(max_length=32)
    new_status = models.CharField(max_length=32)
    action = models.CharField(max_length=64)  # e.g. "mark_paid", "auto_expire"
    is_automatic = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    meta = models.JSONField(null=True, blank=True)  # optional context or payload

    class Meta:
        ordering = ['-timestamp']


class OrderPricingSnapshot(models.Model):
    """
    Captures a snapshot of the order's pricing details at a specific time.
    This is useful for auditing and historical reference.
    """
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="pricing_snapshot"
    )
    pricing_data = models.JSONField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pricing Snapshot for Order #{self.order.id} at {self.calculated_at}"
    

class WriterReassignmentLog(models.Model):
    """
    Logs all writer reassignments for transparency and audit.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="reassignment_logs"
    )
    previous_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_lost"
    )
    new_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_gained"
    )
    reassigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reassignments_made"
    )
    reason = models.TextField(
        blank=True,
        help_text="Optional reason for the reassignment."
    )
    created_at = models.DateTimeField(
        default=now,
        help_text="When the reassignment occurred."
    )

    class Meta:
        verbose_name = "Writer Reassignment Log"
        verbose_name_plural = "Writer Reassignment Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.order.id} reassigned to {self.new_writer}"
    
    class Meta:
        verbose_name = "Order Pricing Snapshot"
        verbose_name_plural = "Order Pricing Snapshots"
        ordering = ["-calculated_at"]

    
class OrderPricingSnapshot(models.Model):
    """
    Captures a snapshot of the order's pricing details at a specific time.
    This is useful for auditing and historical reference.
    """
    order = models.OneToOneField(
        "orders.Order", on_delete=models.CASCADE, related_name="pricing_snapshot"
    )
    pricing_data = models.JSONField()
    calculated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pricing Snapshot for Order #{self.order.id} at {self.calculated_at}"
    
    class Meta:
        verbose_name = "Order Pricing Snapshot"
        verbose_name_plural = "Order Pricing Snapshots"
        ordering = ["-calculated_at"]