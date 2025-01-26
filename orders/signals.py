from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def handle_order_save(sender, instance, created, **kwargs):
    if created:
        print(f"New order created: {instance.title} by {instance.client}")
    else:
        print(f"Order updated: {instance.title}")