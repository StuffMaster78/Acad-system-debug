import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models.orders import Order
from .models.legacy_models.requests import OrderRequest, WriterRequest
from .models.legacy_models.order_disputes import Dispute
from notifications_system.services.notification_service import NotificationService

log = logging.getLogger(__name__)


@receiver(pre_save, sender=Order)
def update_order_status(sender, instance, **kwargs):
    if instance.is_paid and instance.status == 'unpaid':
        instance.status = 'pending'


@receiver(post_save, sender=Order)
def handle_order_completion(sender, instance, created, update_fields, **kwargs):
    """
    When an order transitions to COMPLETED, enqueue a Celery task to
    create the writer's CompensationEvent. Skipped when update_fields is
    provided and does not include 'status' (avoids unnecessary dispatches
    on unrelated saves). Idempotency in the task prevents duplicate events.
    """
    if created:
        return
    if update_fields is not None and "status" not in update_fields:
        return
    if instance.status != "completed":
        return
    from writer_compensation.tasks.order_compensation_tasks import (
        create_order_compensation_event,
    )
    create_order_compensation_event.delay(order_id=instance.pk)

@receiver(post_save, sender=Dispute)
def handle_dispute_creation(sender, instance, created, **kwargs):
    """
    When a dispute is created, flag the order.
    """
    if created:
        order = instance.order
        order.flag = True # Mark the order as disputed
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

    subject = "Your order request has been accepted!"
    dashboard_url = f"https://{domain}/orders/{order.id}/"
    accept_url = f"https://{domain}/orders/{order.id}/accept/"

    message = (
        f"Congrats {writer.get_full_name()}!\n\n"
        f"Your request to work on Order #{order.id} has been accepted.\n"
        f"You can now begin working on it.\n\n"
        f"Order Details:\n"
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

    NotificationService.notify(
        event_key="writer_request_accepted",
        recipient=writer,
        website=website,
        context={
            "order": order,
            "writer": writer,
            "dashboard_url": dashboard_url,
            "accept_url": accept_url
        },
        channels=["email", "in_app"],
        triggered_by=None,
        is_broadcast=False,
        priority="high",
        is_digest=False,
        is_critical=True,
        is_silent=False,
        digest_group=None
    )