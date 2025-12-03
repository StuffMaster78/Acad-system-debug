"""
Signals for phone number reminders.
Sends reminders when clients interact with orders.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from users.services.phone_reminder_service import PhoneReminderService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def check_phone_reminder_on_order_update(sender, instance, created, **kwargs):
    """
    Check if phone reminder should be sent when order status changes to active states.
    Only sends reminder once per order to avoid spam.
    """
    # Only check for clients
    if not instance.client or instance.client.role not in ['client', 'customer']:
        return
    
    # Only check for active order statuses
    active_statuses = [
        'pending', 'in_progress', 'submitted', 'reviewed', 
        'rated', 'revision_requested', 'on_revision', 'revised'
    ]
    
    if instance.status not in active_statuses:
        return
    
    # Check if reminder is needed
    phone_service = PhoneReminderService(instance.client)
    if not phone_service.needs_phone_reminder():
        return
    
    # Send reminder notification (only once per order to avoid spam)
    # The notification system handles deduplication
    try:
        PhoneReminderService.send_reminder_notification(
            instance.client, 
            instance.website,
            order=instance
        )
    except Exception as e:
        logger.warning(f"Failed to send phone reminder for order {instance.id}: {e}")

