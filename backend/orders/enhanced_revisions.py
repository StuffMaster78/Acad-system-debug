"""
Enhanced Revision Request Model
Structured revision requests with severity, deadline, and specific change requests.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from websites.models import Website


class RevisionRequest(models.Model):
    """
    Enhanced revision request with structured fields.
    Replaces simple revision_request text field with comprehensive request.
    """
    SEVERITY_CHOICES = [
        ('minor', 'Minor'),
        ('moderate', 'Moderate'),
        ('major', 'Major'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='revision_requests'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='revision_requests'
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='revision_requests_made',
        limit_choices_to={'role': 'client'}
    )
    
    # Structured request fields
    title = models.CharField(
        max_length=255,
        help_text="Brief title/summary of the revision request"
    )
    description = models.TextField(
        help_text="Detailed description of what needs to be changed"
    )
    
    # What to change (structured)
    changes_required = models.JSONField(
        default=list,
        help_text="List of specific changes: [{'section': 'Introduction', 'issue': '...', 'request': '...'}]"
    )
    
    # Severity and priority
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='moderate',
        help_text="Severity of the revision"
    )
    priority = models.PositiveIntegerField(
        default=5,
        help_text="Priority level (1-10, higher = more urgent)"
    )
    
    # Timeline
    requested_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Client's requested deadline for the revision"
    )
    agreed_deadline = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Agreed deadline (may differ from requested)"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the revision was completed"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revision_requests_assigned',
        limit_choices_to={'role__in': ['writer', 'editor']}
    )
    
    # Communication
    client_notes = models.TextField(
        blank=True,
        help_text="Additional notes from client"
    )
    writer_notes = models.TextField(
        blank=True,
        help_text="Notes from writer during revision"
    )
    
    # Metadata
    is_urgent = models.BooleanField(
        default=False,
        help_text="Marked as urgent by client"
    )
    requires_client_review = models.BooleanField(
        default=True,
        help_text="Whether client needs to review after completion"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['severity', 'status']),
        ]
        verbose_name = "Revision Request"
        verbose_name_plural = "Revision Requests"
    
    def __str__(self):
        return f"Revision #{self.id} - Order #{self.order.id} - {self.severity}"
    
    def can_complete(self):
        """Check if revision can be marked as completed."""
        return self.status in ['pending', 'in_progress']
    
    def complete(self, completed_by=None):
        """Mark revision as completed."""
        if not self.can_complete():
            return False
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        if completed_by:
            self.assigned_to = completed_by
        self.save(update_fields=['status', 'completed_at', 'assigned_to', 'updated_at'])
        
        # Update order status if needed
        if self.order.status == 'revision_requested':
            self.order.status = 'revision_in_progress'
            self.order.save(update_fields=['status'])
        
        return True
    
    def get_timeline(self):
        """Get timeline information for display."""
        timeline = {
            'requested': self.created_at,
            'requested_deadline': self.requested_deadline,
            'agreed_deadline': self.agreed_deadline,
            'completed': self.completed_at,
        }
        
        if self.agreed_deadline:
            timeline['days_remaining'] = (self.agreed_deadline - timezone.now()).days
            timeline['is_overdue'] = timezone.now() > self.agreed_deadline and self.status != 'completed'
        
        return timeline

