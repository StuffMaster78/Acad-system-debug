from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Order, Dispute, WriterRequest

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