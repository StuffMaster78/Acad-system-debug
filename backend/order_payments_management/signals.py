from datetime import timedelta
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.timezone import now

from notifications_system.services.notification_service import (
    NotificationService,
)
from order_payments_management.models.logs import AdminLog, PaymentLog
from order_payments_management.models.payment_dispute import PaymentDispute
from order_payments_management.models.payment_refund import Refund
from order_payments_management.models.payments import (
    FailedPayment,
    OrderPayment,
)
from orders.models.requests import WriterRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=OrderPayment)
def update_order_status(sender, instance, created, **kwargs):
    """
    Update order status when a payment is completed.
    Send notifications and log payment events.
    """
    if instance.status == "completed":
        process_successful_payment(instance)
    elif instance.status == "failed":
        handle_failed_payment(instance)


def process_successful_payment(instance):
    """Handle status update, logging, and notification."""
    if instance.order:
        instance.order.mark_paid()
    elif hasattr(instance, "special_order") and instance.special_order:
        instance.special_order.update_payment_status()
    else:
        logger.error(
            "Payment %s completed, but no order reference found.",
            instance.transaction_id,
        )

    try:
        if instance.order and instance.order.client:
            NotificationService.notify(
                event_key="payment.completed",
                recipient=instance.order.client,
                website=instance.website,
                context={
                    "order_id": instance.order.id,
                    "payment_id": instance.id,
                    "amount": instance.discounted_amount,
                    "website_id": instance.website_id,
                },
                channels=["email", "in_app"],
                triggered_by=instance.client,
                priority="high",
                is_broadcast=False,
                is_critical=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
    except Exception as exc:
        logger.error(
            "Failed to send payment notification: %s",
            exc,
        )

    PaymentLog.log_event(
        payment=instance,
        event="Payment Completed",
        details=(
            f"Payment {instance.transaction_id} completed for "
            f"${instance.discounted_amount}."
        ),
    )


def handle_failed_payment(instance):
    """Handle logging, retry tracking, and notifications."""
    failed_payment, created = FailedPayment.objects.get_or_create(
        payment=instance,
        client=instance.client,
        defaults={"failure_reason": "Payment failed"},
    )

    if not created:
        failed_payment.retry_count += 1
        failed_payment.save()

    if instance.client and instance.order and (
        created or failed_payment.retry_count == 1
    ):
        try:
            NotificationService.notify(
                event_key="payment.failed",
                recipient=instance.order.client,
                website=instance.website,
                context={
                    "order_id": instance.order.id,
                    "payment_id": instance.id,
                    "order": (
                        instance.order.id if instance.order else None
                    ),
                    "amount": instance.discounted_amount,
                    "reason": failed_payment.failure_reason,
                    "website_id": instance.website_id,
                },
                channels=["email", "in_app"],
                triggered_by=instance.client,
                priority="high",
                is_broadcast=False,
                is_critical=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )
        except Exception as exc:
            logger.error(
                "Failed to send payment failed notification: %s",
                exc,
            )

    if failed_payment.retry_count >= 3:
        last_failure = failed_payment.updated_at
        if last_failure and now() - last_failure < timedelta(hours=24):
            try:
                if instance.order and instance.client:
                    NotificationService.notify(
                        event_key="payment.multiple_failures",
                        recipient=instance.client,
                        website=instance.website,
                        context={
                            "order_id": instance.order.id,
                            "failure_count": failed_payment.retry_count,
                            "website_id": instance.website_id,
                        },
                        channels=["email", "in_app"],
                        triggered_by=instance.client,
                        priority="high",
                        is_broadcast=False,
                        is_critical=True,
                        is_digest=False,
                        is_silent=False,
                        digest_group=None,
                    )
            except Exception as exc:
                logger.error(
                    "Failed to send multiple failures notification: %s",
                    exc,
                )

            AdminLog.log_action(
                admin=None,
                action="Repeated Payment Failure",
                details=(
                    f"Client {instance.client.username} failed payment "
                    f"{instance.transaction_id} "
                    f"{failed_payment.retry_count} times."
                ),
            )

    PaymentLog.log_event(
        payment=instance,
        event="Payment Failed",
        details=f"Payment {instance.transaction_id} failed.",
    )


@receiver(post_save, sender=Refund)
def process_refund_action(sender, instance, created, **kwargs):
    """
    Update OrderPayment status when a refund is processed.
    Ensure transaction data is consistent.
    """
    if instance.status == "processed" and getattr(
        instance, "processed_at", None
    ):
        if instance.payment:
            instance.payment.status = "refunded"
            instance.payment.save()

            PaymentLog.log_event(
                payment=instance.payment,
                event="Refund Processed",
                details=(
                    f"Refund of ${instance.amount} issued to "
                    f"{instance.client.username}."
                ),
            )

            AdminLog.log_action(
                admin=instance.processed_by,
                action="Refund Issued",
                details=(
                    f"Refund of ${instance.amount} processed for client "
                    f"{instance.client.username}."
                ),
            )


@receiver(post_save, sender=PaymentDispute)
def log_dispute_action(sender, instance, created, **kwargs):
    """
    Log when a client files a dispute and when it is resolved.
    """
    if created:
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Filed",
            details=(
                f"Dispute filed by {instance.client.username} for "
                f"{instance.payment.id}."
            ),
        )

    elif instance.status == "resolved":
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Resolved",
            details=(
                f"Dispute resolved for payment {instance.payment.id}."
            ),
        )

        try:
            if instance.payment and instance.payment.order:
                NotificationService.notify(
                    event_key="payment.dispute.resolved",
                    recipient=instance.client,
                    website=instance.payment.website,
                    context={
                        "dispute_id": instance.id,
                        "payment_id": instance.payment.id,
                        "order_id": instance.payment.order.id,
                        "website_id": instance.payment.website_id,
                    },
                    channels=["email", "in_app"],
                    triggered_by=instance.client,
                    priority="high",
                    is_broadcast=False,
                    is_critical=False,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
                )
        except Exception as exc:
            logger.error(
                "Failed to send dispute resolved notification: %s",
                exc,
            )

    elif instance.status == "rejected":
        PaymentLog.log_event(
            payment=instance.payment,
            event="Dispute Rejected",
            details=(
                f"Dispute rejected for payment {instance.payment.id}."
            ),
        )

        try:
            if instance.payment and instance.payment.order:
                NotificationService.notify(
                    event_key="payment.dispute.rejected",
                    recipient=instance.client,
                    website=instance.payment.website,
                    context={
                        "dispute_id": instance.id,
                        "payment_id": instance.payment.id,
                        "order_id": instance.payment.order.id,
                        "website_id": instance.payment.website_id,
                    },
                    channels=["email", "in_app"],
                    triggered_by=instance.client,
                    priority="high",
                    is_broadcast=False,
                    is_critical=False,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
                )
        except Exception as exc:
            logger.error(
                "Failed to send dispute rejected notification: %s",
                exc,
            )


@receiver(pre_save, sender=OrderPayment)
def validate_duplicate_payment(sender, instance, **kwargs):
    """Prevent multiple completed payments for the same order."""
    if instance.status == "completed":
        query = models.Q()

        if instance.order:
            query |= models.Q(order=instance.order)

        if hasattr(instance, "special_order") and instance.special_order:
            query |= models.Q(special_order=instance.special_order)

        existing_payment = (
            OrderPayment.objects.filter(query, status="completed")
            .exclude(id=instance.id)
            .exists()
        )

        if existing_payment:
            raise ValidationError(
                "This order has already been paid for."
            )


@receiver(post_save, sender=WriterRequest)
def on_writer_request_approval(sender, instance, created, **kwargs):
    """Automatically calculate total cost when a request is approved."""
    if instance.client_approval and instance.admin_approval:
        instance.order.calculate_total_cost()