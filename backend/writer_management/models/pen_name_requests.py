"""
Models for writer pen name change requests.
Writers cannot delete pen names, only request changes with valid reasons.
"""
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from websites.models import Website
from writer_management.models.profile import WriterProfile

User = settings.AUTH_USER_MODEL


class WriterPenNameChangeRequest(models.Model):
    """
    Writers can request to change their pen name with a valid reason.
    Admin/Superadmin approval required.
    Once a pen name is set, it cannot be deleted, only changed.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="pen_name_change_requests"
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="pen_name_change_requests"
    )
    current_pen_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Current pen name (if any)"
    )
    requested_pen_name = models.CharField(
        max_length=100,
        help_text="New pen name requested by the writer"
    )
    reason = models.TextField(
        help_text="Valid reason for changing the pen name (required)"
    )
    requested_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pen_name_reviews",
        limit_choices_to={'role__in': ['admin', 'superadmin']}
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Admin notes on the request"
    )
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', 'requested_at']),
            models.Index(fields=['writer', 'status']),
        ]
    
    def __str__(self):
        return f"Pen Name Change: {self.writer.user.username} ({self.status})"
    
    def save(self, *args, **kwargs):
        # Auto-set website from writer if not provided
        if not getattr(self, 'website_id', None):
            if getattr(self, 'writer', None) and getattr(self.writer, 'website_id', None):
                self.website_id = self.writer.website_id
        
        # Set current pen name from writer profile if not set
        if not self.current_pen_name and getattr(self, 'writer', None):
            self.current_pen_name = self.writer.pen_name or ''
        
        super().save(*args, **kwargs)
    
    def approve(self, reviewer, notes=None):
        """Approve the pen name change request."""
        if self.status != 'pending':
            raise ValueError("Only pending requests can be approved")
        
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = now()
        if notes:
            self.admin_notes = notes
        
        # Update writer's pen name
        self.writer.pen_name = self.requested_pen_name
        self.writer.save(update_fields=['pen_name'])
        
        self.save()
    
    def reject(self, reviewer, notes=None):
        """Reject the pen name change request."""
        if self.status != 'pending':
            raise ValueError("Only pending requests can be rejected")
        
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.reviewed_at = now()
        if notes:
            self.admin_notes = notes
        
        self.save()

