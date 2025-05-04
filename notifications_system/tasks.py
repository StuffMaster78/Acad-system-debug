from core.celery import shared_task
from .models import Notification
from core.celery import shared_task
from core.utils.notifications import send_notification
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.utils import timezone
from notifications_system.utils import send_website_mail
from orders.models import Order
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_writer(order_id):
    """
    Notify the assigned writer of a new order using tenant-aware email.
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

        # Tenant-aware email notification
        website = getattr(order, "website", None)  # Ensure website is passed if available
        if order.writer.email:
            send_website_mail(
                subject="New Order Assignment",
                message=(
                    f"Dear {order.writer.username},\n\n"
                    f"You have been assigned a new order.\n\n"
                    f"Order ID: {order.id}\n"
                    f"Topic: {order.topic}\n\n"
                    f"Please log in to your dashboard to view the details."
                ),
                recipient_list=[order.writer.email],
                website=website
            )

        logger.info(f"Notification sent to writer {order.writer.email} for Order #{order.id}")
        return f"Notification sent to writer {order.writer.email} for Order #{order.id}"

    except Order.DoesNotExist:
        logger.error(f"Order with ID {order_id} does not exist.")
        return f"Order with ID {order_id} does not exist."

    except Exception as e:
        logger.error(f"Error in notify_writer task: {e}", exc_info=True)
        return f"Error in notify_writer task: {e}"


@shared_task
def send_order_completion_email(
    client_email,
    client_username,
    order_id,
    website_id=None
):
    """
    Sends an email to the client when their order is marked as completed,
    using tenant-aware sender address.
    """
    try:
        from websites.models import Website  # Adjust to your actual website model location

        website = None
        if website_id:
            website = Website.objects.filter(id=website_id).first()

        subject = "Your Order is Completed!"
        message = (
            f"Dear {client_username},\n\n"
            f"Your order #{order_id} has been marked as completed.\n\n"
            f"Please log in to your dashboard to download and review it.\n\n"
            f"Thank you for choosing us!"
        )

        success = send_website_mail(
            subject=subject,
            message=message,
            recipient_list=[client_email],
            website=website
        )

        if success:
            logger.info(f"Order completion email sent to {client_email} for Order #{order_id}")
        else:
            logger.warning(f"Email sending failed for Order #{order_id} to {client_email}")

        return f"Order completion email sent to {client_email} for Order #{order_id}" if success else "Failed to send email"

    except Exception as e:
        logger.error(f"Error sending order completion email: {e}", exc_info=True)
        return f"Error sending order completion email: {e}"
    
@shared_task
def notify_writer_missed_deadline(order_id):
    """
    Alerts a writer they’ve missed the deadline for a specific order.
    """
    try:
        order = Order.objects.select_related('writer', 'website').get(id=order_id)

        if not order.writer:
            logger.warning(f"No writer for missed deadline on Order #{order.id}")
            return

        send_notification(
            user=order.writer,
            title="Deadline Missed",
            message=f"You’ve missed the deadline for Order #{order.id}. Please contact support immediately."
        )

        send_website_mail(
            subject="Deadline Missed Notification",
            message=f"Dear {order.writer.username},\n\n"
                    f"You missed the deadline for Order #{order.id}. Please resolve this with the admin.",
            recipient_list=[order.writer.email],
            website=order.website
        )
        logger.info(f"Missed deadline notice sent for Order #{order.id}")
    except Exception as e:
        logger.error(f"Error sending missed deadline email: {e}", exc_info=True)


@shared_task
def notify_writer_fined(order_id, fine_amount):
    """
    Notifies a writer that a fine has been applied to their order.
    """
    try:
        order = Order.objects.select_related('writer', 'website').get(id=order_id)
        writer = order.writer

        if not writer:
            return

        send_notification(
            user=writer,
            title="Fine Applied",
            message=f"A fine of ${fine_amount:.2f} has been applied to your work on Order #{order.id}."
        )

        send_website_mail(
            subject="Fine Notice",
            message=f"Dear {writer.username},\n\n"
                    f"A fine of ${fine_amount:.2f} has been applied to your account for Order #{order.id} due to policy violation.\n"
                    f"Please check your dashboard for more details.",
            recipient_list=[writer.email],
            website=order.website
        )
    except Exception as e:
        logger.error(f"Error notifying writer of fine: {e}", exc_info=True)



@shared_task
def notify_client_writer_declined(order_id):
    """
    Tells the client that the preferred writer has declined the order.
    """
    try:
        order = Order.objects.select_related('client', 'preferred_writer', 'website').get(id=order_id)

        if not order.client:
            return

        send_notification(
            user=order.client,
            title="Writer Declined",
            message=f"Your preferred writer declined Order #{order.id}. It’s now open to other writers."
        )

        send_website_mail(
            subject="Preferred Writer Declined",
            message=f"Dear {order.client.username},\n\n"
                    f"Unfortunately, your preferred writer declined Order #{order.id}. "
                    f"The order is now visible to all eligible writers.",
            recipient_list=[order.client.email],
            website=order.website
        )
    except Exception as e:
        logger.error(f"Error notifying client about writer decline: {e}", exc_info=True)



@shared_task
def send_scheduled_notification(notification_id):
    """
    Task to send scheduled notifications.
    """
    notification = Notification.objects.get(id=notification_id)
    notification.send()