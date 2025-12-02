"""
Celery tasks for sending reminders for writer acknowledgments, messages, and reviews.
"""
from celery import shared_task
from django.utils import timezone
import logging

from orders.services.writer_acknowledgment_service import WriterAcknowledgmentService
from orders.services.message_reminder_service import MessageReminderService
from orders.services.review_reminder_service import ReviewReminderService

logger = logging.getLogger(__name__)


@shared_task
def send_writer_engagement_reminders():
    """
    Send reminders to writers who haven't acknowledged assignments or engaged with orders.
    Runs daily to check for pending acknowledgments and engagement.
    """
    try:
        # Get pending acknowledgments (not acknowledged within 24 hours)
        pending = WriterAcknowledgmentService.get_pending_acknowledgments(hours_threshold=24)
        count = 0
        
        for acknowledgment in pending:
            try:
                WriterAcknowledgmentService.send_engagement_reminder(acknowledgment)
                count += 1
            except Exception as e:
                logger.error(f"Error sending reminder for acknowledgment {acknowledgment.id}: {e}")
        
        # Get acknowledgments that need engagement reminders
        engagement_reminders = WriterAcknowledgmentService.get_engagement_reminders()
        
        for acknowledgment in engagement_reminders:
            try:
                WriterAcknowledgmentService.send_engagement_reminder(acknowledgment)
                count += 1
            except Exception as e:
                logger.error(f"Error sending engagement reminder for acknowledgment {acknowledgment.id}: {e}")
        
        logger.info(f"Sent {count} writer engagement reminders")
        return f"Sent {count} writer engagement reminders"
    except Exception as e:
        logger.error(f"Error in send_writer_engagement_reminders: {e}")
        raise


@shared_task
def send_message_reminders():
    """
    Send reminders for unread or unresponded messages.
    Runs hourly to check for due message reminders.
    """
    try:
        due_reminders = MessageReminderService.get_due_reminders()
        count = 0
        
        for reminder in due_reminders:
            try:
                MessageReminderService.send_reminder(reminder)
                count += 1
            except Exception as e:
                logger.error(f"Error sending message reminder {reminder.id}: {e}")
        
        logger.info(f"Sent {count} message reminders")
        return f"Sent {count} message reminders"
    except Exception as e:
        logger.error(f"Error in send_message_reminders: {e}")
        raise


@shared_task
def send_review_reminders():
    """
    Send reminders to clients to review and rate their writers.
    Runs daily to check for due review reminders.
    """
    try:
        due_reminders = ReviewReminderService.get_due_reminders()
        count = 0
        
        for reminder in due_reminders:
            try:
                ReviewReminderService.send_reminder(reminder)
                count += 1
            except Exception as e:
                logger.error(f"Error sending review reminder {reminder.id}: {e}")
        
        logger.info(f"Sent {count} review reminders")
        return f"Sent {count} review reminders"
    except Exception as e:
        logger.error(f"Error in send_review_reminders: {e}")
        raise


@shared_task
def create_review_reminders_for_completed_orders():
    """
    Create review reminders when orders are completed.
    This should be called from order completion signals or actions.
    """
    from orders.models import Order
    from orders.order_enums import OrderStatus
    
    try:
        # Get orders that were completed in the last hour and don't have review reminders
        one_hour_ago = timezone.now() - timezone.timedelta(hours=1)
        
        completed_orders = Order.objects.filter(
            status=OrderStatus.COMPLETED.value,
            updated_at__gte=one_hour_ago
        ).exclude(
            review_reminder__isnull=False
        ).select_related('client', 'assigned_writer')
        
        count = 0
        for order in completed_orders:
            try:
                reminder = ReviewReminderService.create_reminder_on_order_completion(order)
                if reminder:
                    count += 1
            except Exception as e:
                logger.error(f"Error creating review reminder for order {order.id}: {e}")
        
        logger.info(f"Created {count} review reminders for completed orders")
        return f"Created {count} review reminders"
    except Exception as e:
        logger.error(f"Error in create_review_reminders_for_completed_orders: {e}")
        raise

