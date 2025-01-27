from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import ClientProfile
from orders.models import Order
from client_management.models import LoyaltyPoint, LoyaltyPointHistory


@receiver(post_save, sender=User)
def create_client_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'client':
        ClientProfile.objects.create(client=instance)



@receiver(post_save, sender=Order)
def add_loyalty_points(sender, instance, created, **kwargs):
    """
    Awards loyalty points to clients after order completion.
    """
    if created and instance.status == "completed" and instance.client.role == "client":
        client = instance.client
        points_earned = instance.total_cost  # Example: 1 point per $1 spent

        # Update or create loyalty points for the client
        loyalty_point, _ = LoyaltyPoint.objects.get_or_create(client=client)
        loyalty_point.points += points_earned
        loyalty_point.save()

        # Log the change
        LoyaltyPointHistory.objects.create(
            client=client,
            points_change=points_earned,
            reason=f"Points earned for order #{instance.id}",
        )