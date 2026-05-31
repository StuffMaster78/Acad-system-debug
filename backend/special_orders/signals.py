from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.utils.email_helpers import send_website_mail

from communications.constants import CommunicationThreadKind
from communications.models import CommunicationThread
from special_orders.constants import FundingMilestoneStatus
from special_orders.models import SpecialOrder, SpecialOrderFundingMilestone

User = get_user_model()


def notify_users(subject, message, recipients, website=None):
    """
    Send an email notification using the tenant's configured sender address.
    """
    try:
        send_website_mail(subject, message, recipients, website=website)
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

    content_type = ContentType.objects.get_for_model(SpecialOrder)
    CommunicationThread.objects.get_or_create(
        website=instance.website,
        kind=CommunicationThreadKind.ADMIN_CLIENT,
        target_content_type=content_type,
        target_object_id=instance.pk,
        defaults={
            "subject": f"Special Order #{instance.pk}: {instance.title}",
            "reference": f"special:{instance.pk}",
            "metadata": {
                "thread_type": "special_order",
                "sender_role": "client",
                "recipient_role": "admin",
            },
        },
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


@receiver(post_save, sender=SpecialOrderFundingMilestone)
def handle_funding_milestone_payment(sender, instance, created, **kwargs):
    """
    Notify admin and client when a funding milestone is paid.
    """
    if not (
        created
        and instance.status == FundingMilestoneStatus.PAID
    ):
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
