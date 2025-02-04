from celery import shared_task
from core.utils.notifications import send_notification
from django.utils import timezone
# from datetime import timedelta
from orders.models import FailedPayment, Order
from django.core.mail import send_mail


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
    



@shared_task
def retry_failed_payment(failed_payment_id):
    failed_payment = FailedPayment.objects.get(id=failed_payment_id)

    # Ensure the retry count doesn't exceed 3 attempts
    if failed_payment.retry_count < 3:
        # Simulate retry logic (you could integrate with a payment gateway here)
        success = process_payment(failed_payment.order)

        if success:
            # Mark the payment as successful
            failed_payment.retry_count = 3  # Mark as resolved
            failed_payment.save()
            return "Payment successfully retried"
        
        else:
            # Increment the retry count and set the last retry time
            failed_payment.retry_count += 1
            failed_payment.last_retry_at = timezone.now()
            failed_payment.save()
            return f"Retry attempt {failed_payment.retry_count} failed"

    else:
        # Send notification if max retries reached
        failed_payment.send_failure_notification()
        return "Max retry attempts reached, notified client"
        
def process_payment(order):
    """
    Simulate payment processing. Integrate with a real payment gateway here.
    Return True if payment is successful, False otherwise.
    """
    # Replace with actual payment gateway code
    return False  # Simulating a failed payment