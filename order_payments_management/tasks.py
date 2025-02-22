from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta
import logging
from django.core.mail import send_mail
from django.conf import settings
from .models import OrderPayment, FailedPayment, PaymentReminderSettings, PaymentLog
from notifications_system.models import Notification
from .models import AdminLog  # Ensure admin logs are properly tracked

logger = logging.getLogger(__name__)


@shared_task
def expire_unpaid_orders():
    """
    Cancels orders that remain unpaid for more than 24 hours.
    """
    time_threshold = now() - timedelta(hours=24)
    unpaid_orders = OrderPayment.objects.filter(
        status="pending", date_processed__lt=time_threshold
    )

    # Bulk update unpaid orders instead of looping
    updated_count = unpaid_orders.update(status="failed")

    if updated_count > 0:
        logger.info(f"Expired {updated_count} unpaid orders.")

        # Notify affected clients
        for payment in unpaid_orders:
            Notification.create_notification(
                user=payment.client,
                message=f"Your order {payment.order.id if payment.order else 'Special Order'} "
                        f"has been canceled due to non-payment."
            )

            # Log expiration
            PaymentLog.log_event(
                payment=payment,
                event="Order Expired",
                details=f"Order {payment.order.id if payment.order else 'Special Order'} "
                        f"marked as failed due to non-payment."
            )


@shared_task
def retry_failed_payments():
    """
    Retries failed payments up to 3 times before marking them as permanently failed.
    """
    failed_payments = FailedPayment.objects.filter(retry_count__lt=3)

    for failed_payment in failed_payments:
        try:
            if failed_payment.payment.status != "failed":
                continue  # Skip already processed payments

            # Prevent duplicate retries for the same payment
            existing_retry = OrderPayment.objects.filter(
                transaction_id__startswith=f"retry-{failed_payment.payment.transaction_id}"
            ).exists()
            if existing_retry:
                logger.warning(f"Skipping duplicate retry for {failed_payment.payment.transaction_id}")
                continue

            # Create a new retry transaction
            new_transaction_id = f"retry-{failed_payment.payment.transaction_id}-{failed_payment.retry_count + 1}"
            new_payment = OrderPayment.objects.create(
                client=failed_payment.client,
                order=failed_payment.payment.order,
                special_order=failed_payment.payment.special_order,
                original_amount=failed_payment.payment.original_amount,
                discounted_amount=failed_payment.payment.discounted_amount,
                status="pending",
                payment_method=failed_payment.payment.payment_method,
                transaction_id=new_transaction_id,
            )

            # Attempt to verify payment
            new_payment.verify_payment()

            if new_payment.status == "completed":
                logger.info(f"Retry successful for transaction {new_transaction_id}")
                failed_payment.delete()  # Remove failed entry if successful
                continue

        except Exception as e:
            logger.error(f"Retry failed for {failed_payment.id}: {e}")
            failed_payment.retry_count += 1
            failed_payment.save()

            if failed_payment.retry_count >= 3:
                Notification.create_notification(
                    user=failed_payment.client,
                    message=f"Your payment attempt for order {failed_payment.payment.order.id if failed_payment.payment.order else 'Special Order'} "
                            f"has failed after 3 retries. Please contact support."
                )

                PaymentLog.log_event(
                    payment=failed_payment.payment,
                    event="Payment Failed (Max Retries)",
                    details=f"Payment {failed_payment.payment.transaction_id} failed after 3 retries."
                )


@shared_task
def send_payment_reminders():
    """
    Sends email and in-app reminders for pending payments before expiration.
    Uses admin-configurable intervals and messages.
    """
    # Fetch admin settings, or create defaults if none exist
    settings_obj, _ = PaymentReminderSettings.objects.get_or_create()

    now_time = now()

    # Calculate reminder times
    reminder_time_1 = now_time - timedelta(hours=(24 - settings_obj.first_reminder_hours))
    reminder_time_2 = now_time - timedelta(hours=(24 - settings_obj.final_reminder_hours))

    # Fetch payments eligible for reminders
    pending_payments = OrderPayment.objects.filter(
        status="pending", date_processed__lt=reminder_time_1
    ) | OrderPayment.objects.filter(
        status="pending", date_processed__lt=reminder_time_2
    )

    for payment in pending_payments:
        client = payment.client
        hours_left = settings_obj.final_reminder_hours if payment.date_processed < reminder_time_2 else settings_obj.first_reminder_hours
        message_body = settings_obj.final_reminder_message if payment.date_processed < reminder_time_2 else settings_obj.first_reminder_message

        subject = "⚠️ Payment Reminder - Your Order is About to Expire!"
        message = (
            f"Dear {client.username},\n\n{message_body}\n\n"
            f"Your order {payment.order.id if payment.order else 'Special Order'} "
            f"will be canceled in {hours_left} hours if payment is not completed.\n\n"
            f"Click here to complete your payment now: {settings.SITE_URL}/payments/{payment.id}\n\n"
            f"If you have any questions, please contact support."
        )

        # Send email reminder
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[client.email],
        )

        # Send in-app notification
        Notification.create_notification(
            user=client,
            message=f"Reminder: Your payment for order {payment.order.id if payment.order else 'Special Order'} "
                    f"will expire in {hours_left} hours."
        )

        logger.info(f"Payment reminder sent to {client.email} for payment {payment.id}")