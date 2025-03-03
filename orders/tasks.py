from celery import shared_task
from core.utils.notifications import send_notification
from django.utils.timezone import now
from orders.models import Order
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)

@shared_task
def notify_writer(order_id):
    """
    Task to notify the assigned writer about an order.
    Sends an in-app notification and an email.
    """
    try:
        order = Order.objects.select_related('writer', 'client').get(id=order_id)

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
                message=f"Dear {order.writer.username},\n\nYou have been assigned a new order.\n\n"
                        f"Order ID: {order.id}\nTopic: {order.topic}\n\n"
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
        logger.error(f"Error in notify_writer task: {e}")
        return f"Error in notify_writer task: {e}"
    


# Email notification to the client
@shared_task
def send_order_completion_email(client_email, client_username, order_id):
    subject = "Your Order is Completed!"
    message = f"Dear {client_username},\n\nYour order #{order_id} has been marked as completed."
    send_mail(subject, message, "no-reply@yourdomain.com", [client_email], fail_silently=True)
