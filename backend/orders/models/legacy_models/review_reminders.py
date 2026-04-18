"""
Review Reminders Model
Tracks and sends reminders for clients to review and rate their writers.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = settings.AUTH_USER_MODEL


class ReviewReminder(models.Model):
    """
    Tracks reminders for clients to review and rate their completed orders.
    """
    order = models.OneToOneField(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='review_reminder'
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_reminders',
        limit_choices_to={'role': 'client'}
    )
    writer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='writer_review_reminders',
        limit_choices_to={'role': 'writer'},
        null=True,
        blank=True
    )
    order_completed_at = models.DateTimeField(
        help_text="When the order was completed"
    )
    has_reviewed = models.BooleanField(default=False)
    has_rated = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Rating given (1-5)"
    )
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    next_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to send the next reminder"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-order_completed_at']
        indexes = [
            models.Index(fields=['client', 'has_reviewed', 'has_rated']),
            models.Index(fields=['order']),
            models.Index(fields=['next_reminder_at']),
        ]
    
    def __str__(self):
        status = "Completed" if self.has_reviewed and self.has_rated else "Pending"
        return f"Review Reminder - Order {self.order.id} - {status}"
    
    def mark_as_reviewed(self):
        """Mark that client has submitted a review."""
        self.has_reviewed = True
        if self.has_rated:
            self.complete()
        else:
            self.save(update_fields=['has_reviewed', 'updated_at'])
    
    def mark_as_rated(self, rating=None):
        """Mark that client has rated the writer."""
        self.has_rated = True
        if rating:
            self.rating = rating
        if self.has_reviewed:
            self.complete()
        else:
            self.save(update_fields=['has_rated', 'rating', 'updated_at'])
    
    def complete(self):
        """Mark reminder as completed."""
        if not self.completed_at:
            self.completed_at = timezone.now()
            self.save(update_fields=['completed_at', 'has_reviewed', 'has_rated', 'updated_at'])
    
    def send_reminder(self):
        """Record that a reminder was sent and schedule next one."""
        self.last_reminder_sent = timezone.now()
        self.reminder_count += 1
        
        # Schedule next reminder (1 day, 3 days, 7 days)
        days = [1, 3, 7][min(self.reminder_count - 1, 2)]
        self.next_reminder_at = timezone.now() + timedelta(days=days)
        
        self.save(update_fields=['last_reminder_sent', 'reminder_count', 'next_reminder_at', 'updated_at'])
    
    @property
    def is_completed(self):
        """Check if review and rating are completed."""
        return self.completed_at is not None
    
    @classmethod
    def create_for_order(cls, order):
        """Create a review reminder when order is completed."""
        if not order.client or order.client.role != 'client':
            return None
        
        reminder, created = cls.objects.get_or_create(
            order=order,
            defaults={
                'client': order.client,
                'writer': order.assigned_writer,
                'order_completed_at': timezone.now(),
                'next_reminder_at': timezone.now() + timedelta(days=1)
            }
        )
        return reminder

