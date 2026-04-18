"""
Message Reminders Model
Tracks unread messages and reminds users to respond.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

User = settings.AUTH_USER_MODEL


class MessageReminder(models.Model):
    """
    Tracks message reminders for users who haven't read or responded to messages.
    """
    REMINDER_TYPE_CHOICES = [
        ('unread', 'Unread Message'),
        ('unresponded', 'Unresponded Message'),
        ('urgent', 'Urgent Response Needed'),
    ]
    
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='message_reminders'
    )
    message = models.ForeignKey(
        'communications.CommunicationMessage',
        on_delete=models.CASCADE,
        related_name='reminders',
        null=True,
        blank=True,
        help_text="Specific message that needs attention"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='message_reminders',
        help_text="User who needs to be reminded"
    )
    reminder_type = models.CharField(
        max_length=20,
        choices=REMINDER_TYPE_CHOICES,
        default='unread'
    )
    is_read = models.BooleanField(default=False)
    is_responded = models.BooleanField(default=False)
    last_reminder_sent = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    next_reminder_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When to send the next reminder"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['order', 'user', 'message']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'is_responded']),
            models.Index(fields=['order', 'reminder_type']),
            models.Index(fields=['next_reminder_at']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.user.username} - Order {self.order.id} - {self.get_reminder_type_display()}"
    
    def mark_as_read(self):
        """Mark message as read and resolve reminder if responded."""
        self.is_read = True
        if self.is_responded:
            self.resolve()
        else:
            self.save(update_fields=['is_read', 'updated_at'])
    
    def mark_as_responded(self):
        """Mark message as responded and resolve reminder."""
        self.is_responded = True
        self.resolve()
    
    def resolve(self):
        """Resolve the reminder."""
        if not self.resolved_at:
            self.resolved_at = timezone.now()
            self.save(update_fields=['resolved_at', 'is_read', 'is_responded', 'updated_at'])
    
    def send_reminder(self):
        """Record that a reminder was sent and schedule next one."""
        self.last_reminder_sent = timezone.now()
        self.reminder_count += 1
        
        # Schedule next reminder (exponential backoff: 1h, 4h, 12h, 24h)
        hours = min(24, 4 ** min(self.reminder_count - 1, 3))
        self.next_reminder_at = timezone.now() + timedelta(hours=hours)
        
        self.save(update_fields=['last_reminder_sent', 'reminder_count', 'next_reminder_at', 'updated_at'])
    
    @property
    def is_resolved(self):
        """Check if reminder is resolved."""
        return self.resolved_at is not None
    
    @classmethod
    def create_or_update(cls, order, user, message=None, reminder_type='unread'):
        """Create or update a message reminder."""
        reminder, created = cls.objects.get_or_create(
            order=order,
            user=user,
            message=message,
            defaults={
                'reminder_type': reminder_type,
                'next_reminder_at': timezone.now() + timedelta(hours=1)
            }
        )
        if not created:
            # Update existing reminder
            reminder.reminder_type = reminder_type
            reminder.next_reminder_at = timezone.now() + timedelta(hours=1)
            reminder.save(update_fields=['reminder_type', 'next_reminder_at', 'updated_at'])
        return reminder

