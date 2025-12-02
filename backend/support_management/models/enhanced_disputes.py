"""
Enhanced Dispute & Escalation Models
In-app dispute flows with clear states and escalation tracking.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
# Use string references to avoid circular imports


class OrderDispute(models.Model):
    """
    Enhanced dispute model with clear states and escalation tracking.
    """
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='order_disputes'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='enhanced_disputes'
    )
    
    # Dispute details
    title = models.CharField(
        max_length=255,
        help_text="Brief title/summary of the dispute"
    )
    description = models.TextField(
        help_text="Detailed description of the dispute"
    )
    
    # Parties
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enhanced_disputes_raised',
        help_text="User who raised the dispute (client or writer)"
    )
    other_party = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='disputes_against',
        help_text="The other party in the dispute"
    )
    
    # Status and priority
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_assigned',
        limit_choices_to={'role__in': ['support', 'admin', 'superadmin']}
    )
    
    # Resolution
    resolution_notes = models.TextField(
        blank=True,
        help_text="Resolution notes from support/admin"
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_resolved',
        limit_choices_to={'role__in': ['support', 'admin', 'superadmin']}
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True
    )
    resolution_outcome = models.CharField(
        max_length=50,
        blank=True,
        help_text="Outcome: 'client_wins', 'writer_wins', 'partial_refund', etc."
    )
    
    # Escalation
    escalated_at = models.DateTimeField(
        null=True,
        blank=True
    )
    escalated_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='disputes_escalated_to',
        limit_choices_to={'role__in': ['admin', 'superadmin']}
    )
    escalation_reason = models.TextField(
        blank=True,
        help_text="Reason for escalation"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['raised_by', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['status', 'priority']),
        ]
        verbose_name = "Order Dispute"
        verbose_name_plural = "Order Disputes"
    
    def __str__(self):
        return f"Dispute #{self.id} - Order #{self.order.id} - {self.status}"
    
    def escalate(self, escalated_to, reason=''):
        """Escalate dispute to admin/superadmin."""
        self.status = 'escalated'
        self.escalated_at = timezone.now()
        self.escalated_to = escalated_to
        self.escalation_reason = reason
        self.save(update_fields=['status', 'escalated_at', 'escalated_to', 'escalation_reason', 'updated_at'])
    
    def resolve(self, resolved_by, resolution_notes, outcome):
        """Resolve dispute."""
        self.status = 'resolved'
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        self.resolution_notes = resolution_notes
        self.resolution_outcome = outcome
        self.save(update_fields=['status', 'resolved_at', 'resolved_by', 'resolution_notes', 'resolution_outcome', 'updated_at'])
    
    def close(self):
        """Close dispute (final state)."""
        self.status = 'closed'
        self.save(update_fields=['status', 'updated_at'])


class DisputeMessage(models.Model):
    """
    Messages within a dispute thread.
    """
    dispute = models.ForeignKey(
        OrderDispute,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dispute_messages_sent'
    )
    message = models.TextField()
    is_internal = models.BooleanField(
        default=False,
        help_text="Internal note (not visible to other party)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Message in Dispute #{self.dispute.id} from {self.sender.email}"

