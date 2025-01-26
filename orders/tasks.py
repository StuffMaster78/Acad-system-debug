from celery import shared_task
from .models import Order

@shared_task
def notify_writer(order_id):
    order = Order.objects.get(id=order_id)
    if order.assigned_writer:
        # Send notification logic here
        return f"Notification sent to writer {order.assigned_writer.email} for Order #{order.id}"
    return f"No writer assigned for Order #{order.id}"