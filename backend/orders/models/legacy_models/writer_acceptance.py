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
from orders.models.orders import Order

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



class WriterAssignmentAcceptance(models.Model):
    """
    Tracks writer acceptance or rejection of order assignments.
    When an admin assigns a writer, the order moves to 'pending_writer_assignment' status.
    The writer must accept or reject the assignment.
    """
    ACCEPTANCE_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_assignment_acceptances'
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='assignment_acceptance',
        help_text="The order that was assigned"
    )
    writer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_acceptances',
        limit_choices_to={'role': 'writer'},
        help_text="The writer who was assigned"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assignments_made',
        help_text="Admin/support who assigned the order"
    )
    status = models.CharField(
        max_length=20,
        choices=ACCEPTANCE_STATUS_CHOICES,
        default='pending',
        help_text="Whether the writer has accepted or rejected the assignment"
    )
    reason = models.TextField(
        blank=True,
        null=True,
        help_text="Writer's reason for accepting or rejecting (optional)"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the assignment was made"
    )
    responded_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the writer accepted or rejected"
    )
    
    class Meta:
        verbose_name = "Writer Assignment Acceptance"
        verbose_name_plural = "Writer Assignment Acceptances"
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['writer', 'status']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['status', 'assigned_at']),
        ]
    
    def __str__(self):
        return f"Assignment #{self.id} - Order #{self.order.id} - {self.get_status_display()}"
    
    def accept(self, reason=None):
        """Mark assignment as accepted and move order to in_progress."""
        if self.status != 'pending':
            raise ValidationError(f"Cannot accept assignment that is already {self.status}")
        
        self.status = 'accepted'
        self.reason = reason
        self.responded_at = timezone.now()
        self.save()
        
        # Use unified transition helper to move to in_progress
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            self.order,
            OrderStatus.IN_PROGRESS.value,
            user=self.writer,
            reason=reason or "Writer accepted assignment",
            action="accept_assignment",
            is_automatic=False,
            skip_payment_check=True,  # Payment already validated
            metadata={
                "assignment_acceptance_id": self.id,
                "writer_id": self.writer.id,
                "assigned_by_id": self.assigned_by.id if self.assigned_by else None,
            }
        )
        
        # Send notification
        from notifications_system.services.notification_service import NotificationService
    
        NotificationService.notify(
            event_key="order.assignment_accepted",
            recipient=self.assigned_by,
            website=self.website,
            context={
                "order_id": self.order.id,
                "order_title": self.order.title,
                "writer_username": self.writer.username,
            },
            channels={"in_app": True, "email": True},
            triggered_by=self.writer,
            priority="high",
            is_broadcast=False,
            is_digest=False,
            is_silent=False,
            digest_group=None,
        )
    
    def reject(self, reason=None):
        """Mark assignment as rejected and return order to available."""
        if self.status != 'pending':
            raise ValidationError(f"Cannot reject assignment that is already {self.status}")
        
        self.status = 'rejected'
        self.reason = reason
        self.responded_at = timezone.now()
        self.save()
        
        # Unassign writer
        self.order.assigned_writer = None
        self.order.save(update_fields=['assigned_writer'])
        
        # Use unified transition helper to move to available
        from orders.services.transition_helper import OrderTransitionHelper
        OrderTransitionHelper.transition_order(
            self.order,
            OrderStatus.AVAILABLE.value,
            user=self.writer,
            reason=reason or "Writer rejected assignment",
            action="reject_assignment",
            is_automatic=False,
            metadata={
                "assignment_acceptance_id": self.id,
                "writer_id": self.writer.id,
                "assigned_by_id": self.assigned_by.id if self.assigned_by else None,
                "rejection_reason": reason,
            }
        )
        
        # Send notification
        from notifications_system.services.notification_service import NotificationService
        NotificationService.notify(
            event_key="order.assignment_rejected",
            recipient=self.assigned_by,
            website=self.website,
            context={
                "order_id": self.order.id,
                "order_title": self.order.title,
                "writer_username": self.writer.username,
                "rejection_reason": reason,
            },
            channels= ["email", "in_app"],
            triggered_by=self.writer,
            priority="high",
            is_broadcast=False,
            is_digest=False,
            is_silent=False,
            digest_group=None,
        )

