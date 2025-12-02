"""
Service for managing review reminders.
"""
from django.utils import timezone
from datetime import timedelta
from orders.models import ReviewReminder, Order


class ReviewReminderService:
    """Service for managing review reminders."""
    
    @staticmethod
    def create_reminder_on_order_completion(order: Order):
        """Create a review reminder when an order is completed."""
        if not order.client or order.client.role != 'client':
            return None
        
        return ReviewReminder.create_for_order(order)
    
    @staticmethod
    def get_due_reminders():
        """Get reminders that are due to be sent."""
        return ReviewReminder.objects.filter(
            is_completed=False,
            next_reminder_at__lte=timezone.now()
        ).select_related('order', 'client', 'writer')
    
    @staticmethod
    def send_reminder(reminder: ReviewReminder):
        """Send a review reminder notification."""
        from communications.services.notification_service import NotificationService
        
        reminder.send_reminder()
        
        # Send notification
        message = f"Please review and rate your writer for order #{reminder.order.id}."
        NotificationService.send_notification(
            user=reminder.client,
            title="Review Reminder",
            message=message,
            notification_type="reminder"
        )
        
        return reminder

