"""
SLA Timers & Priorities for Tickets
Visible countdowns and priority-based SLA tracking.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
# Use string reference to avoid circular import
# Use string reference to avoid circular import
# Ticket will be resolved by Django


class TicketSLA(models.Model):
    """
    SLA tracking for tickets with visible countdowns.
    """
    PRIORITY_SLA_HOURS = {
        'critical': 1,   # 1 hour
        'high': 4,       # 4 hours
        'medium': 24,    # 24 hours
        'low': 72,       # 72 hours
    }
    
    ticket = models.OneToOneField(
        'tickets.Ticket',
        on_delete=models.CASCADE,
        related_name='sla_tracking'
    )
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='ticket_slas'
    )
    
    # SLA timers
    created_at = models.DateTimeField(auto_now_add=True)
    first_response_deadline = models.DateTimeField(
        help_text="Deadline for first response"
    )
    resolution_deadline = models.DateTimeField(
        help_text="Deadline for resolution"
    )
    
    # Actual times
    first_response_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When first response was sent"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When ticket was resolved"
    )
    
    # Status
    first_response_breached = models.BooleanField(
        default=False,
        help_text="Whether first response SLA was breached"
    )
    resolution_breached = models.BooleanField(
        default=False,
        help_text="Whether resolution SLA was breached"
    )
    
    # Priority (synced from ticket)
    # Use same choices as Ticket model
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        help_text="Priority level (affects SLA)"
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['ticket', 'resolution_deadline']),
            models.Index(fields=['website', 'resolution_breached']),
        ]
        verbose_name = "Ticket SLA"
        verbose_name_plural = "Ticket SLAs"
    
    def __str__(self):
        return f"SLA for Ticket #{self.ticket.id} - {self.priority}"
    
    @classmethod
    def create_for_ticket(cls, ticket):
        """Create SLA tracking for a ticket based on priority."""
        hours = cls.PRIORITY_SLA_HOURS.get(ticket.priority, 24)
        
        now = timezone.now()
        first_response_deadline = now + timezone.timedelta(hours=hours // 2)
        resolution_deadline = now + timezone.timedelta(hours=hours)
        
        return cls.objects.create(
            ticket=ticket,
            website=ticket.website,
            priority=ticket.priority,
            first_response_deadline=first_response_deadline,
            resolution_deadline=resolution_deadline
        )
    
    def get_time_remaining(self):
        """Get time remaining until resolution deadline."""
        if self.resolved_at:
            return None
        
        remaining = self.resolution_deadline - timezone.now()
        return {
            'total_seconds': int(remaining.total_seconds()),
            'hours': int(remaining.total_seconds() / 3600),
            'minutes': int((remaining.total_seconds() % 3600) / 60),
            'is_overdue': remaining.total_seconds() < 0,
            'is_urgent': 0 < remaining.total_seconds() < 3600,  # Less than 1 hour
        }
    
    def get_first_response_time_remaining(self):
        """Get time remaining until first response deadline."""
        if self.first_response_at:
            return None
        
        remaining = self.first_response_deadline - timezone.now()
        return {
            'total_seconds': int(remaining.total_seconds()),
            'hours': int(remaining.total_seconds() / 3600),
            'minutes': int((remaining.total_seconds() % 3600) / 60),
            'is_overdue': remaining.total_seconds() < 0,
        }
    
    def check_and_update_breaches(self):
        """Check and update SLA breach status."""
        now = timezone.now()
        
        # Check first response
        if not self.first_response_at and now > self.first_response_deadline:
            self.first_response_breached = True
        
        # Check resolution
        if not self.resolved_at and now > self.resolution_deadline:
            self.resolution_breached = True
        
        self.save(update_fields=['first_response_breached', 'resolution_breached'])
    
    def mark_first_response(self):
        """Mark first response sent."""
        if not self.first_response_at:
            self.first_response_at = timezone.now()
            self.first_response_breached = timezone.now() > self.first_response_deadline
            self.save(update_fields=['first_response_at', 'first_response_breached'])
    
    def mark_resolved(self):
        """Mark ticket as resolved."""
        if not self.resolved_at:
            self.resolved_at = timezone.now()
            self.resolution_breached = timezone.now() > self.resolution_deadline
            self.save(update_fields=['resolved_at', 'resolution_breached'])

