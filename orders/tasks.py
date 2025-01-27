from celery import shared_task
from .models import Order
from core.utils import send_notification

@shared_task
def notify_writer(order_id):
    """
    Task to notify the assigned writer about an order.
    """
    try:
        order = Order.objects.select_related('writer').get(id=order_id)
        if order.writer:
            # Replace with actual notification logic (e.g., email, SMS, or real-time notification)
            send_notification(
                user=order.writer,
                title="New Order Assigned",
                message=f"You have been assigned to Order #{order.id}: {order.topic}. Please check your dashboard."
            )
            return f"Notification sent to writer {order.writer.email} for Order #{order.id}"
        return f"No writer assigned for Order #{order.id}"
    except Order.DoesNotExist:
        return f"Order with ID {order_id} does not exist."