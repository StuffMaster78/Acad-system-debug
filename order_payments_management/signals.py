from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now
from django.conf import settings  # ✅ Import settings
from .models import (
    OrderPayment, Refund, PaymentNotification, PaymentDispute, 
    PaymentLog, FailedPayment, AdminLog
)
from notifications_system.models import Notification
import logging
from django.db import models

logger = logging.getLogger(__name__)

@receiver(post_save, sender=OrderPayment)
def update_order_status(sender, instance, created, **kwargs):
    """
    Updates the order status when a payment is completed.
    Sends a notification to the client and logs payment events.
    """
    if instance.status == "completed":
        if instance.order:
            instance.order.mark_paid()
        elif instance.special_order:
            instance.special_order.update_payment_status()

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

    elif instance.status == "failed":
        # Log and track failed payments
        failed_payment, created = FailedPayment.objects.get_or_create(
            payment=instance,
            client=instance.client,
            defaults={"failure_reason": "Payment failed"}
        )
        if not created:
            failed_payment.retry_count += 1
            failed_payment.save()

        # If too many failures, notify admin
        if failed_payment.retry_count >= 3:
            Notification.create_notification(
                user=instance.client,
                message="Your payment attempt failed multiple times. Contact support."
            )
            AdminLog.log_action(
                admin=None,
                action="Repeated Payment Failure",
                details=f"Client {instance.client.username} failed payment {instance.transaction_id} "
                        f"{failed_payment.retry_count} times."
            )

        # Notify client
        Notification.create_notification(
            user=instance.client,
            message="Your payment attempt failed. Please try again."
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
    if created and instance.status == "processed":
        # Mark the original payment as refunded
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
    """
    Prevents duplicate payments for the same order or special order.
    """
    if instance.status == "completed":
        existing_payment = OrderPayment.objects.filter(
            (models.Q(order=instance.order) | models.Q(special_order=instance.special_order)),
            status="completed"
        ).exclude(id=instance.id).exists()

        if existing_payment:
            raise ValueError("This order has already been paid for.")