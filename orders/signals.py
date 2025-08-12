from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, Dispute, WriterRequest, OrderRequest
from notifications_system.services.dispatch import NotificationDispatcher
from django.core.mail import send_mail

@receiver(post_save, sender=Order)
def handle_order_save(sender, instance, created, **kwargs):
    """
    Signal to handle actions after an order is created or updated.
    """
    if created:
        print(f"New order created: {instance.topic} by {instance.client}")
        # Example: Notify admin or writer about the new order
    else:
        print(f"Order updated: {instance.topic} (Status: {instance.status})")
        # Example: Notify client when order status changes

@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    """
    Automatically update the order's status based on payment.
    """
    if instance.is_paid and instance.status == 'unpaid':
        instance.status = 'pending'  # Auto-update status when payment is received

@receiver(post_save, sender=Dispute)
def handle_dispute_creation(sender, instance, created, **kwargs):
    """
    When a dispute is created, flag the order.
    """
    if created:
        order = instance.order
        order.flag = True  # Mark the order as disputed
        order.save()
        print(f"Dispute created for order: {order.topic}")
        # Example: Notify admin for dispute resolution


@receiver(post_save, sender=WriterRequest)
def on_writer_request_approved(sender, instance, created, **kwargs):
    if instance.admin_approval and instance.client_approval:
        # Automatically update total cost after approval
        instance.order.calculate_total_cost()

@receiver(post_save, sender=Dispute)
def on_dispute_resolved(sender, instance, created, **kwargs):
    if instance.status == 'resolved':
        # Handle dispute resolution, such as notifying users or updating order status
        pass



@receiver(post_save, sender=OrderRequest)
def notify_writer_on_acceptance(sender, instance, created, **kwargs):
    """
    Notify the writer when their request has been accepted.
    """
    if created or not instance.accepted or not instance.accepted_at:
        return

    website = instance.website
    domain = website.domain.rstrip("/")
    order = instance.order
    writer = instance.writer

    subject = "🎉 Your order request has been accepted!"
    dashboard_url = f"https://{domain}/orders/{order.id}/"
    accept_url = f"https://{domain}/orders/{order.id}/accept/"

    message = (
        f"🎉 Congrats {writer.get_full_name()}!\n\n"
        f"Your request to work on Order #{order.id} has been accepted.\n"
        f"You can now begin working on it.\n\n"
        f"🔎 Order Details:\n"
        f"• Topic: {order.topic}\n"
        f"• Client: {order.client.username}\n"
        f"• Due Date: {order.due_date.strftime('%Y-%m-%d %H:%M')}\n"
        f"• View Order: {dashboard_url}\n"
        f"• Accept Assignment: {accept_url}\n\n"
        f"Please ensure you follow all order requirements and timelines.\n"
        f"Reach out if you need any clarification.\n\n"
        f"Thank you for your dedication.\n"
        f"- {domain} Team"
    )

    # System dashboard notification
    try:
        NotificationDispatcher.dispatch(
            user=writer,
            message="🎯 Your request to work on an order was accepted! "
                    f"Click to accept the assignment: {accept_url}",
            metadata={
                "order_id": order.id,
                "website_id": website.id,
                "expires_at": instance.expires_at.isoformat(),
            },
        )
    except Exception:
        pass  # Silently fail

    # Email notification
    try:
        send_mail(
            subject,
            message,
            f"no-reply@{domain}",
            [writer.email],
            fail_silently=True,
        )
    except Exception:
        pass