from django.db import models
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile
from orders.models import Order


class Tip(models.Model):
    """
    Represents a tip sent by a client to a writer.
    Can be for an order, a class/task, or directly to the writer.
    """
    TIP_TYPE_CHOICES = [
        ('direct', 'Direct Tip'),
        ('order', 'Order-Based Tip'),
        ('class', 'Class/Task-Based Tip'),
    ]
    
    client = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="tips_sent"
    )
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name="tips_received"
    )
    website = models.ForeignKey(
        "websites.Website",
        on_delete=models.CASCADE,
        help_text="Multitenancy support: this tip is for a specific website.",
    )
    
    # Tip type and related entities
    tip_type = models.CharField(
        max_length=20,
        choices=TIP_TYPE_CHOICES,
        default='direct',
        help_text="Type of tip: direct, order-based, or class/task-based"
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tips",
        help_text="Order this tip is for (if order-based)"
    )
    related_entity_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Type of related entity (e.g., 'class_bundle', 'express_class')"
    )
    related_entity_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of related entity (class bundle, express class, etc.)"
    )
    
    # Tip amount and split
    tip_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Full tip amount paid by client"
    )
    tip_reason = models.TextField(blank=True, help_text="Reason for the tip")
    sent_at = models.DateTimeField(auto_now_add=True)
    
    # Writer level and split calculation
    writer_level = models.ForeignKey(
        'writer_management.WriterLevel',
        on_delete=models.SET_NULL,
        null=True,
        related_name="tips",
        help_text="Writer level at time of tip (for percentage calculation)"
    )
    writer_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Percentage of tip that goes to writer (based on their level)"
    )
    writer_earning = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount writer receives (their share only)"
    )
    platform_profit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount platform retains (not visible to writer)"
    )
    
    # Payment tracking
    payment = models.ForeignKey(
        'order_payments_management.OrderPayment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tips",
        help_text="Payment record for this tip"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
        help_text="Payment status for this tip"
    )
    
    origin = models.CharField(
        max_length=50,
        default='client',
        help_text="Origin of tip (e.g., 'client', 'admin', 'system')"
    )
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['client', 'website']),
            models.Index(fields=['writer', 'website']),
            models.Index(fields=['tip_type', 'related_entity_type', 'related_entity_id']),
        ]
    
    def __str__(self):
        entity_info = ""
        if self.tip_type == 'order' and self.order:
            entity_info = f" for Order #{self.order.id}"
        elif self.tip_type == 'class' and self.related_entity_type:
            entity_info = f" for {self.related_entity_type} #{self.related_entity_id}"
        return f"Tip ${self.tip_amount} from {self.client.username} to {self.writer.username}{entity_info}"