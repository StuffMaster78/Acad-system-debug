"""
Writer Assignment Acknowledgment Model
Tracks when writers acknowledge order assignments and engagement reminders.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class WriterAssignmentAcknowledgment(models.Model):
    """
    Tracks writer acknowledgment of order assignments.
    """
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='writer_acknowledgments'
    )
    writer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_acknowledgments',
        limit_choices_to={'role': 'writer'}
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    has_sent_message = models.BooleanField(default=False)
    has_downloaded_files = models.BooleanField(default=False)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True, help_text="Writer's notes about the assignment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['order', 'writer']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'writer']),
            models.Index(fields=['writer', 'acknowledged_at']),
        ]
    
    def __str__(self):
        status = "Acknowledged" if self.acknowledged_at else "Pending"
        return f"Writer {self.writer.username} - Order {self.order.id} - {status}"
    
    def acknowledge(self):
        """Mark assignment as acknowledged."""
        if not self.acknowledged_at:
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['acknowledged_at', 'updated_at'])
    
    def mark_message_sent(self):
        """Mark that writer has sent a message to client."""
        if not self.has_sent_message:
            self.has_sent_message = True
            self.save(update_fields=['has_sent_message', 'updated_at'])
    
    def mark_file_downloaded(self):
        """Mark that writer has downloaded order files."""
        if not self.has_downloaded_files:
            self.has_downloaded_files = True
            self.save(update_fields=['has_downloaded_files', 'updated_at'])
    
    def send_reminder(self):
        """Record that a reminder was sent."""
        self.last_reminder_sent = timezone.now()
        self.reminder_count += 1
        self.save(update_fields=['last_reminder_sent', 'reminder_count', 'updated_at'])
    
    @property
    def is_fully_engaged(self):
        """Check if writer is fully engaged (acknowledged, messaged, downloaded files)."""
        return (
            self.acknowledged_at is not None and
            self.has_sent_message and
            self.has_downloaded_files
        )

