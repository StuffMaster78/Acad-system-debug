from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def handle_order_save(sender, instance, created, **kwargs):
    """
    Signal to handle actions after an order is created or updated.
    """
    if created:
        # Handle logic for a newly created order
        print(f"New order created: {instance.topic} by {instance.client}")
    else:
        # Handle logic for an updated order
        print(f"Order updated: {instance.topic} (Status: {instance.status})")