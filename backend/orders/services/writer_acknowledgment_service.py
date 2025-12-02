"""
Service for managing writer assignment acknowledgments and reminders.
"""
from django.utils import timezone
from django.db import models
from datetime import timedelta
from orders.models import WriterAssignmentAcknowledgment, Order


class WriterAcknowledgmentService:
    """Service for managing writer acknowledgments and engagement reminders."""
    
    @staticmethod
    def create_acknowledgment_on_assignment(order: Order, writer):
        """Create an acknowledgment record when a writer is assigned to an order."""
        if not writer or writer.role != 'writer':
            return None
        
        acknowledgment, created = WriterAssignmentAcknowledgment.objects.get_or_create(
            order=order,
            writer=writer
        )
        
        return acknowledgment
    
    @staticmethod
    def get_pending_acknowledgments(hours_threshold=24):
        """Get acknowledgments that haven't been acknowledged within threshold."""
        threshold_time = timezone.now() - timedelta(hours=hours_threshold)
        
        return WriterAssignmentAcknowledgment.objects.filter(
            acknowledged_at__isnull=True,
            created_at__lt=threshold_time
        ).select_related('order', 'writer')
    
    @staticmethod
    def get_engagement_reminders():
        """Get acknowledgments that need engagement reminders."""
        # Writers who acknowledged but haven't sent message or downloaded files
        # and it's been more than 12 hours since acknowledgment
        threshold_time = timezone.now() - timedelta(hours=12)
        
        return WriterAssignmentAcknowledgment.objects.filter(
            acknowledged_at__isnull=False,
            acknowledged_at__lt=threshold_time,
        ).filter(
            # Not fully engaged
            models.Q(has_sent_message=False) | models.Q(has_downloaded_files=False)
        ).exclude(
            # Don't remind if last reminder was less than 24 hours ago
            last_reminder_sent__gt=timezone.now() - timedelta(hours=24)
        ).select_related('order', 'writer')
    
    @staticmethod
    def send_engagement_reminder(acknowledgment: WriterAssignmentAcknowledgment):
        """Send an engagement reminder to a writer."""
        from communications.services.notification_service import NotificationService
        
        acknowledgment.send_reminder()
        
        # Send notification
        message_parts = []
        if not acknowledgment.has_sent_message:
            message_parts.append("send a message to the client")
        if not acknowledgment.has_downloaded_files:
            message_parts.append("download the order files")
        
        if message_parts:
            message = f"Please remember to {', and '.join(message_parts)} for order #{acknowledgment.order.id}."
            NotificationService.send_notification(
                user=acknowledgment.writer,
                title="Order Engagement Reminder",
                message=message,
                notification_type="reminder"
            )
        
        return acknowledgment

