from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .models import SpecialOrder, InstallmentPayment
from communications.models import OrderMessageThread

User = get_user_model()


def notify_users(subject, message, recipients):
    """
    Send an email notification to a list of recipients.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email='no-reply@yourdomain.com',
            recipient_list=recipients,
            fail_silently=True
        )
    except Exception as e:
        print(f"Email send error: {e}")


@receiver(post_save, sender=SpecialOrder)
def handle_new_special_order(sender, instance, created, **kwargs):
    """
    Notify admins and create message thread for new special orders.
    """
    if not created:
        return

    admin_emails = list(
        User.objects.filter(is_staff=True)
        .values_list('email', flat=True)
    )

    if admin_emails:
        notify_users(
            subject=f"New Special Order #{instance.id} Created",
            message=(
                f"A new special order has been placed by "
                f"{instance.client.username}."
            ),
            recipients=admin_emails
        )

    OrderMessageThread.objects.create(
        order_type='special',
        special_order=instance,
        sender_role='client',
        recipient_role='admin'
    )


@receiver(post_save, sender=SpecialOrder)
def handle_status_change(sender, instance, created, **kwargs):
    """
    Notify the client when their order status changes.
    """
    if created:
        return

    subject = f"Order #{instance.id} Status Update"
    message = f"Your order status is now '{instance.status}'."
    notify_users(subject, message, [instance.client.email])


@receiver(post_save, sender=SpecialOrder)
def handle_order_completion(sender, instance, created, **kwargs):
    """
    Notify client and writer when a special order is completed.
    """
    if created or instance.status != 'completed':
        return

    subject = f"Order #{instance.id} Completed"
    message = "Your special order has been completed."

    notify_users(subject, message, [instance.client.email])

    if instance.writer and instance.writer.email:
        notify_users(
            subject=subject,
            message="The order you worked on is now marked as completed.",
            recipients=[instance.writer.email]
        )


@receiver(post_save, sender=SpecialOrder)
def handle_admin_payment_override(sender, instance, created, **kwargs):
    """
    Notify client when admin manually confirms payment.
    """
    if created or not instance.admin_marked_paid:
        return

    subject = f"Payment Confirmation for Order #{instance.id}"
    message = "Admin has confirmed your payment manually."
    notify_users(subject, message, [instance.client.email])


@receiver(post_save, sender=InstallmentPayment)
def handle_installment_payment(sender, instance, created, **kwargs):
    """
    Notify admin and client when an installment payment is recorded.
    """
    if not (created and instance.is_paid):
        return

    subject = f"Payment Received for Order #{instance.special_order.id}"
    message = (
        f"An installment of ${instance.amount_due} has been received."
    )

    notify_users(subject, message, [instance.special_order.client.email])

    admin_emails = list(
        User.objects.filter(is_staff=True)
        .values_list('email', flat=True)
    )

    if admin_emails:
        notify_users(subject, message, admin_emails)