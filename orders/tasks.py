from core.celery import shared_task
from core.utils.notifications import send_notification
from django.utils.timezone import now
from orders.models import Order
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
import logging
from django.utils import timezone
from orders.models import Order
from datetime import timedelta

from orders.services.archive_order_service import ArchiveOrderService
from orders.services.status_transition_service import StatusTransitionService

logger = logging.getLogger(__name__)

@shared_task
def notify_writer(order_id):
    """
    Task to notify the assigned writer about an order.
    Sends an in-app notification and an email.
    """
    try:
        order = get_object_or_404(Order.objects.select_related('writer', 'client'), id=order_id)

        if not order.writer:
            logger.warning(f"No writer assigned for Order #{order.id}")
            return f"No writer assigned for Order #{order.id}"

        # In-app notification
        send_notification(
            user=order.writer,
            title="New Order Assigned",
            message=f"You have been assigned to Order #{order.id}: {order.topic}. Please check your dashboard."
        )

        # Email notification
        if order.writer.email:
            send_mail(
                subject="New Order Assignment",
                message=f"Dear {order.writer.username},\n\n"
                        f"You have been assigned a new order.\n\n"
                        f"Order ID: {order.id}\n"
                        f"Topic: {order.topic}\n\n"
                        f"Please log in to your dashboard to view the details.",
                from_email="no-reply@example.com",
                recipient_list=[order.writer.email],
                fail_silently=True
            )

        logger.info(f"Notification sent to writer {order.writer.email} for Order #{order.id}")
        return f"Notification sent to writer {order.writer.email} for Order #{order.id}"

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        return f"Order with ID {order_id} does not exist."

    except Exception as e:
        logger.error(f"Error in notify_writer task: {e}", exc_info=True)
        return f"Error in notify_writer task: {e}"
    


# Email notification to the client
@shared_task
def send_order_completion_email(client_email, client_username, order_id):
    """
    Sends an email to the client when their order is marked as completed.
    """
    try:
        subject = "Your Order is Completed!"
        message = f"Dear {client_username},\n\nYour order #{order_id} has been marked as completed."
        send_mail(
            subject, message, "no-reply@yourdomain.com", [client_email], fail_silently=True
        )
        logger.info(f"Order completion email sent to {client_email} for Order #{order_id}")
        return f"Order completion email sent to {client_email} for Order #{order_id}"

    except Exception as e:
        logger.error(f"Error sending order completion email: {e}", exc_info=True)
        return f"Error sending order completion email: {e}"
    

@shared_task
def release_stale_preferred_orders():
    """
    This task checks for orders that have been in the 'pending_preferred' status 
    for too long and moves them back to the public pool (status = 'available').

    This ensures that orders with no response from the preferred writer are 
    re-opened to the pool after a specified time.
    """
    stale_time = timedelta(hours=24)  # Orders older than 24 hours will be released

    # Find orders that are still in 'pending_preferred' and are stale
    stale_orders = Order.objects.filter(
        status='pending_preferred',
        created_at__lte=timezone.now() - stale_time
    )

    for order in stale_orders:
        order.status = 'available'  # Move to public pool
        order.preferred_writer = None  # Remove the preferred writer
        order.save()

        # Notify the client that their preferred writer did not respond
        if order.client.email:
            send_mail(
                subject="Preferred Writer Did Not Respond",
                message=f"Dear {order.client.username},\n\n"
                        f"Your preferred writer did not respond to the order request for Order #{order.id}."
                        f"The order is now available for other writers to take.\n\n"
                        f"Best regards,\nYour Team",
                from_email="no-reply@example.com",
                recipient_list=[order.client.email],
                fail_silently=True
            )

        logger.info(f"Released Order #{order.id} back to the public pool after {stale_time} hours.")
        
    print(f"Released {stale_orders.count()} stale preferred orders.")



@shared_task
def archive_approved_orders_task():
    """
    Archive orders that are in 'approved' state older than 2 weeks.
    """
    cutoff_date = now() - timedelta(weeks=2)
    ArchiveOrderService.archive_approved_orders_older_than(cutoff_date)


@shared_task
def move_complete_to_approved_task():
    """
    Move orders from 'complete' to 'approved' if they are older than 3 weeks.
    """
    cutoff_date = now() - timedelta(weeks=3)
    StatusTransitionService.move_complete_orders_to_approved_older_than(cutoff_date)