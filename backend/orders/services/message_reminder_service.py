"""
Service for managing message reminders.
"""
from django.utils import timezone
from datetime import timedelta
from orders.models import MessageReminder, Order


class MessageReminderService:
    """Service for managing message reminders."""
    
    @staticmethod
    def create_reminder_for_unread_message(order: Order, user, message=None):
        """Create a reminder for an unread message."""
        return MessageReminder.create_or_update(
            order=order,
            user=user,
            message=message,
            reminder_type='unread'
        )
    
    @staticmethod
    def create_reminder_for_unresponded_message(order: Order, user, message=None):
        """Create a reminder for an unresponded message."""
        return MessageReminder.create_or_update(
            order=order,
            user=user,
            message=message,
            reminder_type='unresponded'
        )
    
    @staticmethod
    def get_due_reminders():
        """Get reminders that are due to be sent."""
        return MessageReminder.objects.filter(
            is_resolved=False,
            next_reminder_at__lte=timezone.now()
        ).select_related('order', 'user', 'message')
    
    @staticmethod
    def send_reminder(reminder: MessageReminder):
        """Send a reminder notification."""
        from communications.services.notification_service import NotificationService
        
        reminder.send_reminder()
        
        # Send notification
        reminder_text = {
            'unread': 'You have an unread message',
            'unresponded': 'You have a message waiting for your response',
            'urgent': 'Urgent: Please respond to this message'
        }.get(reminder.reminder_type, 'You have a message')
        
        message = f"{reminder_text} for order #{reminder.order.id}."
        NotificationService.send_notification(
            user=reminder.user,
            title="Message Reminder",
            message=message,
            notification_type="reminder"
        )
        
        return reminder

