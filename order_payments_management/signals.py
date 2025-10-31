from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings 
from .models import (
    OrderPayment, Refund, PaymentNotification, PaymentDispute, 
    PaymentLog, FailedPayment, AdminLog
)
from orders.models import WriterRequest
from notifications_system.models.notifications import Notification
import logging
from django.db import models
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderPayment)
def update_order_status(sender, instance, created, **kwargs):
    """
    Updates the order status when a payment is completed.
    Sends a notification to the client and logs payment events.
    """
    if instance.status == "completed":
        process_successful_payment(instance)

    elif instance.status == "failed":
        handle_failed_payment(instance)


def process_successful_payment(instance):
    """Handles order status update, logging, and notification for successful payments."""
    if instance.order:
        instance.order.mark_paid()
    elif hasattr(instance, 'special_order') and instance.special_order:
        instance.special_order.update_payment_status()
    else:
        logger.error(f"Payment {instance.transaction_id} completed, but no order reference found.")

    # Notify client
    Notification.create_notification(
        user=instance.client,
        message=f"Your payment of ${instance.discounted_amount} was successful!"
    )

    # Log successful payment
    PaymentLog.log_event(
        payment=instance,
        event="Payment Completed",
        details=f"Payment {instance.transaction_id} completed for ${instance.discounted_amount}."
    )


def handle_failed_payment(instance):
    """Handles logging, retry tracking, and notifications for failed payments."""
    failed_payment, created = FailedPayment.objects.get_or_create(
        payment=instance,
        client=instance.client,
        defaults={"failure_reason": "Payment failed"}
    )
    if not created:
        failed_payment.retry_count += 1
        failed_payment.save()

     # A Safeguard: Ensure client exists before notifying
    if instance.client:
        # Notify client only on first failure
        if created or failed_payment.retry_count == 1:
            Notification.create_notification(
                user=instance.client,
                message="Your payment attempt failed. Please try again."
            )

    # Notify client only on first failure
    if created or failed_payment.retry_count == 1:
        Notification.create_notification(
            user=instance.client,
            message="Your payment attempt failed. Please try again."
        )

    # If too many failures in 24 hours, alert admin
    if failed_payment.retry_count >= 3:
        last_failure = failed_payment.updated_at
        if last_failure and now() - last_failure < timedelta(hours=24):
            Notification.create_notification(
                user=instance.client,
                message="Multiple failed payments detected. Contact support."
            )
            AdminLog.log_action(
                admin=None,
                action="Repeated Payment Failure",
                details=f"Client {instance.client.username} failed payment {instance.transaction_id} "
                        f"{failed_payment.retry_count} times."
            )

    # Log failure
    PaymentLog.log_event(
        payment=instance,
        event="Payment Failed",
        details=f"Payment {instance.transaction_id} failed."
    )


@receiver(post_save, sender=Refund)
def process_refund_action(sender, instance, created, **kwargs):
    """
    Updates the OrderPayment status when a refund is processed.
    Ensures the transaction data is consistent.
    """
    if instance.status == "processed" and getattr(instance, "processed_at", None):
        if instance.payment:
            instance.payment.status = "refunded"
            instance.payment.save()

            # Log refund event
            PaymentLog.log_event(
                payment=instance.payment,
                event="Refund Processed",
                details=f"Refund of ${instance.amount} issued to {instance.client.username}."
            )

            # Log refund action for admin tracking
            AdminLog.log_action(
                admin=instance.processed_by,
                action="Refund Issued",
                details=f"Refund of ${instance.amount} processed for client {instance.client.username}."
            )


@receiver(post_save, sender=PaymentDispute)
def log_dispute_action(sender, instance, created, **kwargs):
    """
    Logs when a client files a dispute and when it is resolved.
    """
    if created:
        # Log dispute creation
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Filed",
            details=f"Dispute filed by {instance.client.username} for {instance.payment.id}."
        )
    elif instance.status == "resolved":
        # Log dispute resolution
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Resolved",
            details=f"Dispute resolved for payment {instance.payment.id}."
        )

        # Notify the client
        Notification.create_notification(
            user=instance.client,
            message="Your payment dispute has been resolved."
        )

    elif instance.status == "rejected":
        # Log dispute rejection
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Rejected",
            details=f"Dispute rejected for payment {instance.payment.id}."
        )

        # Notify the client
        Notification.create_notification(
            user=instance.client,
            message="Your payment dispute was rejected."
        )


@receiver(pre_save, sender=OrderPayment)
def validate_duplicate_payment(sender, instance, **kwargs):
    if instance.status == "completed":
        query = models.Q()
        if instance.order:
            query |= models.Q(order=instance.order)
        if hasattr(instance, 'special_order') and instance.special_order:
            query |= models.Q(special_order=instance.special_order)

        existing_payment = OrderPayment.objects.filter(query, status="completed").exclude(id=instance.id).exists()

        if existing_payment:
            raise ValidationError("This order has already been paid for.")
        


# Signal to automatically calculate the total cost when a request is approved.
@receiver(post_save, sender=WriterRequest)
def on_writer_request_approval(sender, instance, created, **kwargs):
    if instance.client_approval and instance.admin_approval:
        instance.order.calculate_total_cost()